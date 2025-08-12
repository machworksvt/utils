
import numpy as np
import Scripts.tools as tl

import sympy as sp
from sympy import solve

def wrap_to_90(angle_deg):
    angle = ((angle_deg + 90) % 180) - 90
    return angle 
def eps():
    return 1E-5

class EquationSet:
    def __init__(self, equations, known_vars):
        # equations: list of strings like "a + b = c"
        self.known_vars = list(known_vars)
        self.equations = []
        self.all_vars = set()

        for eq_str in equations:
            lhs_str, rhs_str = map(str.strip, eq_str.split('='))
            lhs = sp.sympify(lhs_str)
            rhs = sp.sympify(rhs_str)
            eq = sp.Eq(lhs, rhs)
            self.equations.append(eq)
            self.all_vars.update(lhs.free_symbols)
            self.all_vars.update(rhs.free_symbols)

        self.all_vars = sorted(self.all_vars, key=lambda s: s.name)
        self.known_syms = [sp.Symbol(k) for k in self.known_vars]
        self.unknown_syms = [v for v in self.all_vars if v.name not in self.known_vars]

        tl.sprint(
            f"Making equation set. Knowns: ({', '.join(str(s) for s in self.known_syms)}), "
            f"Unknowns: ({', '.join(str(s) for s in self.unknown_syms)}). Attempting solve...",
            3,
            lead_func=True
        )


        # Try to solve the system
        self.solutions = solve(self.equations, self.unknown_syms, dict=True)
        if not self.solutions:
            tl.sprint("No solution found for given equations and known variables.", -1, lead_func=True)
        if len(self.solutions) > 1:
            tl.sprint(f"Multiple solution branches not yet supported: {self.solutions}", -1, lead_func=True)

        tl.sprint(f"Succeeded!", 3, lead_func=True)

        self.lambdas = {}
        sol_dict = self.solutions[0]
        for unk_sym in self.unknown_syms:
            if unk_sym in sol_dict:
                self.lambdas[unk_sym.name] = sp.lambdify(self.known_syms, sol_dict[unk_sym], modules='numpy')

        self.eq_var_names = {v.name for v in self.all_vars}
        self.unknown_vars = set(self.known_vars) - self.eq_var_names

    def evaluate(self, known_values):
        """
        known_values: dict mapping variable name to value
        Returns: dict mapping unknown variable names to their evaluated numeric values
        """
        tl.sprint(f"Subsituiting into equation set with: {known_values}", 3, lead_func=True)
        try:
            args = [known_values[k] for k in self.known_vars]
        except KeyError as e:
            tl.sprint(f"Missing value for known variable: {e}", -1, lead_func=True)

        # Compute values for the unknowns
        solved_values = {
            name: func(*args)
            for name, func in self.lambdas.items()
        }

        # Merge with known values
        return {**known_values, **solved_values}
    
