"""Loads the saturated-water tables and looks up values in them.

Lecture concepts used:
    pandas read_csv (Week 5), lists + for loops (Week 3), if/elif (Week 2),
    NumPy arrays (Week 4), dictionaries (Python_Basics.py),
    linear interpolation (Week 2, "Program: Linear Interpolation").

NOTE: run the program from the project folder (the one with main.py),
because the CSV paths below are relative to that folder.
"""
import numpy as np
import pandas as pd


# Kelvin = °C + 273.15 (absolute temperature, used in the ideal-gas estimate)
KELVIN_OFFSET = 273.15


def load_table():
    """Read the SI saturated-water CSV and return everything in one dictionary.

    Units everywhere: T in °C, P in bar, v in m³/kg.
    """
    # ---- 1. Read the file ----
    df = pd.read_csv("data/sat_water_SI.csv")

    # ---- 2. Split the rows into the temperature table and the pressure table ----
    # Each row's "table" column says which book table it came from.
    T_temp = []
    P_temp = []
    vf_temp = []
    vg_temp = []

    T_press = []
    P_press = []
    vf_press = []
    vg_press = []

    for i in range(len(df)):
        if df["table"][i] == "A-2":            # temperature table
            T_temp.append(df["T_C"][i])
            P_temp.append(df["P_bar"][i])
            vf_temp.append(df["vf_m3_per_kg"][i])
            vg_temp.append(df["vg_m3_per_kg"][i])
        elif df["table"][i] == "A-3":          # pressure table
            T_press.append(df["T_C"][i])
            P_press.append(df["P_bar"][i])
            vf_press.append(df["vf_m3_per_kg"][i])
            vg_press.append(df["vg_m3_per_kg"][i])

    # ---- 3. Put everything in one dictionary (lists -> NumPy arrays) ----
    table = {
        "temperature": {          # Table A-2 (rows listed by T)
            "T": np.array(T_temp),
            "P": np.array(P_temp),
            "vf": np.array(vf_temp),
            "vg": np.array(vg_temp),
        },
        "pressure": {             # Table A-3 (rows listed by P)
            "T": np.array(T_press),
            "P": np.array(P_press),
            "vf": np.array(vf_press),
            "vg": np.array(vg_press),
        },
    }

    # ---- 4. The last row of the pressure table is the critical point ----
    table["T_crit"] = T_press[-1]
    table["P_crit"] = P_press[-1]
    table["v_crit"] = vf_press[-1]

    return table


def linear_interpolation(x, x_data, y_data):
    """Find y at x by interpolating between the two table rows around x.

    Same formula as the Week 2 program:
        y = (x - x_low) / (x_high - x_low) * (y_high - y_low) + y_low
    x_data must be sorted from smallest to largest.
    """
    if x < x_data[0] or x > x_data[-1]:
        print(f"{x} is outside the table range {x_data[0]} to {x_data[-1]}")
        exit()

    # Walk down the table until x is between row i and row i+1
    for i in range(len(x_data) - 1):
        if x >= x_data[i] and x <= x_data[i + 1]:
            x_low = x_data[i]
            x_high = x_data[i + 1]
            y_low = y_data[i]
            y_high = y_data[i + 1]
            return (x - x_low) / (x_high - x_low) * (y_high - y_low) + y_low


# ---------------------------------------------------------------
# Saturation look-ups (all are just linear_interpolation calls)
# ---------------------------------------------------------------

def lookup_by_P(table, P, column):
    """Interpolate a column ("T", "vf" or "vg") at pressure P.

    Uses the pressure table when P is inside it. Below its first row
    (0.04 bar) it falls back to the temperature table, whose pressures go
    lower (down to 0.00611 bar at the triple point).
    """
    if P >= table["pressure"]["P"][0]:
        return linear_interpolation(P, table["pressure"]["P"], table["pressure"][column])
    else:
        return linear_interpolation(P, table["temperature"]["P"], table["temperature"][column])


def Tsat(table, P):
    """Saturation temperature at pressure P."""
    return lookup_by_P(table, P, "T")


def Psat(table, T):
    """Saturation pressure at temperature T (temperature table)."""
    return linear_interpolation(T, table["temperature"]["T"], table["temperature"]["P"])


def vf_at_P(table, P):
    """Saturated-liquid specific volume at pressure P."""
    return lookup_by_P(table, P, "vf")


def vg_at_P(table, P):
    """Saturated-vapor specific volume at pressure P."""
    return lookup_by_P(table, P, "vg")


def vf_at_T(table, T):
    """Saturated-liquid specific volume at temperature T."""
    return linear_interpolation(T, table["temperature"]["T"], table["temperature"]["vf"])


def vg_at_T(table, T):
    """Saturated-vapor specific volume at temperature T."""
    return linear_interpolation(T, table["temperature"]["T"], table["temperature"]["vg"])


def superheated_volume(table, P, T):
    """Approximate v of superheated vapor at (P, T).

    The saturated tables don't cover superheated vapor, so we start from
    vg at this pressure and treat the vapor as an ideal gas (Pv = RT).
    At constant P, v is proportional to absolute temperature:

        v = vg(P) * T_abs / Tsat_abs(P)

    Check against the Week 2 slide table (1.5 bar, 200 °C):
        1.159 * (200 + 273.15) / (111.37 + 273.15) = 1.426 m³/kg   (table: 1.444)
    """
    T_abs = T + KELVIN_OFFSET
    Tsat_abs = Tsat(table, P) + KELVIN_OFFSET
    return vg_at_P(table, P) * T_abs / Tsat_abs
