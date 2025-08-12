from sympy import symbols, Eq, solve

# Declare all symbols
span, root_chord, tip_chord = symbols('span root_chord tip_chord')
sin_sweep, sin_back_sweep, taper = symbols('sin_sweep sin_back_sweep taper')
avg_chord, aspect_ratio, area = symbols('avg_chord aspect_ratio area')

# Define equations
eq1 = Eq(span * sin_sweep + tip_chord - root_chord - span * sin_back_sweep, 0)  # sweep geometry
eq2 = Eq(avg_chord, (tip_chord + root_chord) / 2)  # average chord
eq3 = Eq(aspect_ratio, span / avg_chord)  # aspect ratio
eq4 = Eq(area, span*avg_chord)  # aspect ratio
eq5 = Eq(taper, tip_chord/root_chord)  # aspect ratio


# Solve system of equations
# solutions = solve([eq1, eq2, eq3, eq4, eq5], [sin_back_sweep, avg_chord, aspect_ratio, area, taper], dict=True)

solutions = solve([eq1, eq2, eq3, eq4, eq5], [aspect_ratio, span , taper, root_chord, tip_chord], dict=True)

# Print result
print(solutions)