"""Isotherm for the p-v plot and isobar for the T-v plot.

Lecture concepts used: lists, for loops, if/else (Weeks 2-3),
np.linspace and arrays (Week 4).

Each curve has three parts, drawn in order so they join into one line:
    1. liquid part   (left of the dome)
    2. flat part     (inside the dome, from vf to vg)
    3. vapor part    (right of the dome)
"""
import numpy as np

from thermo_state.data import Psat, Tsat, vf_at_P, vg_at_P, vf_at_T, vg_at_T, superheated_volume

N_POINTS = 100   # points per part of each curve


def isotherm_pv(table, T1):
    """Return v and P arrays for the isotherm at temperature T1 (p-v diagram)."""
    P_lowest = table["temperature"]["P"][0]   # lowest pressure in the tables
    P_crit = table["P_crit"]

    v_list = []
    P_list = []

    if T1 < table["T_crit"]:
        P_sat = Psat(table, T1)
        vf = vf_at_T(table, T1)
        vg = vg_at_T(table, T1)

        # 1. Liquid part: liquid is almost incompressible, so v stays ≈ vf
        #    as P goes up. That's a vertical line from P_crit down to P_sat.
        for P in np.linspace(P_crit, P_sat, N_POINTS):
            v_list.append(vf)
            P_list.append(P)

        # 2. Flat part: inside the dome P stays at P_sat while v goes vf -> vg
        v_list.append(vg)
        P_list.append(P_sat)

        P_vapor_start = P_sat
    else:
        # Above the critical temperature there is no dome crossing:
        # the isotherm is all vapor.
        P_vapor_start = P_crit

    # 3. Vapor part: from where the vapor starts down to the lowest table pressure.
    #    Spread the points evenly in ln(P) so the low pressures (which are
    #    bunched up on the plot) still get enough points.
    for lnP in np.linspace(np.log(P_vapor_start), np.log(P_lowest), N_POINTS):
        P = np.exp(lnP)
        # exp(log(P)) can come back a hair off (round-off error, Week 5),
        # e.g. 220.9000000000001, which is "outside the table". Clamp it.
        if P > P_vapor_start:
            P = P_vapor_start
        if P < P_lowest:
            P = P_lowest
        v_list.append(superheated_volume(table, P, T1))
        P_list.append(P)

    return np.array(v_list), np.array(P_list)


def isobar_tv(table, P1, T_top):
    """Return v and T arrays for the isobar at pressure P1 (T-v diagram).

    T_top: highest temperature to draw the vapor part up to.
    """
    T_lowest = table["temperature"]["T"][0]
    T_sat = Tsat(table, P1)

    v_list = []
    T_list = []

    # 1. Liquid part: compressed liquid has v ≈ vf at the same T,
    #    so this part follows the liquid side of the dome up to T_sat.
    for T in np.linspace(T_lowest, T_sat, N_POINTS):
        v_list.append(vf_at_T(table, T))
        T_list.append(T)

    # 2. Flat part: inside the dome T stays at T_sat while v goes vf -> vg
    v_list.append(vg_at_P(table, P1))
    T_list.append(T_sat)

    # 3. Vapor part: ideal-gas estimate from vg up to T_top
    for T in np.linspace(T_sat, T_top, N_POINTS):
        v_list.append(superheated_volume(table, P1, T))
        T_list.append(T)

    return np.array(v_list), np.array(T_list)
