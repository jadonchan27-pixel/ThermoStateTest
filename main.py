"""Project Thermo State: draw the vapor dome of water for a given p and T.

Run from this folder with:  python main.py

Lecture concepts used: input/float (Week 1), while loops that re-prompt on
bad input (Week 3, midterm 1 review), functions (Week 4).
"""
from thermo_state.data import load_table
from thermo_state.state import find_state
from thermo_state.plotting import show_plots


def ask_units():
    """Ask for SI or English units; keep asking until the answer is valid."""
    answer = input("Which unit system? (SI/English): ").strip().lower()
    while answer != "si" and answer != "english":
        answer = input('Invalid input. Enter "SI" or "English": ').strip().lower()

    if answer == "si":
        return "SI"
    else:
        return "English"


def main():
    # 1. Units, then load the matching table
    units = ask_units()
    table = load_table(units)

    P_min = table["temperature"]["P"][0]   # lowest pressure in either table
    P_crit = table["P_crit"]
    T_min = table["temperature"]["T"][0]

    # 2. Pressure: must be inside the pressure table and below the critical point
    #    (above P_crit there is no dome, so no Tsat to compare with)
    P1 = float(input(f"Enter a pressure P1 [{table['P_label']}] ({P_min} to {P_crit}): "))
    while P1 < P_min or P1 >= P_crit:
        P1 = float(input(f"Invalid. P1 must be from {P_min} up to (not including) {P_crit}: "))

    # 3. Temperature: can't be below the lowest table temperature
    T1 = float(input(f"Enter a temperature T1 [{table['T_label']}] (at least {T_min}): "))
    while T1 < T_min:
        T1 = float(input(f"Invalid. T1 must be at least {T_min}: "))

    # 4. Find the state of the water
    state_name = find_state(table, P1, T1)
    print("State of water:", state_name)

    # 5. Draw the p-v and T-v plots
    show_plots(table, P1, T1, state_name)


if __name__ == "__main__":
    main()
