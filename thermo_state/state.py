"""Work out the state of water at the user's pressure P1 and temperature T1.

Lecture concepts used: if/elif/else branching (Week 2), functions (Week 4).
"""
import numpy as np

from thermo_state.data import Tsat, vf_at_P, vg_at_P, vf_at_T, superheated_volume

COMPRESSED = "COMPRESSED LIQUID"
SATURATED = "SAT. LIQUID-VAPOR"
SUPERHEATED = "SUPERHEATED VAPOR"

# How close T1 must be to Tsat to count as "saturated" (°C).
# Exact equality almost never happens with decimals, so we use a tolerance.
TOLERANCE = 0.1


def find_state(table, P1, T1):
    """Compare T1 with Tsat(P1):
        T1 < Tsat  ->  compressed liquid
        T1 = Tsat  ->  saturated liquid-vapor   (within TOLERANCE)
        T1 > Tsat  ->  superheated vapor
    main.py only allows P1 below the critical pressure, so Tsat always exists.
    """
    T_sat = Tsat(table, P1)

    if abs(T1 - T_sat) <= TOLERANCE:
        return SATURATED
    elif T1 < T_sat:
        return COMPRESSED
    else:
        return SUPERHEATED


def specific_volume(table, P1, T1, state_name):
    """Pick the v used to place the point (P1, T1) on the plots."""
    if state_name == COMPRESSED:
        # Liquid is almost incompressible: v ≈ vf at the same temperature
        return vf_at_T(table, T1)

    elif state_name == SATURATED:
        # Inside the dome P and T don't fix v (it can be anywhere from vf to vg).
        # We put the point in the visual middle of the line. The v-axis is
        # logarithmic, so the middle is the geometric mean sqrt(vf * vg).
        return np.sqrt(vf_at_P(table, P1) * vg_at_P(table, P1))

    else:
        # Superheated: ideal-gas estimate starting from vg (see data.py)
        return superheated_volume(table, P1, T1)
