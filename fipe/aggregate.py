"""The aggregates behind every published number. Nothing else defines a finding (CLAUDE.md).

All tables use January references only and come with `n`, so a reader can always see how many prices a number
rests on. Inputs are the clean price table from fipe/clean.py (with `price_real_brl` from fipe/inflation.py).
"""

from __future__ import annotations

import pandas as pd

from fipe.clean import CAR

JANUARY = 1
RECENT_YEARS = 5  # "recent" scope in retention_by_age: the last five January references


def _january_used(prices: pd.DataFrame) -> pd.DataFrame:
    return prices[(prices["ref_month"] == JANUARY) & ~prices["is_new"]]


def _quantiles(s: pd.Series) -> dict[str, float]:
    return {"median": s.median(), "p25": s.quantile(0.25), "p75": s.quantile(0.75)}


def yearly_change(prices: pd.DataFrame, ipca: pd.DataFrame) -> pd.DataFrame:
    """How the price of the same used car moved from one January to the next.

    Pairs every used car (fipe/clean.py CAR key) present in two consecutive Januaries; the car is one year
    older in the second one, so the change mixes ageing with the market. Medians of the price ratio minus 1,
    nominal and real, next to the January-to-January IPCA and, for context, the nominal change of brand-new
    prices (same code and fuel group, `new_n` pairs).
    """
    used = _january_used(prices)
    jan_new = prices[(prices["ref_month"] == JANUARY) & prices["is_new"]]
    new_key = ["codigo_fipe", "fuel_group"]
    jan = ipca[ipca["month"] == JANUARY].set_index("year")["ipca_index"]
    rows = []
    years = sorted(used["ref_year"].unique())
    for prev, cur in zip(years, years[1:], strict=False):
        if cur != prev + 1:
            continue
        a = used[used["ref_year"] == prev].set_index(CAR)
        b = used[used["ref_year"] == cur].set_index(CAR)
        pairs = a.join(b, how="inner", lsuffix="_a", rsuffix="_b")
        nominal = pairs["price_brl_b"] / pairs["price_brl_a"] - 1
        real = pairs["price_real_brl_b"] / pairs["price_real_brl_a"] - 1
        q = _quantiles(real)
        na = jan_new[jan_new["ref_year"] == prev].set_index(new_key)
        nb = jan_new[jan_new["ref_year"] == cur].set_index(new_key)
        new_pairs = na.join(nb, how="inner", lsuffix="_a", rsuffix="_b")
        rows.append(
            {
                "from_year": int(prev),
                "to_year": int(cur),
                "n": len(pairs),
                "median_nominal": nominal.median(),
                "median_real": q["median"],
                "p25_real": q["p25"],
                "p75_real": q["p75"],
                "ipca": jan[cur] / jan[prev] - 1,
                "new_n": len(new_pairs),
                "new_median_nominal": (new_pairs["price_brl_b"] / new_pairs["price_brl_a"] - 1).median(),
            }
        )
    return pd.DataFrame(rows).round(4)


def new_vs_used(prices: pd.DataFrame) -> pd.DataFrame:
    """What a used car of the current model year is worth next to the same car brand new, per January.

    Matches, within a reference month, the brand-new price (`is_new`) and the used price with model year equal
    to the reference year, for the same code and fuel group. A median of 0.90 means a 10% gap.
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
        .agg(n="size", median="median", p25=lambda s: s.quantile(0.25), p75=lambda s: s.quantile(0.75))
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
    jan = prices[prices["ref_month"] == JANUARY]
    keys = ["ref_year", "codigo_fipe", "fuel_group"]
    new = jan[jan["is_new"]][[*keys, "price_brl"]].rename(columns={"price_brl": "new"})
    used = jan[~jan["is_new"]].copy()
    used["age"] = used["ref_year"] - used["model_year"].astype(int)
    used = used[(used["age"] >= 0) & (used["age"] <= max_age)]
    pairs = used.merge(new, on=keys)
    pairs["ratio"] = pairs["price_brl"] / pairs["new"]

    last = int(jan["ref_year"].max())
    scopes = {"all": pairs, "recent": pairs[pairs["ref_year"] > last - RECENT_YEARS]}
    frames = []
    for scope, df in scopes.items():
        g = (
            df.groupby("age")["ratio"]
            .agg(n="size", median="median", p25=lambda s: s.quantile(0.25), p75=lambda s: s.quantile(0.75))
            .reset_index()
            .rename(columns={"median": "median_ratio", "p25": "p25_ratio", "p75": "p75_ratio"})
        )
        g.insert(0, "scope", scope)
        frames.append(g)
    out = pd.concat(frames, ignore_index=True)
    out["age"] = out["age"].astype(int)
    return out.round(4)


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
