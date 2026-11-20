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

    # ---- 5. Superheated vapor table (Table A-4), from its own CSV ----
    table["superheated"] = load_superheated()

    return table


def load_superheated():
    """Read Table A-4 (superheated water vapor) into a list of "blocks".

    The book prints A-4 as one block per pressure (0.06 bar, 0.35 bar, ...,
    320 bar). Each block lists T and v from saturation upward. The CSV keeps
    that order: sorted by pressure, then by temperature. The first row of
    each block below the critical pressure is the "Sat." row (T = Tsat).

    Returns a list like:
        [ {"P": 0.06, "T": array([36.16, 80, ...]), "v": array([23.739, 27.132, ...])},
          {"P": 0.35, "T": ..., "v": ...},
          ... ]
    """
    df = pd.read_csv("data/superheated_water_SI.csv")

    blocks = []
    for i in range(len(df)):
        P = df["P_bar"][i]
        # A new pressure means a new block
        if len(blocks) == 0 or P != blocks[-1]["P"]:
            blocks.append({"P": P, "T": [], "v": []})
        blocks[-1]["T"].append(df["T_C"][i])
        blocks[-1]["v"].append(df["v_m3_per_kg"][i])

    # Lists -> NumPy arrays
    for block in blocks:
        block["T"] = np.array(block["T"])
        block["v"] = np.array(block["v"])

    return blocks


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


def v_in_block(block, T):
    """v at temperature T inside ONE pressure block of Table A-4."""
    T_first = block["T"][0]
    T_last = block["T"][-1]

    if T < T_first:
        # Can only happen by a hair (rounding between Tables A-3 and A-4):
        # use the saturated-vapor row
        return block["v"][0]
    elif T <= T_last:
        return linear_interpolation(T, block["T"], block["v"])
    else:
        # Hotter than the table goes: extend with the ideal gas law.
        # At constant P, v is proportional to absolute temperature.
        return block["v"][-1] * (T + KELVIN_OFFSET) / (T_last + KELVIN_OFFSET)


def superheated_volume(table, P, T):
    """v of superheated vapor at (P, T), from Table A-4 by double interpolation.

    1. Find the two A-4 pressure blocks around P (e.g. P = 50 bar -> 40 and 60 bar).
    2. In each block, interpolate in T to get v at T.
    3. Interpolate between the two blocks in P.
    (Steps 2 and 3 are in double_interpolation below.)

    Step 3 interpolates P*v instead of v. v is roughly proportional to 1/P
    (ideal gas), so it curves a lot between pressures, but P*v is almost
    constant, so a straight line between the two blocks is very accurate.
    (Same idea as the Week 10 fits: transform first so the data is close
    to a straight line.) Example at 200 °C between 0.06 and 0.35 bar:
    interpolating v directly gives 21.8 m³/kg at 0.2 bar, but P*v gives
    10.9 m³/kg, which is the right answer.

    Check (50 bar, 500 °C):
        40 bar: P*v = 40 * 0.08643 = 3.457      60 bar: P*v = 60 * 0.05665 = 3.399
        50 bar: P*v = 3.428  ->  v = 3.428 / 50 = 0.06856 m³/kg
    """
    blocks = table["superheated"]

    # Below the lowest A-4 pressure (0.06 bar), steam is an ideal gas almost
    # exactly, so start from vg and scale by absolute temperature.
    if P < blocks[0]["P"]:
        T_abs = T + KELVIN_OFFSET
        Tsat_abs = Tsat(table, P) + KELVIN_OFFSET
        return vg_at_P(table, P) * T_abs / Tsat_abs

    # 1. Find the blocks just below and just above P
    #    (P exactly on a block, like 200 bar, uses that block as "low")
    low = blocks[0]
    high = blocks[1]
    for i in range(len(blocks) - 1):
        if P >= blocks[i]["P"] and P < blocks[i + 1]["P"]:
            low = blocks[i]
            high = blocks[i + 1]
            break

    T_start = high["T"][0]     # first temperature the higher block has

    if T >= T_start:
        # Both blocks have data at T: normal double interpolation
        return double_interpolation(low, high, P, T)
    else:
        # Just above the dome. The higher-pressure block has no rows this
        # cold (it would be liquid there). So interpolate in T between:
        #   - the saturated vapor at P:  (Tsat(P), vg(P))  from Table A-3
        #   - the first T both blocks have:  (T_start, v at T_start)
        T_s = Tsat(table, P)
        v_s = vg_at_P(table, P)
        if T <= T_s:
            return v_s
        v_start = double_interpolation(low, high, P, T_start)
        return linear_interpolation(T, [T_s, T_start], [v_s, v_start])


def double_interpolation(low, high, P, T):
    """v at (P, T) from two neighboring A-4 blocks (low P and high P).

    2. Interpolate in T inside each block.
    3. Interpolate between the blocks in P, using P*v (see superheated_volume).
    """
    Pv_low = low["P"] * v_in_block(low, T)
    Pv_high = high["P"] * v_in_block(high, T)
    Pv = linear_interpolation(P, [low["P"], high["P"]], [Pv_low, Pv_high])
    return Pv / P
