"""Checks to run once the functions are written:  python -m pytest

Add more as you go.
"""
from thermo_state.data import Tsat, load_table
from thermo_state.state import COMPRESSED, SATURATED, SUPERHEATED, find_state


def test_tsat_matches_table():
    table = load_table("SI")
    assert abs(Tsat(table, 10.0) - 179.9) < 0.1      # Table A-3: 10 bar


def test_states_at_1_bar():
    table = load_table("SI")
    assert find_state(table, 1.0, 20) == COMPRESSED
    assert find_state(table, 1.0, 99.63) == SATURATED
    assert find_state(table, 1.0, 200) == SUPERHEATED
