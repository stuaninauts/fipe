"""The aggregates behind every published number. Nothing else defines a finding (CLAUDE.md).

All tables use January references only and come with `n`, so a reader can always see how many prices a number
rests on. Inputs are the clean price table from fipe/clean.py (with `price_real_brl` from fipe/inflation.py).

Two ways of following value (docs/adr/0006):
- the same car over time: cohort (bought brand new in January Y, valued in later Januaries) and the
  year-to-year change of the same used car. These are the headline methods;
- the same January: a used car next to today's brand-new price of the same code (retention_by_age,
  new_vs_used). Kept as secondary ("compared with a brand-new car today").
"""

from __future__ import annotations

import math

import pandas as pd

from fipe.clean import CAR
from fipe.family import family

JANUARY = 1
RECENT_YEARS = 5  # "recent" scope in retention_by_age: the last five January references
PRICE_BANDS = ["q1", "q2", "q3", "q4", "q5"]  # quintiles within each January, cheapest first
EXPLORE_MIN_BRAND_N = 1000  # a brand enters the explore cubes with at least this many retention pairs
EXPLORE_MAX_AGE = 10  # past this age the same-January curve rests on a few long-lived models (survivorship)
SHOCK_YEAR = 2022  # the one January with a real gain; left out of the "normal" loss by age
# Premium and luxury brands: 27% of the catalogue, a small share of sales. The mass-market sensitivity
# leaves them out (docs/adr/0006).
PREMIUM_BRANDS = frozenset(
    {
        "Acura",
        "Alfa Romeo",
        "ASTON MARTIN",
        "Audi",
        "BMW",
        "Cadillac",
        "Ferrari",
        "Jaguar",
        "LAMBORGHINI",
        "Land Rover",
        "Lexus",
        "Lotus",
        "Maserati",
        "Mclaren",
        "Mercedes-Benz",
        "MINI",
        "Porsche",
        "Rolls-Royce",
        "smart",
        "Volvo",
    }
)
MASS_AGES = (1, 15)  # mass-market sensitivity: cars aged 1 to 15 in the second January
HOLDS_VALUE_AGE = 5  # what holds value: compared five years after purchase
HOLDS_VALUE_MIN_N = 100  # a brand needs this many cars bought new and valued five years later
DIESEL_LABEL_FROM = 2011  # before 2011 many diesel cars were labelled "Gasolina" (see fuel_relabels)
VERSION_MIN_CODES = 3  # a family needs at least this many versions bought new in the same year
VERSION_MIN_SPREAD = 1.15  # and the top version must cost at least 15% more than the entry one


def _january_used(prices: pd.DataFrame) -> pd.DataFrame:
    return prices[(prices["ref_month"] == JANUARY) & ~prices["is_new"]]


def _quantiles(s: pd.Series) -> dict[str, float]:
    return {"median": s.median(), "p25": s.quantile(0.25), "p75": s.quantile(0.75)}


def _quintiles(values: pd.Series, by: pd.Series) -> pd.Series:
    """Quintile label of each value within its group (q1 = cheapest fifth)."""
    pct = values.groupby(by).rank(method="first", pct=True)  # (0, 1]
    band = (pct * len(PRICE_BANDS)).apply(math.ceil).clip(1, len(PRICE_BANDS))
    return band.map(lambda i: PRICE_BANDS[int(i) - 1])


def _yearly_pairs(prices: pd.DataFrame) -> pd.DataFrame:
    """Every used car present in two consecutive Januaries, with its nominal and real change.

    `price_band` is the quintile of the car's real price among the used cars of the first January.
    """
    used = _january_used(prices)
    frames = []
    years = sorted(used["ref_year"].unique())
    for prev, cur in zip(years, years[1:], strict=False):
        if cur != prev + 1:
            continue
        a = used[used["ref_year"] == prev].set_index(CAR)
        b = used[used["ref_year"] == cur].set_index(CAR)
        pairs = a.join(b, how="inner", lsuffix="_a", rsuffix="_b").reset_index()
        frames.append(
            pd.DataFrame(
                {
                    "from_year": int(prev),
                    "to_year": int(cur),
                    "age": int(cur) - pairs["model_year"].astype(int),
                    "brand": pairs["brand_b"],
                    "fuel_group": pairs["fuel_group"],
                    "real_a": pairs["price_real_brl_a"],
                    "nominal": pairs["price_brl_b"] / pairs["price_brl_a"] - 1,
                    "real": pairs["price_real_brl_b"] / pairs["price_real_brl_a"] - 1,
                }
            )
        )
    out = pd.concat(frames, ignore_index=True)
    out["price_band"] = _quintiles(out["real_a"], out["from_year"])
    return out


def _retention_pairs(prices: pd.DataFrame, max_age: int) -> pd.DataFrame:
    """Each used model year next to the brand-new price of the same code and fuel group, same January.

    `price_band` is the quintile of the brand-new price within its January; `recent` marks the last
    RECENT_YEARS references.
    """
    jan = prices[prices["ref_month"] == JANUARY]
    keys = ["ref_year", "codigo_fipe", "fuel_group"]
    new = jan[jan["is_new"]][[*keys, "price_brl"]].rename(columns={"price_brl": "new"})
    new["price_band"] = _quintiles(new["new"], new["ref_year"])
    used = jan[~jan["is_new"]].copy()
    used["age"] = used["ref_year"] - used["model_year"].astype(int)
    used = used[(used["age"] >= 0) & (used["age"] <= max_age)]
    pairs = used.merge(new, on=keys)
    pairs["ratio"] = pairs["price_brl"] / pairs["new"]
    pairs["recent"] = pairs["ref_year"] > int(jan["ref_year"].max()) - RECENT_YEARS
    return pairs


def _summary(df: pd.DataFrame, by: list[str], value: str, quartiles: bool = True) -> pd.DataFrame:
    agg = {"n": (value, "size"), "median": (value, "median")}
    if quartiles:
        agg |= {"p25": (value, lambda s: s.quantile(0.25)), "p75": (value, lambda s: s.quantile(0.75))}
    return df.groupby(by, observed=True).agg(**agg).reset_index()


def _cohort_pairs(prices: pd.DataFrame) -> pd.DataFrame:
    """Cars bought brand new in January Y, valued in each later January.

    The brand-new price (`is_new`) of a code and fuel group in January Y is matched with the used price of the
    same code, fuel group and model year Y in January Y + age. `real` and `nominal` are the share of the
    purchase price left; `price_band` is the quintile of the purchase price within its January.
    """
    jan = prices[prices["ref_month"] == JANUARY]
    keys = ["codigo_fipe", "fuel_group"]
    new = jan[jan["is_new"]][["ref_year", *keys, "brand", "model", "price_brl", "price_real_brl"]].rename(
        columns={"ref_year": "purchase_year", "price_brl": "new_nominal", "price_real_brl": "new_real"}
    )
    new["price_band"] = _quintiles(new["new_real"], new["purchase_year"])
    used = jan[~jan["is_new"]][["ref_year", *keys, "model_year", "price_brl", "price_real_brl"]].copy()
    used["purchase_year"] = used["model_year"].astype(int)
    pairs = used.merge(new, on=["purchase_year", *keys])
    pairs["age"] = pairs["ref_year"] - pairs["purchase_year"]
    pairs = pairs[pairs["age"] >= 1].copy()
    pairs["real"] = pairs["price_real_brl"] / pairs["new_real"]
    pairs["nominal"] = pairs["price_brl"] / pairs["new_nominal"]
    return pairs


def cohort(prices: pd.DataFrame) -> pd.DataFrame:
    """Share of the purchase price left, by year of purchase and age (the same car since it was bought new).

    Real values divide inflation-adjusted prices, so 0.75 means the car is worth 75% of what was paid, in
    money of the same value. This is the headline method for "how much does my car lose" (docs/adr/0006).
    """
    pairs = _cohort_pairs(prices)
    g = pairs.groupby(["purchase_year", "age"])
    out = pd.DataFrame(
        {
            "n": g.size(),
            "median_real": g["real"].median(),
            "p25_real": g["real"].quantile(0.25),
            "p75_real": g["real"].quantile(0.75),
            "median_nominal": g["nominal"].median(),
        }
    ).reset_index()
    return out.astype({"purchase_year": int, "age": int, "n": int}).round(4)


def cohort_pooled(prices: pd.DataFrame, max_age: int = 10) -> pd.DataFrame:
    """The cohort pooled over every year of purchase, by age.

    The result depends on which years are pooled, so the site uses it only for the first year and always next
    to the range across years of purchase.
    """
    pairs = _cohort_pairs(prices)
    pairs = pairs[pairs["age"] <= max_age]
    g = pairs.groupby("age")
    out = pd.DataFrame(
        {
            "n": g.size(),
            "purchase_years": g["purchase_year"].nunique(),
            "median_real": g["real"].median(),
            "median_nominal": g["nominal"].median(),
        }
    ).reset_index()
    return out.astype({"age": int, "n": int, "purchase_years": int}).round(4)


def loss_by_age(prices: pd.DataFrame, max_age: int = 30) -> pd.DataFrame:
    """Median change of the same used car from one January to the next, by its age in the second January.

    Leaves out the SHOCK_YEAR arrival, so it describes a normal year. Age 1 means the car went from the
    current model year to one year old.
    """
    pairs = _yearly_pairs(prices)
    pairs = pairs[(pairs["to_year"] != SHOCK_YEAR) & (pairs["age"] >= 1) & (pairs["age"] <= max_age)]
    g = pairs.groupby("age")
    out = pd.DataFrame(
        {
            "n": g.size(),
            "years": g["to_year"].nunique(),
            "median_real": g["real"].median(),
            "p25_real": g["real"].quantile(0.25),
            "p75_real": g["real"].quantile(0.75),
            "median_nominal": g["nominal"].median(),
        }
    ).reset_index()
    return out.astype({"age": int, "n": int, "years": int}).round(4)


def four_year_change(prices: pd.DataFrame, span: int = 4) -> pd.DataFrame:
    """The same used car over `span` years, for every start January: what was left of the 2022 shock."""
    used = _january_used(prices)
    years = sorted(used["ref_year"].unique())
    rows = []
    for start in years:
        end = start + span
        if end not in years:
            continue
        a = used[used["ref_year"] == start].set_index(CAR)
        b = used[used["ref_year"] == end].set_index(CAR)
        pairs = a.join(b, how="inner", lsuffix="_a", rsuffix="_b")
        rows.append(
            {
                "from_year": int(start),
                "to_year": int(end),
                "n": len(pairs),
                "median_real": (pairs["price_real_brl_b"] / pairs["price_real_brl_a"] - 1).median(),
                "median_nominal": (pairs["price_brl_b"] / pairs["price_brl_a"] - 1).median(),
            }
        )
    return pd.DataFrame(rows).round(4)


def _relative(df: pd.DataFrame, by: list[str], value: str = "real") -> pd.Series:
    """Each value over the median of its group: 1.09 means 9% above comparable cars."""
    return df[value] / df.groupby(by)[value].transform("median")


def holds_value(prices: pd.DataFrame, age: int = HOLDS_VALUE_AGE) -> pd.DataFrame:
    """What holds value five years after purchase, against cars bought new the same year in the same band.

    The year of purchase alone moves retention from about 40% to 75%, so raw comparisons mislead. Groups:
    brand (with at least HOLDS_VALUE_MIN_N cars), fuel group (purchases from DIESEL_LABEL_FROM on, when the
    diesel label became reliable) and price band (relative to the purchase year only, since the band is the
    control itself). `median_relative` of 1.09 means 9% above comparable cars.
    """
    pairs = _cohort_pairs(prices)
    pairs = pairs[pairs["age"] == age].copy()
    pairs["rel"] = _relative(pairs, ["purchase_year", "price_band"])
    pairs["rel_year"] = _relative(pairs, ["purchase_year"])
    counts = pairs["brand"].value_counts()
    brands = pairs[pairs["brand"].isin(counts[counts >= HOLDS_VALUE_MIN_N].index)]
    fuels = pairs[pairs["purchase_year"] >= DIESEL_LABEL_FROM]
    frames = []
    for group_type, df, col, value in [
        ("brand", brands, "brand", "rel"),
        ("fuel_group", fuels, "fuel_group", "rel"),
        ("price_band", pairs, "price_band", "rel_year"),
    ]:
        g = df.groupby(col)
        out = pd.DataFrame(
            {
                "n": g.size(),
                "purchase_years": g["purchase_year"].nunique(),
                "median_relative": g[value].median(),
                "p25_relative": g[value].quantile(0.25),
                "p75_relative": g[value].quantile(0.75),
                "median_real": g["real"].median(),
            }
        ).reset_index(names="group")
        out.insert(0, "group_type", group_type)
        frames.append(out)
    out = pd.concat(frames, ignore_index=True)
    return out.astype({"n": int, "purchase_years": int}).round(4)


def version_gap(prices: pd.DataFrame, ages: tuple[int, ...] = (3, 5)) -> pd.DataFrame:
    """Top of the range against the entry version of the same model family, bought new the same year.

    Within a family (fipe/family.py), purchase year and fuel group with at least VERSION_MIN_CODES versions
    and a price spread of at least VERSION_MIN_SPREAD, compares the share of the purchase price left by the
    most and the least expensive version: `median_gap` of -0.09 means the top version keeps 9% less.
    """
    pairs = _cohort_pairs(prices)
    pairs["family"] = [family(b, m) for b, m in zip(pairs["brand"], pairs["model"], strict=True)]
    rows = []
    for age in ages:
        at = pairs[(pairs["age"] == age) & pairs["family"].notna()]
        gaps = []
        for _, grp in at.groupby(["family", "purchase_year", "fuel_group"]):
            if len(grp) < VERSION_MIN_CODES:
                continue
            grp = grp.sort_values("new_real")
            entry, top = grp.iloc[0], grp.iloc[-1]
            if top["new_real"] / entry["new_real"] < VERSION_MIN_SPREAD:
                continue
            gaps.append(top["real"] / entry["real"] - 1)
        gap = pd.Series(gaps, dtype=float)
        rows.append(
            {
                "age": age,
                "groups": len(gap),
                "median_gap": gap.median(),
                "p25_gap": gap.quantile(0.25),
                "p75_gap": gap.quantile(0.75),
                "share_top_keeps_less": (gap < 0).mean(),
            }
        )
    return pd.DataFrame(rows).round(4)


def fuel_relabels(prices: pd.DataFrame, min_n: int = 10) -> pd.DataFrame:
    """Cars whose fuel label changed from one January to the next.

    Same code, model year and new/used flag, with one price in each year. Documents the 2011 diesel and the
    2024 flex relabels.
    """
    jan = prices[prices["ref_month"] == JANUARY]
    key = ["codigo_fipe", "is_new", "model_year"]
    single = jan[~jan.duplicated(["ref_year", *key], keep=False)]
    rows = []
    years = sorted(single["ref_year"].unique())
    for prev, cur in zip(years, years[1:], strict=False):
        a = single[single["ref_year"] == prev]
        b = single[single["ref_year"] == cur]
        m = a.merge(b, on=key, suffixes=("_a", "_b"))
        changed = m[m["fuel_a"] != m["fuel_b"]]
        for (fa, fb), n in changed.groupby(["fuel_a", "fuel_b"]).size().items():
            if n >= min_n:
                rows.append(
                    {
                        "from_year": int(prev),
                        "to_year": int(cur),
                        "fuel_from": fa,
                        "fuel_to": fb,
                        "cars": int(n),
                    }
                )
    return pd.DataFrame(rows, columns=["from_year", "to_year", "fuel_from", "fuel_to", "cars"])


def yearly_change(prices: pd.DataFrame, ipca: pd.DataFrame) -> pd.DataFrame:
    """How the price of the same used car moved from one January to the next.

    Pairs every used car (fipe/clean.py CAR key) present in two consecutive Januaries; the car is one year
    older in the second one, so the change mixes ageing with the market. Medians of the price ratio minus 1,
    nominal and real, next to the January-to-January IPCA and, for context, the nominal change of brand-new
    prices (same code and fuel group, `new_n` pairs). `mass_*` is the sensitivity without PREMIUM_BRANDS and
    with cars aged MASS_AGES only, closer to what most people own.
    """
    jan_new = prices[(prices["ref_month"] == JANUARY) & prices["is_new"]]
    new_key = ["codigo_fipe", "fuel_group"]
    jan = ipca[ipca["month"] == JANUARY].set_index("year")["ipca_index"]
    rows = []
    for (prev, cur), pairs in _yearly_pairs(prices).groupby(["from_year", "to_year"]):
        q = _quantiles(pairs["real"])
        mass = pairs[~pairs["brand"].isin(PREMIUM_BRANDS) & pairs["age"].between(*MASS_AGES)]
        na = jan_new[jan_new["ref_year"] == prev].set_index(new_key)
        nb = jan_new[jan_new["ref_year"] == cur].set_index(new_key)
        new_pairs = na.join(nb, how="inner", lsuffix="_a", rsuffix="_b")
        rows.append(
            {
                "from_year": int(prev),
                "to_year": int(cur),
                "n": len(pairs),
                "median_nominal": pairs["nominal"].median(),
                "median_real": q["median"],
                "p25_real": q["p25"],
                "p75_real": q["p75"],
                "ipca": jan[cur] / jan[prev] - 1,
                "new_n": len(new_pairs),
                "new_median_nominal": (new_pairs["price_brl_b"] / new_pairs["price_brl_a"] - 1).median(),
                "mass_n": len(mass),
                "mass_median_real": mass["real"].median(),
            }
        )
    return pd.DataFrame(rows).round(4)


def new_vs_used(prices: pd.DataFrame) -> pd.DataFrame:
    """What a used car of the current model year is worth next to the same car brand new, per January.

    Matches, within a reference month, the brand-new price (`is_new`) and the used price with model year equal
    to the reference year, for the same code and fuel group. A median of 0.90 means a 10% gap. `max_ratio` is
    the highest single pair: it never reaches 1, which looks like a FIPE rule for the current model year.
    """
    jan = prices[prices["ref_month"] == JANUARY]
    keys = ["ref_year", "codigo_fipe", "fuel_group"]
    new = jan[jan["is_new"]][[*keys, "price_brl"]].rename(columns={"price_brl": "new"})
    same_year = jan[~jan["is_new"] & (jan["model_year"] == jan["ref_year"])]
    used = same_year[[*keys, "price_brl"]].rename(columns={"price_brl": "used"})
    pairs = used.merge(new, on=keys, validate="one_to_one")
    ratio = pairs["used"] / pairs["new"]
    out = (
        ratio.groupby(pairs["ref_year"])
        .agg(
            n="size",
            median="median",
            p25=lambda s: s.quantile(0.25),
            p75=lambda s: s.quantile(0.75),
            max_ratio="max",
        )
        .reset_index()
        .rename(columns={"median": "median_ratio", "p25": "p25_ratio", "p75": "p75_ratio"})
    )
    out["ref_year"] = out["ref_year"].astype(int)
    return out.round(4)


def retention_by_age(prices: pd.DataFrame, max_age: int = 15) -> pd.DataFrame:
    """Share of the brand-new price a car keeps at each age, within the same January.

    For every code and fuel group with a brand-new price in a reference month, each used model year is divided
    by that brand-new price (same month, so inflation cancels out). Age = reference year minus model year.
    Two scopes: every January ("all") and the last RECENT_YEARS of them ("recent").
    """
    pairs = _retention_pairs(prices, max_age)
    frames = []
    for scope, df in {"all": pairs, "recent": pairs[pairs["recent"]]}.items():
        g = _summary(df, ["age"], "ratio").rename(
            columns={"median": "median_ratio", "p25": "p25_ratio", "p75": "p75_ratio"}
        )
        g.insert(0, "scope", scope)
        frames.append(g)
    out = pd.concat(frames, ignore_index=True)
    out["age"] = out["age"].astype(int)
    return out.round(4)


def explore_brands(prices: pd.DataFrame, max_age: int = EXPLORE_MAX_AGE) -> list[str]:
    """Brands with enough retention pairs to be offered in the explore page, most data first."""
    counts = _retention_pairs(prices, max_age)["brand"].value_counts()
    return counts[counts >= EXPLORE_MIN_BRAND_N].index.tolist()


def _by_group(
    pairs: pd.DataFrame, brands: list[str], keys: list[str], value: str, quartiles: bool
) -> pd.DataFrame:
    """The same summary for everything, per brand (only `brands`), per fuel group and per price band."""
    groups = {
        "all": pairs.assign(group="all"),
        "brand": pairs[pairs["brand"].isin(brands)].assign(group=lambda d: d["brand"]),
        "fuel_group": pairs.assign(group=lambda d: d["fuel_group"]),
        "price_band": pairs.assign(group=lambda d: d["price_band"]),
    }
    frames = []
    for group_type, df in groups.items():
        g = _summary(df, ["group", *keys], value, quartiles)
        g.insert(0, "group_type", group_type)
        frames.append(g)
    return pd.concat(frames, ignore_index=True)


def explore_retention(prices: pd.DataFrame, max_age: int = EXPLORE_MAX_AGE) -> pd.DataFrame:
    """retention_by_age by brand, fuel group and brand-new price band, both scopes, up to EXPLORE_MAX_AGE."""
    pairs = _retention_pairs(prices, max_age)
    brands = explore_brands(prices, max_age)
    frames = []
    for scope, df in {"all": pairs, "recent": pairs[pairs["recent"]]}.items():
        g = _by_group(df, brands, ["age"], "ratio", quartiles=True)
        g.insert(1, "scope", scope)
        frames.append(g)
    out = pd.concat(frames, ignore_index=True)
    out["age"] = out["age"].astype(int)
    return out.rename(columns={"median": "median_ratio", "p25": "p25_ratio", "p75": "p75_ratio"}).round(4)


def explore_yearly(prices: pd.DataFrame) -> pd.DataFrame:
    """The real change of the same used car per January, by brand, fuel group and price band."""
    pairs = _yearly_pairs(prices)
    out = _by_group(pairs, explore_brands(prices), ["to_year"], "real", quartiles=False)
    out["to_year"] = out["to_year"].astype(int)
    return out.rename(columns={"median": "median_real"}).round(4)


def coverage(prices: pd.DataFrame) -> pd.DataFrame:
    """Per reference month: how many prices, brand-new prices, FIPE codes and brands the table has."""
    g = prices.groupby(["ref_year", "ref_month"])
    out = pd.DataFrame(
        {
            "prices": g.size(),
            "new_car_prices": g["is_new"].sum(),
            "codigos_fipe": g["codigo_fipe"].nunique(),
            "brands": g["brand"].nunique(),
        }
    ).reset_index()
    return out.astype({"ref_year": int, "ref_month": int, "new_car_prices": int})


def fuel_labels(prices: pd.DataFrame) -> pd.DataFrame:
    """Prices per fuel label and January: shows the 2024 split of "Gasolina" (fipe/clean.py FUEL_GROUP)."""
    jan = prices[prices["ref_month"] == JANUARY]
    out = jan.groupby(["ref_year", "fuel"]).size().rename("prices").reset_index()
    return (
        out.astype({"ref_year": int, "prices": int}).sort_values(["ref_year", "fuel"]).reset_index(drop=True)
    )
