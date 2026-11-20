# Project Thermo State

Draws the vapor dome of water on a **p–v** and a **T–v** diagram.

At start-up the user enters a pressure p₁ and a temperature T₁ for water. The program then

1. plots the saturated-water table data points and a best-fit curve through them (the vapor dome),
2. draws the isotherm for T₁ on the p–v plot and the isobar for p₁ on the T–v plot,
3. marks the point (p₁, T₁) and displays the state of the water.

![Project sketch](docs/project_sketch.png)

## Setup

Requires Python 3.9+.

```
git clone https://github.com/<your-username>/thermo-state.git
cd thermo-state
pip install -r requirements.txt
python main.py
```

Run the tests with `python -m pytest`.

## Project layout

| File | What goes in it | Owner |
|---|---|---|
| `main.py` | User input and the overall steps | |
| `thermo_state/data.py` | Load the CSV tables; Tsat(p) and psat(T) | |
| `thermo_state/fitting.py` | Curve-fitting methods from class | |
| `thermo_state/state.py` | State of water at (p₁, T₁) | |
| `thermo_state/curves.py` | Isotherm and isobar | |
| `thermo_state/plotting.py` | The two plots | |
| `data/` | Saturated water table as CSV (Moran, Tables A-2/A-3) | |
| `tests/` | Automated checks | |

Run everything from this folder (the one with `main.py`): the CSV paths are relative to it.

### Methods (all from ME 318M lectures)
- **Table look-ups:** linear interpolation (Week 2)
- **Vapor dome:** piecewise least-squares quadratic fits of ln(v) (Weeks 9–10), with a quadratic "cap" at the critical point
- **Superheated vapor:** ideal-gas estimate starting from vg, `v = vg(P) · T_abs / Tsat_abs(P)`
- **Compressed liquid:** `v ≈ vf(T)`
- **Plots:** `plt.subplot` + semilog-x axes (Week 5)

## Data

Everything is in SI units: T in °C, P in bar, v in m³/kg.
`data/sat_water_SI.csv` holds the temperature table (A-2) and the pressure table (A-3);
the `table` column says which one a row is from.
`vf` in the SI file is in m³/kg (the book prints vf × 10³). Values are as printed in
the book.

## Working together

- Make a branch for each task: `git checkout -b fitting`
- Commit, push (`git push -u origin fitting`), and open a Pull Request on GitHub.
- A teammate reviews, then merges. Before starting new work: `git checkout main` and `git pull`.
