import math
import re

class RecurrenceRelation:
    def __init__(self, a_val, b_val, fn_val):
        self.a = a_val  # Number of subproblems
        self.b = b_val  # Division/decrease factor
        self.fn = fn_val  # Non-recursive part f(n)
        self.fn_type = -1  # Type of function (0: constant, 1: logarithmic, 2: polynomial, 3: exponential)
        self.log_power = 1.0  # Power of logarithm (for log^k(n))
        self.exp_base = 2.0  # Base of exponential (for k^n)
        self.determine_function_type()
    
    def determine_function_type(self):
        # Handle constant functions
        if self.fn in ["1", "c", "0"] or re.match(r"^\d+$", self.fn):
            self.fn_type = 0
        
        # Handle combined polynomial and logarithmic (e.g., n*log(n))
        elif "n" in self.fn and "log" in self.fn:
            self.fn_type = 2  # Treat as polynomial for Master Theorem cases
            
            # Check for log power in n*log^p(n)
            log_pos = self.fn.find("log")
            if log_pos != -1:
                power_pos = self.fn.find("^", log_pos)
                if power_pos != -1:
                    power_str = self.fn[power_pos + 1:]
                    end_pos = power_str.find("(")
                    if end_pos != -1:
                        power_str = power_str[:end_pos]
                    try:
                        self.log_power = float(power_str)
                    except:
                        self.log_power = 1.0
        
        # Handle logarithmic functions (log^p(n))
        elif "log" in self.fn:
            self.fn_type = 1
            # Check for log^2(n) or similar
            if "^" in self.fn:
                power_pos = self.fn.find("^")
                if power_pos != -1 and power_pos > 0:
                    # Extract the power value
                    power_str = self.fn[power_pos + 1:]
                    end_pos = power_str.find("(")
                    if end_pos != -1:
                        power_str = power_str[:end_pos]
                    try:
                        self.log_power = float(power_str)
                    except:
                        self.log_power = 1.0
        
        # Handle polynomial functions (n^k)
        elif "n^" in self.fn or ("n" in self.fn and "^" not in self.fn):
            self.fn_type = 2
        
        # Handle exponential functions (k^n)
        elif "^n" in self.fn or "2^" in self.fn or "e^" in self.fn:
            self.fn_type = 3
            # Extract the base of the exponential
            if "2^" in self.fn:
                self.exp_base = 2.0
            elif "e^" in self.fn:
                self.exp_base = math.e
            else:
                base_pos = self.fn.find("^")
                if base_pos != -1 and base_pos > 0:
                    base_str = self.fn[:base_pos]
                    try:
                        self.exp_base = float(base_str)
                    except:
                        self.exp_base = 2.0
        
        else:
            self.fn_type = 0  # Default to constant if no pattern is matched
    
    def get_polynomial_exponent(self):
        if self.fn_type != 2:
            return 0.0
        
        # For n*log^p(n) format
        if "n" in self.fn and "log" in self.fn:
            return 1.0  # The polynomial part is usually n^1
        
        pos = self.fn.find("^")
        if pos != -1:
            exp_str = self.fn[pos + 1:]
            try:
                return float(exp_str)
            except:
                return 1.0
        
        if "n" in self.fn:
            return 1.0
        
        return 0.0
    
    def solve(self, notation="Θ"):
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def get_recurrence_equation(self):
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def get_method_name(self):
        raise NotImplementedError("This method should be implemented by subclasses")


class DividingFunctionRecurrence(RecurrenceRelation):
    def __init__(self, a_val, b_val, fn_val, diff_sizes=False, b_prime_val=0):
        super().__init__(a_val, b_val, fn_val)
        self.diff_sizes = diff_sizes  # Whether subproblems have different sizes
        self.b_prime = b_prime_val  # Second division factor (if differentSizes is true)
    
    def get_recurrence_equation(self):
        if self.diff_sizes:
            return f"T(n) = T(n/{self.b}) + T(n/{self.b_prime}) + {self.fn}"
        else:
            return f"T(n) = {self.a}T(n/{self.b}) + {self.fn}"
    
    def get_method_name(self):
        if self.diff_sizes:
            return "Approximation Method"
        else:
            log_a_b = math.log(self.a) / math.log(self.b)
            k = self.get_polynomial_exponent()
            b_power_k = self.b ** k
            
            # Use the exact Master Theorem case
            if abs(self.a - b_power_k) < 0.0001:
                if self.log_power > -1:
                    return "Master Theorem (Case 2a)"
                elif abs(self.log_power - (-1)) < 0.0001:
                    return "Master Theorem (Case 2b)"
                else:
                    return "Master Theorem (Case 2c)"
            elif self.a > b_power_k:
                return "Master Theorem (Case 1)"
            elif self.a < b_power_k:
                if self.log_power >= 0:
                    return "Master Theorem (Case 3a)"
                else:
                    return "Master Theorem (Case 3b)"
            elif self.fn_type == 3:
                return "Extended Master Theorem"
            
            return "Advanced Master Theorem"
    
    def apply_master_theorem(self, notation):
        log_a_b = math.log(self.a) / math.log(self.b)
        k = self.get_polynomial_exponent()  # This is k in n^k
        p = self.log_power  # This is p in log^p(n)
        b_power_k = self.b ** k
        
        # Case 1: a > b^k
        if self.a > b_power_k:
            return f"{notation}(n^{log_a_b:.2f})"
        # Case 2: a = b^k
        elif abs(self.a - b_power_k) < 0.0001:
            if p > -1:
                # Case 2(a): p > -1
                return f"{notation}(n^{log_a_b:.2f} * log^{p+1:.2f}n)"
            elif abs(p - (-1)) < 0.0001:
                # Case 2(b): p = -1
                return f"{notation}(n^{log_a_b:.2f} * log log n)"
            else:
                # Case 2(c): p < -1
                return f"{notation}(n^{log_a_b:.2f})"
        # Case 3: a < b^k
        else:
            if p >= 0:
                # Case 3(a): p >= 0
                return f"{notation}(n^{k:.2f} * log^{p:.2f}n)"
            else:
                # Case 3(b): p < 0
                return f"{notation}(n^{k:.2f})"
    
    def apply_extended_master_theorem(self, notation):
        log_a_b = math.log(self.a) / math.log(self.b)
        
        if self.fn_type == 3:
            if self.exp_base > 1.0:
                return f"{notation}({self.exp_base:.2f}^n)"
        
        if self.fn_type == 1:
            if self.log_power > 1.0:
                return f"{notation}(n^{log_a_b:.2f} * log^{self.log_power:.2f} n)"
            return f"{notation}(n^{log_a_b:.2f} * log log n)"
        
        return self.apply_master_theorem(notation)
    
    def apply_approximation_method(self, notation):
        avg = (1.0/self.b + 1.0/self.b_prime) / 2.0
        eff_b = 1.0 / avg
        eff_a = 2.0
        log_a_b = math.log(eff_a) / math.log(eff_b)
        
        if self.fn_type == 0:
            return f"{notation}(n^{log_a_b:.2f})"
        elif self.fn_type == 2:
            exp = self.get_polynomial_exponent()
            
            if exp < log_a_b:
                return f"{notation}(n^{log_a_b:.2f})"
            elif abs(exp - log_a_b) < 0.0001:
                return f"{notation}(n^{log_a_b:.2f} * log n)"
            else:
                return f"{notation}(n^{exp:.2f})"
        elif self.fn_type == 1:
            if self.log_power > 1.0:
                return f"{notation}(n^{log_a_b:.2f} * log^{self.log_power:.2f} n)"
            return f"{notation}(n^{log_a_b:.2f} * log n)"
        elif self.fn_type == 3:
            return f"{notation}({self.exp_base:.2f}^n)"
        
        return f"{notation}(n^{log_a_b:.2f})"
    
    def solve(self, notation="Θ"):
        if self.diff_sizes:
            return self.apply_approximation_method(notation)
        else:
            if self.fn_type == 3 or "log log" in self.fn:
                return self.apply_extended_master_theorem(notation)
            else:
                return self.apply_master_theorem(notation)


class DecreasingFunctionRecurrence(RecurrenceRelation):
    def __init__(self, a_val, b_val, fn_val):
        super().__init__(a_val, b_val, fn_val)
    
    def get_recurrence_equation(self):
        return f"T(n) = {self.a}T(n-{self.b}) + {self.fn}"
    
    def get_method_name(self):
        if self.a == 1:
            return "Muster Theorem"
        else:
            return "Substitution Method"
    
    def apply_muster_theorem(self, notation):
        if self.a != 1:
            return f"Cannot apply Muster Theorem with a ≠ 1"
        
        if self.fn_type == 0:
            return f"{notation}(n)"
        elif self.fn_type == 2:
            exp = self.get_polynomial_exponent()
            return f"{notation}(n^{exp+1:.2f})"
        elif self.fn_type == 1:
            if self.log_power > 1.0:
                return f"{notation}(n * log^{self.log_power:.2f} n)"
            return f"{notation}(n log n)"
        elif self.fn_type == 3:
            return f"{notation}(n * {self.exp_base:.2f}^n)"
        
        return f"{notation}(n * {self.fn})"
    
    def apply_substitution_method(self, notation):
        # Fixed substitution method calculation
        if self.a < 1:
            return f"{notation}({self.fn})"
        
        if self.a == 1:
            return self.apply_muster_theorem(notation)
        
        # For a > 1 cases (recursive expansion)
        if self.a > 1:
            if self.fn_type == 0:  # Constant function
                # T(n) = aT(n-b) + c => T(n) = Θ(a^(n/b))
                return f"{notation}({self.a:.2f}^(n/{self.b:.2f}))"
            
            elif self.fn_type == 2:  # Polynomial function
                exp = self.get_polynomial_exponent()
                # Special case for n^k where a > 1
                # T(n) = aT(n-b) + n^k => T(n) = Θ(n^k * a^(n/b))
                return f"{notation}(n^{exp:.2f} * {self.a:.2f}^(n/{self.b:.2f}))"
            
            elif self.fn_type == 1:  # Logarithmic function
                # T(n) = aT(n-b) + log^k(n) => T(n) = Θ(log^k(n) * a^(n/b))
                if self.log_power > 1.0:
                    return f"{notation}(log^{self.log_power:.2f}(n) * {self.a:.2f}^(n/{self.b:.2f}))"
                return f"{notation}(log(n) * {self.a:.2f}^(n/{self.b:.2f}))"
            
            elif self.fn_type == 3:  # Exponential function
                # T(n) = aT(n-b) + k^n => T(n) = Θ((max(a, k^b))^(n/b))
                max_val = max(self.a, self.exp_base ** self.b)
                return f"{notation}({max_val:.2f}^(n/{self.b:.2f}))"
        
        # Default for unexpected cases
        return f"{notation}({self.a:.2f}^(n/{self.b:.2f}))"
    
    def solve(self, notation="Θ"):
        if self.a == 1:
            return self.apply_muster_theorem(notation)
        else:
            return self.apply_substitution_method(notation)


class RecurrenceSolver:
    def __init__(self):
        self.type = 0
        self.a = 0
        self.b = 0
        self.fn = ""
        self.diff_sizes = False
        self.b_prime = 0
        self.notation = "Θ"
    
    def display_intro(self):
        print("==================================================")
        print("          Recurrence Relation Solver             ")
        print("==================================================")
        print("This program solves recurrence relations of the form:")
        print("- Dividing function: T(n) = aT(n/b) + f(n)")
        print("- Decreasing function: T(n) = aT(n-b) + f(n)")
        print("==================================================")
        print("Just enter your full recurrence equation and select")
        print("the notation you want (Big O, Ω, or Θ)")
        print("==================================================")
    
    def parse_equation(self, equation):
        # Remove all whitespace
        equation = re.sub(r'\s+', '', equation)
        
        # Check if it's a dividing function
        if "t(n/" in equation.lower() or "t(n/" in equation.lower():
            self.type = 1
            # Check for different sizes
            if equation.lower().count("t(n/") == 2:
                self.diff_sizes = True
                # Extract both division factors
                parts = re.split(r'[+-]', equation.lower().split('+')[-1])
                self.fn = parts[-1]
                
                # Find all n/b patterns
                matches = re.findall(r't\(n/([^)]+)\)', equation.lower())
                if len(matches) >= 2:
                    self.b = float(matches[0])
                    self.b_prime = float(matches[1])
                self.a = 2  # For different size problems
            else:
                # Standard dividing function
                match = re.match(r't\(n\)=(\d+)t\(n/([^)]+)\)\+([^+]+)', equation.lower())
                if match:
                    self.a = float(match.group(1))
                    self.b = float(match.group(2))
                    self.fn = match.group(3)
                else:
                    # Handle case where coefficient might be omitted (assume 1)
                    match = re.match(r't\(n\)=t\(n/([^)]+)\)\+([^+]+)', equation.lower())
                    if match:
                        self.a = 1
                        self.b = float(match.group(1))
                        self.fn = match.group(2)
        else:
            # Assume decreasing function
            self.type = 2
            match = re.match(r't\(n\)=(\d+)t\(n-([^)]+)\)\+([^+]+)', equation.lower())
            if match:
                self.a = float(match.group(1))
                self.b = float(match.group(2))
                self.fn = match.group(3)
            else:
                # Handle case where coefficient might be omitted (assume 1)
                match = re.match(r't\(n\)=t\(n-([^)]+)\)\+([^+]+)', equation.lower())
                if match:
                    self.a = 1
                    self.b = float(match.group(1))
                    self.fn = match.group(2)
    
    def get_input(self):
        equation = input("\nEnter your recurrence relation (e.g., T(n)=2T(n/2)+n): ")
        self.parse_equation(equation)
        
        print("\nSelect notation:")
        print("1. Big O (Upper bound)")
        print("2. Big Ω (Lower bound)")
        print("3. Big Θ (Tight bound)")
        
        while True:
            choice = input("Enter choice (1-3): ")
            if choice == '1':
                self.notation = "O"
                break
            elif choice == '2':
                self.notation = "Ω"
                break
            elif choice == '3':
                self.notation = "Θ"
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
    
    def create_relation(self):
        if self.type == 1:
            return DividingFunctionRecurrence(self.a, self.b, self.fn, self.diff_sizes, self.b_prime)
        else:
            return DecreasingFunctionRecurrence(self.a, self.b, self.fn)
    
    def show_result(self, relation):
        print("\n==================================================")
        print("RESULT:")
        print(f"Recurrence equation: {relation.get_recurrence_equation()}")
        print(f"Method used: {relation.get_method_name()}")
        print(f"Solution: T(n) = {relation.solve(self.notation)}")
        print("==================================================")
    
    def run(self):
        self.display_intro()
        self.get_input()
        
        relation = self.create_relation()
        self.show_result(relation)


if __name__ == "__main__":
    solver = RecurrenceSolver()
    solver.run()