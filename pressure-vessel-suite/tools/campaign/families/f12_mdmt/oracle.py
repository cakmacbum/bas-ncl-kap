"""Independent reference ledger; no code-plugin implementation is used.

The standard's plotted curve data is deliberately not reconstructed from
memory. Published K4 outputs are retained as point references; all other
points are unreferenced and must remain KAYNAK_BEKLİYOR.
"""

PUBLISHED = {
    "K4-09": {"quantity": "MDMT", "value_c": -48.3333333333,
              "source": "K4 sources-K4.md §B, K4-09 (PVEng/PV Elite, 2015); -55 °F"},
    "K4-10": {"quantity": "MDMT", "value_c": -31.1111111111,
              "source": "K4 sources-K4.md §B, K4-10 (PVEng/PV Elite, 2015); -24 °F"},
    "K4-13": {"quantity": "MDMT", "value_c": -98.8888888889,
              "source": "K4 sources-K4.md §B, K4-13; -146 °F"},
    "K4-16": {"quantity": "MDMT", "value_c": -19.4444444444,
              "source": "K4 sources-K4.md §B, K4-16; -3 °F"},
}


def oracle(case_id):
    return PUBLISHED.get(case_id)
