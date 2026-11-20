"""Curve fitting for the "best fit" vapor dome.

Lecture concepts used:
    Quadratic least-squares fit by solving A x = b (Week 9, lecture_wk9_2.py)
    Linearizing with ln() before fitting (Week 10, exponential/power fits)
    While loops, lists, array slicing (Weeks 3-4)

WHY PIECEWISE?
    One fit over the whole table doesn't work: v goes from 0.001 to 206 m³/kg,
    and every single linear/quadratic/exponential/power fit misses some table
    points by more than 100%. So we split the table into short runs of
    consecutive points (5 by default) and do a quadratic fit on each run.
    Neighboring pieces share their end point, so the pieces join up.

WHY A SEPARATE "CAP" AT THE TOP?
    At the critical point the dome turns over: going up the liquid side, v
    keeps growing while T (or P) levels off. A fit of v as a function of T
    can't make that turn, so it wobbles. Near the top we flip the fit around
    and fit T (or P) as a quadratic in ln(v), using the last table point on
    EACH side plus the critical point. The top of the dome looks like an
    upside-down parabola, which is exactly what a quadratic is good at.
    (With 3 points the quadratic goes exactly through them. I tried 5 points,
    cap_points=2, and it missed the 360 °C liquid point, because the top of
    the dome is lopsided.)

WHY ln(v)?
    Same trick as the Week 10 exponential fit: fit ln(v) instead of v, then
    take exp() of the result. v changes by orders of magnitude, and ln(v)
    is much smoother, so a quadratic follows it much better.
"""
import numpy as np


def quadratic_fit(x, y):
    """Least-squares quadratic y = a x² + b x + c (same steps as lecture_wk9_2.py)."""
    n = len(x)

    # Summations
    x4_sum = np.sum(x**4)
    x3_sum = np.sum(x**3)
    x2_sum = np.sum(x**2)
    x_sum = np.sum(x)
    x2y_sum = np.sum(x**2 * y)
    xy_sum = np.sum(x * y)
    y_sum = np.sum(y)

    # A matrix and b vector
    Amat = np.array([
        [x4_sum, x3_sum, x2_sum],
        [x3_sum, x2_sum, x_sum],
        [x2_sum, x_sum, n],
    ])
    b_vec = np.array([x2y_sum, xy_sum, y_sum])

    # Solve for a, b, c
    coeffs = np.linalg.solve(Amat, b_vec)
    return coeffs[0], coeffs[1], coeffs[2]


def fit_curve(x, v, points_per_piece=5):
    """Piecewise quadratic fit of ln(v) against x.

    x: pressures (for the p-v dome) or temperatures (for the T-v dome)
    v: vf or vg values from the same table rows

    Returns the "model": a list of pieces, each piece is
        [x_start, x_end, a, b, c]   meaning   ln(v) = a x² + b x + c   on that range
    """
    ln_v = np.log(v)
    n = len(x)
    pieces = []

    start = 0
    while start < n - 1:
        end = start + points_per_piece - 1      # index of the last point in this piece
        if end > n - 1:                          # don't run past the end of the table
            end = n - 1

        # Always fit with points_per_piece points (the last piece borrows
        # some earlier points so it still has enough to fit a quadratic).
        first = end - points_per_piece + 1
        if first < 0:
            first = 0

        a, b, c = quadratic_fit(x[first:end + 1], ln_v[first:end + 1])
        pieces.append([x[start], x[end], a, b, c])

        start = end                              # next piece starts where this one ended

    return pieces


def evaluate_curve(model, x_new):
    """Evaluate the fitted model at one value x_new. Returns v."""
    for piece in model:
        x_start = piece[0]
        x_end = piece[1]
        if x_new >= x_start and x_new <= x_end:
            a = piece[2]
            b = piece[3]
            c = piece[4]
            return np.exp(a * x_new**2 + b * x_new + c)

    print(f"{x_new} is outside the fitted range")
    exit()


def curve_points(model, points_per_piece=30):
    """Return smooth x and v arrays along the whole fitted curve (for plotting)."""
    x_list = []
    v_list = []
    for piece in model:
        x_values = np.linspace(piece[0], piece[1], points_per_piece)
        for x in x_values:
            x_list.append(x)
            v_list.append(evaluate_curve(model, x))
    return np.array(x_list), np.array(v_list)


def dome_curve(x, vf, vg, cap_points=1):
    """Smooth curve for the whole vapor dome, ready to plot.

    x:  pressures (p-v dome) or temperatures (T-v dome) from one table,
        smallest to largest, with the critical point as the last row
    vf, vg: the matching saturated-liquid and saturated-vapor volumes
    cap_points: how many points below the critical point (on each side)
        go into the cap fit

    Returns v_dome, x_dome: the dome traced from the bottom of the liquid
    side, over the top, and down the vapor side.
    """
    n = len(x)
    split = n - 1 - cap_points        # index where the sides end and the cap starts

    # ---- 1. The two sides: piecewise fits of ln(v) against x ----
    liquid_model = fit_curve(x[:split + 1], vf[:split + 1])
    vapor_model = fit_curve(x[:split + 1], vg[:split + 1])
    x_liquid, v_liquid = curve_points(liquid_model)
    x_vapor, v_vapor = curve_points(vapor_model)

    # ---- 2. The cap: x as a quadratic in ln(v), using points from both sides ----
    ln_v_cap = []
    x_cap = []
    for i in range(split, n):          # liquid side, going up to the critical point
        ln_v_cap.append(np.log(vf[i]))
        x_cap.append(x[i])
    for i in range(split, n - 1):      # vapor side (critical point already added)
        ln_v_cap.append(np.log(vg[i]))
        x_cap.append(x[i])
    a, b, c = quadratic_fit(np.array(ln_v_cap), np.array(x_cap))

    # Evaluate the cap from where the liquid side ends to where the vapor side ends
    ln_v_values = np.linspace(np.log(v_liquid[-1]), np.log(v_vapor[-1]), 60)
    v_top = np.exp(ln_v_values)
    x_top = a * ln_v_values**2 + b * ln_v_values + c

    # ---- 3. Join: liquid side (bottom -> top), cap, vapor side (top -> bottom) ----
    v_list = []
    x_list = []
    for i in range(len(v_liquid)):
        v_list.append(v_liquid[i])
        x_list.append(x_liquid[i])
    for i in range(len(v_top)):
        v_list.append(v_top[i])
        x_list.append(x_top[i])
    for i in range(len(v_vapor) - 1, -1, -1):      # backwards: top -> bottom
        v_list.append(v_vapor[i])
        x_list.append(x_vapor[i])

    return np.array(v_list), np.array(x_list)
