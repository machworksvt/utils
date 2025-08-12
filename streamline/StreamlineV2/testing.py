from sympy import solve, Eq, symbols, simplify

class EquationSet:
    def __init__(self):
        self.equations = []
        self.variables = set()

    def add_equation(self, lhs, rhs):
        eq = Eq(lhs, rhs)
        self.equations.append(eq)
        self.variables |= eq.free_symbols  # Add all symbols from equation

    def solve_all(self, target_vars=None):
        # Step 1: Optionally solve and substitute "easy" equations first
        knowns = {}

        # Find directly solvable equations (1 equation, 1 unknown)
        for eq in self.equations:
            syms = eq.free_symbols
            if len(syms) == 1:
                var = list(syms)[0]
                try:
                    sol = solve(eq, var)
                    if sol:
                        knowns[var] = simplify(sol[0])
                except:
                    continue

        # Step 2: Substitute into remaining equations
        substituted_eqs = []
        for eq in self.equations:
            substituted_eq = eq.subs(knowns)
            substituted_eqs.append(simplify(substituted_eq))

        # Step 3: Solve the simplified system
        target_vars = target_vars or list(self.variables)
        try:
            sol = solve(substituted_eqs, target_vars, dict=True)
        except Exception as e:
            print(f"Error solving system: {e}")
            return

        if not sol:
            print("No solution found.")
            return

        print("\nSymbolic Solutions:")
        for s in sol:
            for var, expr in s.items():
                print(f"  {var} = {simplify(expr)}")

        return sol

# Declare symbols
span, root_chord, tip_chord = symbols('span root_chord tip_chord')
sin_sweep, sin_back_sweep, taper = symbols('sin_sweep sin_back_sweep taper')
avg_chord, aspect_ratio, area = symbols('avg_chord aspect_ratio area')

eqset = EquationSet()
eqset.add_equation(span * sin_sweep + tip_chord - root_chord - span * sin_back_sweep, 0)
eqset.add_equation(avg_chord, (tip_chord + root_chord) / 2)
eqset.add_equation(aspect_ratio, span / avg_chord)
eqset.add_equation(area, span * avg_chord)
eqset.add_equation(taper, tip_chord / root_chord)

# Try solving everything
eqset.solve_all([root_chord])
