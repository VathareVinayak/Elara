import ast
import operator as op
import math
import sympy as sp
import re

# Supported operators
operators = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: op.neg
}

# Safely evaluate math expressions without using eval().
def safe_eval(expr):

    def eval_node(node):
        if isinstance(node, ast.Num):  # <number>
            return node.n
        elif isinstance(node, ast.BinOp):  # operator
            left = eval_node(node.left)
            right = eval_node(node.right)
            return operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):  # unary minus
            operand = eval_node(node.operand)
            return operators[type(node.op)](operand)
        else:
            raise TypeError(f"Unsupported expression: {node}")
    node = ast.parse(expr, mode='eval').body
    return eval_node(node)

# Solve algebraic equations
def solve_equation(expression: str) -> str:
    try:
        # Better regex pattern that handles spaces and complex equations
        equation_match = re.search(r'(.+?)\s*=\s*(.+)', expression)
        if not equation_match:
            # Try alternative pattern for equations without spaces around '='
            equation_match = re.search(r'([^=]+)=([^=]+)', expression)
        
        if not equation_match:
            return "Please provide an equation with '=' sign. Example: 'solve x^2 - 4 = 0'"
        
        lhs, rhs = equation_match.groups()
        
        x = sp.symbols('x')
        equation = sp.Eq(sp.sympify(lhs.strip()), sp.sympify(rhs.strip()))
        solutions = sp.solve(equation, x)
        
        if solutions:
            return f"Equation: {equation}\nSolutions: {solutions}"
        else:
            return "No solution found."
            
    except Exception as e:
        return f"Error: {str(e)}. Try: 'solve x^2 - 4 = 0'"

# Calculate derivatives    
def calculate_derivative(expression: str) -> str:
    try:
        if "derivative of" in expression.lower():
            expr_str = expression.lower().split("derivative of")[-1].strip()
        elif "differentiate" in expression.lower():
            expr_str = expression.lower().split("differentiate")[-1].strip()
        else:
            expr_str = expression
        
        expr_str = re.sub(r'[^\w\s\+\-\*\/\^\(\)\.]', '', expr_str)
        
        x = sp.symbols('x')
        expr = sp.sympify(expr_str)
        
        derivative = sp.diff(expr, x)
        
        return f"Derivative of: \n {expr} is: \n {derivative}"
        
    except Exception as e:
        return f"Error While calculating derivative:\n {str(e)}. \n  Try this type of queries : 'derivative of x^2'"

# Calculate trigonometric functions and solve trig equations
def solve_trigonometry(expression: str) -> str:
    try:
        trig_match = re.search(r'(sin|cos|tan|csc|sec|cot)\(([^)]+)\)', expression.lower())
        
        if trig_match:
            func, arg = trig_match.groups()
            x = sp.symbols('x')
            
            if 'degree' in arg or '°' in arg:
                arg_num = float(re.search(r'[\d\.]+', arg).group())
                arg_rad = sp.rad(arg_num)
            else:
                arg_num = float(re.search(r'[\d\.]+', arg).group()) if re.search(r'[\d\.]+', arg) else x
                arg_rad = arg_num if isinstance(arg_num, (int, float)) else x
            
            if func == 'sin':
                result = sp.sin(arg_rad)
            elif func == 'cos':
                result = sp.cos(arg_rad)
            elif func == 'tan':
                result = sp.tan(arg_rad)
            elif func == 'csc':
                result = sp.csc(arg_rad)
            elif func == 'sec':
                result = sp.sec(arg_rad)
            elif func == 'cot':
                result = sp.cot(arg_rad)
            else:
                return "Unsupported trigonometric function."
            
            if isinstance(arg_num, (int, float)):
                numerical_result = float(result.evalf())
                return f"{func}({arg_num}) = {numerical_result}"
            else:
                return f"{func}({arg}) = {result}"
        
        elif '=' in expression:
            return solve_equation(expression)
        
        else:
            return "Try: 'sin(30 degrees)' or 'solve sin(x) = 0.5'"
            
    except Exception as e:
        return f"Error In Tool trigonometry with your equation: \n {str(e)}. \n You Can Try Below Some Equation For Better Response: \n 'sin(30)' \n 'cos(45 degrees)'"

# Main expression evaluator
def calculate(expression: str) -> str:
    clean_expr = expression.strip()
    
    # Treat any '=' with a variable as an equation even if no keywords
    if '=' in clean_expr and re.search(r'[a-zA-Z]', clean_expr):
        return solve_equation(clean_expr)
    
    elif re.search(r'derivative|differentiate|d/dx', clean_expr.lower()):
        return calculate_derivative(clean_expr)
    
    elif re.search(r'sin|cos|tan|trig|angle', clean_expr.lower()):
        return solve_trigonometry(clean_expr)
    
    else:
        try:
            allowed_names = {}
            for name, value in math.__dict__.items():
                if not name.startswith("__"):
                    allowed_names[name] = value
            
            result = eval(expression, {"__builtins__": None}, allowed_names)
            return str(result)
        except Exception as e:
            return f"Error For Evaluating Expressions : {e}"
