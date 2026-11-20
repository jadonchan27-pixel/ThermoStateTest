"""Draw the two plot windows: p-v and T-v (see docs/project_sketch.png).

Lecture concepts used (Week 5 plotting):
    plt.figure, plt.subplot (side-by-side plots), semilog plots,
    plt.xlabel / plt.ylabel / plt.title, plt.legend, plt.grid, plt.show

The v-axis is logarithmic (plt.semilogx). With a normal axis the liquid side
of the dome (v ≈ 0.001) would be squashed against the axis, because vg goes
up to ~206 m³/kg. On a log axis the dome looks like the sketch.
"""
import matplotlib.pyplot as plt

from thermo_state.fitting import dome_curve
from thermo_state.curves import isotherm_pv, isobar_tv
from thermo_state.state import specific_volume


def plot_pv(table, P1, T1, v1, state_name):
    """Draw the p-v diagram in the current subplot."""
    P_data = table["pressure"]["P"]
    vf_data = table["pressure"]["vf"]
    vg_data = table["pressure"]["vg"]

    # 1. Table data points (pressure table)
    plt.semilogx(vf_data, P_data, 'g*', label='Table data')
    plt.semilogx(vg_data, P_data, 'g*')

    # 2. Best-fit dome (fitting.py)
    v_dome, P_dome = dome_curve(P_data, vf_data, vg_data)
    plt.semilogx(v_dome, P_dome, 'r-', linewidth=2, label='Best fit (vapor dome)')

    # 3. Isotherm for T1
    v_iso, P_iso = isotherm_pv(table, T1)
    plt.semilogx(v_iso, P_iso, 'm-', label=f'Isotherm T1 = {T1} {table["T_label"]}')

    # 4. The point (P1, T1)
    plt.semilogx(v1, P1, 'mo', markersize=9, label='(P1, T1)')

    # 5. Labels, state of water, legend
    plt.xlabel(f'Specific volume v [{table["v_label"]}]')
    plt.ylabel(f'Pressure P [{table["P_label"]}]')
    plt.title(f'p-v diagram:  {state_name}')
    plt.legend()
    plt.grid(True)


def plot_tv(table, P1, T1, v1, state_name):
    """Draw the T-v diagram in the current subplot."""
    T_data = table["temperature"]["T"]
    vf_data = table["temperature"]["vf"]
    vg_data = table["temperature"]["vg"]

    # 1. Table data points (temperature table)
    plt.semilogx(vf_data, T_data, 'g*', label='Table data')
    plt.semilogx(vg_data, T_data, 'g*')

    # 2. Best-fit dome (fitting.py)
    v_dome, T_dome = dome_curve(T_data, vf_data, vg_data)
    plt.semilogx(v_dome, T_dome, 'b-', linewidth=2, label='Best fit (vapor dome)')

    # 3. Isobar for P1, drawn up to a bit above T1 or the critical point
    if T1 > table["T_crit"]:
        T_top = 1.15 * T1
    else:
        T_top = 1.15 * table["T_crit"]
    v_bar, T_bar = isobar_tv(table, P1, T_top)
    plt.semilogx(v_bar, T_bar, 'm-', label=f'Isobar P1 = {P1} {table["P_label"]}')

    # 4. The point (P1, T1)
    plt.semilogx(v1, T1, 'mo', markersize=9, label='(P1, T1)')

    # 5. Labels, state of water, legend
    plt.xlabel(f'Specific volume v [{table["v_label"]}]')
    plt.ylabel(f'Temperature T [{table["T_label"]}]')
    plt.title(f'T-v diagram:  {state_name}')
    plt.legend()
    plt.grid(True)


def show_plots(table, P1, T1, state_name):
    """Create both plots side by side and show them."""
    v1 = specific_volume(table, P1, T1, state_name)

    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)
    plot_pv(table, P1, T1, v1, state_name)

    plt.subplot(1, 2, 2)
    plot_tv(table, P1, T1, v1, state_name)

    plt.show()
