"""Checks for data.py, fitting.py, state.py and curves.py.

Run from the project folder with:  python -m pytest -v
"""
import numpy as np
import pytest

from thermo_state.data import (Psat, Tsat, linear_interpolation, load_table,
                               superheated_volume, vf_at_T, vg_at_P)
from thermo_state.fitting import dome_curve, quadratic_fit
from thermo_state.state import COMPRESSED, SATURATED, SUPERHEATED, find_state, specific_volume
from thermo_state.curves import isobar_tv, isotherm_pv


# ---------- load_table ----------

def test_tables_have_rows():
    table = load_table()
    assert len(table["temperature"]["T"]) == 70
    assert len(table["pressure"]["P"]) == 50


def test_critical_point():
    table = load_table()
    assert table["T_crit"] == pytest.approx(374.1, abs=0.1)     # °C
    assert table["P_crit"] == pytest.approx(220.9, abs=0.1)     # bar
    assert table["v_crit"] == pytest.approx(0.003155, rel=1e-3)


# ---------- linear_interpolation ----------

def test_interpolation_halfway():
    assert linear_interpolation(5, [0, 10], [0, 100]) == pytest.approx(50)


def test_interpolation_out_of_range_exits():
    with pytest.raises(SystemExit):           # exit() is called
        linear_interpolation(25, [0, 10, 20], [0, 100, 400])


# ---------- saturation look-ups ----------

def test_psat():
    table = load_table()
    assert Psat(table, 100) == pytest.approx(1.014, abs=0.001)  # Table A-2


def test_tsat_1_atm():
    table = load_table()
    assert Tsat(table, 1.01325) == pytest.approx(100, abs=0.1)  # 1 atm boils at 100 °C


def test_tsat_below_pressure_table():
    # 0.0234 bar is below the pressure table (starts at 0.04 bar),
    # so this uses the temperature table: Psat(20 °C) = 0.02339 bar
    table = load_table()
    assert Tsat(table, 0.02339) == pytest.approx(20, abs=0.1)


def test_superheated_matches_week2_table():
    # Week 2 slide: 1.5 bar, 200 °C -> v = 1.444 m³/kg (ideal-gas estimate within 2%)
    table = load_table()
    assert superheated_volume(table, 1.5, 200) == pytest.approx(1.444, rel=0.02)


# ---------- fitting ----------

def test_quadratic_fit_exact():
    # Points on y = 2x² - 3x + 1 should give back a=2, b=-3, c=1
    x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    a, b, c = quadratic_fit(x, 2 * x**2 - 3 * x + 1)
    assert a == pytest.approx(2)
    assert b == pytest.approx(-3)
    assert c == pytest.approx(1)


def test_dome_passes_near_data():
    # Every vg point in the pressure table should be within 5% of the fitted dome
    table = load_table()
    P = table["pressure"]["P"]
    v_dome, P_dome = dome_curve(P, table["pressure"]["vf"], table["pressure"]["vg"])
    for i in range(len(P) - 1):
        closest = np.min(np.abs(np.log(v_dome) - np.log(table["pressure"]["vg"][i])))
        assert closest < 0.05


def test_dome_top_near_critical_point():
    table = load_table()
    v_dome, T_dome = dome_curve(table["temperature"]["T"],
                                table["temperature"]["vf"], table["temperature"]["vg"])
    assert np.max(T_dome) == pytest.approx(table["T_crit"], abs=2)


# ---------- state ----------

def test_states_at_5_bar():
    table = load_table()
    assert find_state(table, 5.0, 20) == COMPRESSED
    assert find_state(table, 5.0, 300) == SUPERHEATED


def test_point_is_inside_dome_when_saturated():
    table = load_table()
    v = specific_volume(table, 1.0, 99.63, SATURATED)
    assert v > table["pressure"]["vf"][0] and v < vg_at_P(table, 1.0)


def test_compressed_volume_is_vf():
    table = load_table()
    assert specific_volume(table, 10.0, 50, COMPRESSED) == pytest.approx(vf_at_T(table, 50))


# ---------- curves ----------

def test_isotherm_has_flat_part_at_psat():
    table = load_table()
    v, P = isotherm_pv(table, 100)
    P_sat = Psat(table, 100)
    flat = 0
    for p in P:
        if abs(p - P_sat) < 1e-9:
            flat = flat + 1
    assert flat >= 2                     # both ends of the flat line


def test_isotherm_above_critical_is_all_vapor():
    table = load_table()
    v, P = isotherm_pv(table, 500)
    assert np.min(v) > table["v_crit"] * 0.9


def test_isobar_reaches_top():
    table = load_table()
    v, T = isobar_tv(table, 1.0, 400)
    assert T[0] == pytest.approx(table["temperature"]["T"][0])
    assert T[-1] == pytest.approx(400)
