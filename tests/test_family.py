import pytest

from fipe.family import family


@pytest.mark.parametrize(
    ("brand", "model", "expected"),
    [
        ("VW - VolksWagen", "Gol 1.0 Mi 8V", "VW - VolksWagen|GOL"),
        ("Toyota", "Corolla XEi 2.0 Flex 16V Aut.", "Toyota|COROLLA"),
        ("VW - VolksWagen", "New Beetle 2.0 Mi Mec./Aut.", "VW - VolksWagen|BEETLE"),
        ("VW - VolksWagen", "NOVA SAVEIRO Robust 1.6 Total Flex 16V", "VW - VolksWagen|SAVEIRO"),
        ("Fiat", "Grand Siena ATTRAC. 1.4 EVO F.Flex 8V", "Fiat|GRAND SIENA"),
        ("Jeep", "Grand Cherokee Limited 3.6 4x4 V6 Aut.", "Jeep|GRAND CHEROKEE"),
        ("Hyundai", "HB20S 1.6 Comf.Plus 16V Flex 4p Aut.", "Hyundai|HB20S"),
        ("Mitsubishi", "L200 Triton 3.2 CD TB Diesel", "Mitsubishi|L200"),
        ("Citroën", "C4-Lounge Tendance 1.6 THP Flex Aut.", "Citroën|C4"),
    ],
)
def test_family_is_brand_and_model_name(brand, model, expected):
    assert family(brand, model) == expected


def test_versions_of_the_same_model_share_a_family():
    entry = family("Fiat", "Palio 1.0 ECONOMY Fire Flex 8V 4p")
    top = family("Fiat", "Palio Sporting 1.6 Flex 16V 5p")
    assert entry == top == "Fiat|PALIO"


def test_a_name_with_only_a_prefix_has_no_family():
    assert family("VW - VolksWagen", "New") is None
