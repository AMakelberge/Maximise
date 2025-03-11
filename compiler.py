import subprocess
import re

def maxima_to_latex(expression):
    try:
        maxima_code = f'string(tex({expression})); quit();'
        print("Running Maxima command:", maxima_code)

        result = subprocess.run(
            ["maxima", "--batch-string", maxima_code],
            capture_output=True, text=True
        )

        # Debugging: Print Maxima output
        print("Maxima stdout:", result.stdout)
        print("Maxima stderr:", result.stderr)

        if result.returncode != 0:
            return f"Error: Maxima exited with code {result.returncode}. stderr: {result.stderr}"

        # Try extracting the LaTeX output
        match = re.search(r"\$\$(.*?)\$\$", result.stdout, re.DOTALL)
        if match:
            return r"\[" + match.group(1).strip() + r"\]"
        else:
            return result.stdout.strip()
    except Exception as e:
        return f"Error processing LaTeX: {e}"

import re

class MaximaToLatex:
    def __init__(self):
        pass
    
    def convert(self, expr: str) -> str:
        expr = self.handle_fractions(expr)
        expr = self.handle_basic_operations(expr)
        expr = self.handle_exponents_and_subscripts(expr)
        expr = self.handle_square_roots(expr)
        expr = self.handle_trigonometry(expr)
        expr = self.handle_matrices(expr)
        expr = self.handle_calculus(expr)
        return expr
    
    def handle_basic_operations(self, expr: str) -> str:
        expr = expr.replace("*", " ")  # Remove explicit multiplication
        expr = re.sub(r'([^\s]+)/(?!/)([^\s]+)', r'\\frac{\1}{\2}', expr)  # Replace / with \frac
        return expr
    
    def handle_exponents_and_subscripts(self, expr: str) -> str:
        expr = re.sub(r'([a-zA-Z0-9]+)\^([a-zA-Z0-9]+)', r'\1^{\2}', expr)
        expr = re.sub(r'([a-zA-Z]+)_([a-zA-Z0-9]+)', r'\1_{\2}', expr)
        return expr
    
    def handle_fractions(self, expr: str) -> str:
        expr = re.sub(r'([0-9]+)\/([0-9]+)', r'\\frac{\1}{\2}', expr)
        return expr
    
    def handle_square_roots(self, expr: str) -> str:
        expr = re.sub(r'sqrt\((.*?)\)', r'\\sqrt{\g<1>}', expr)
        return expr
    
    def handle_trigonometry(self, expr: str) -> str:
        trig_functions = ['sin', 'cos', 'tan', 'sec', 'csc', 'cot']
        for func in trig_functions:
            expr = re.sub(rf'\b{func}\((.*?)\)', rf'\\{func}{{\g<1>}}', expr)
        return expr
    
    def handle_matrices(self, expr: str) -> str:
        expr = re.sub(r'\[\[(.*?)\]\]', lambda m: self.format_matrix(m.group(1)), expr)
        return expr
    
    def format_matrix(self, content: str) -> str:
        rows = content.split("], [")
        formatted_rows = [" & ".join(row.split(", ")) for row in rows]
        return "\\begin{bmatrix} " + " \\ ".join(formatted_rows) + " \\end{bmatrix}"
    
    def handle_calculus(self, expr: str) -> str:
        expr = re.sub(r'diff\((.*?), (.*?)\)', r'\\frac{d}{d\g<2>} \\left( \g<1> \\right)', expr)
        expr = re.sub(r'integrate\((.*?), (.*?)\)', r'\\int \g<1> \\, d\g<2>', expr)
        return expr

# Example Usage:
converter = MaximaToLatex()
maxima_expr = "x^3/(x+1)"
latex_output = converter.convert(maxima_expr)
print(latex_output)

