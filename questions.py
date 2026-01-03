questions = {
    'Python': {
        'section1': [  # Questions 1-20 (First Section)
            ("Question 1: Who developed Python?", 
             [("A", "Guido van Rossum"), ("B", "James Gosling"), ("C", "Dennis Ritchie"), ("D", "Bjarne Stroustrup")], 
             "A"),

            ("Question 2: Python is named after:", 
             [("A", "A species of snake"), ("B", "Monty Python's Flying Circus (British comedy series)"), ("C", "The Greek letter π (pi)"), ("D", "A mathematical concept")], 
             "B"),

            ("Question 3: Which of the following is NOT a key characteristic of Python mentioned in the notes?", 
             [("A", "Interpreted"), ("B", "Interactive"), ("C", "Compiled"), ("D", "Object-Oriented")], 
             "C"),

            ("Question 4: How do you display the full Zen of Python in the Python shell?", 
             [("A", "print(zen)"), ("B", "import this"), ("C", "from zen import *"), ("D", "zen()")], 
             "B"),

            ("Question 5: What was the release year of Python 3.0?", 
             [("A", "2000"), ("B", "2006"), ("C", "2008"), ("D", "2010")], 
             "C"),

            ("Question 6: What is the code to print \"Hello World\" in Python?", 
             [("A", "echo \"Hello World\""), ("B", "printf(\"Hello World\")"), ("C", "print(\"Hello World\")"), ("D", "System.out.println(\"Hello World\")")], 
             "C"),

            ("Question 7: Which of the following is a popular application area where Python is widely used according to the notes?", 
             [("A", "Low-level system programming"), ("B", "Data Science and Machine Learning"), ("C", "Operating system kernel development"), ("D", "Real-time embedded firmware")], 
             "B"),

            ("Question 8: In Python, how are code blocks defined?", 
             [("A", "Using curly braces {}"), ("B", "Using indentation (spaces or tabs)"), ("C", "Using semicolons ;"), ("D", "Using parentheses ()")], 
             "B"),

            ("Question 9: How do you denote a private variable in a Python class (by convention)?", 
             [("A", "_variable"), ("B", "__variable"), ("C", "variable_"), ("D", "$variable")], 
             "B"),

            ("Question 10: Which built-in function is used to convert a string like \"123\" to an integer?", 
             [("A", "float()"), ("B", "str()"), ("C", "int()"), ("D", "complex()")], 
             "C"),

            ("Question 11: Which of the following is the correct way to write an octal integer literal in Python?", 
             [("A", "034"), ("B", "0o34"), ("C", "0x34"), ("D", "#34")], 
             "B"),

            ("Question 12: What is the value of the hexadecimal literal 0x1C in decimal?", 
             [("A", "16"), ("B", "24"), ("C", "28"), ("D", "34")], 
             "C"),

            ("Question 13: Which literal represents a complex number?", 
             [("A", "10.5"), ("B", "\"Hello\""), ("C", "2 + 3j"), ("D", "[1, 2, 3]")], 
             "C"),

            ("Question 14: How are multi-line string literals defined in Python?", 
             [("A", "Using single quotes ' '"), ("B", "Using double quotes \" \" "), ("C", "Using triple quotes ''' or \"\"\""), ("D", "Using parentheses ( )")], 
             "C"),

            ("Question 15: What is the type of the literal (1, \"Ravi\", 75.50, True)?", 
             [("A", "list"), ("B", "dict"), ("C", "tuple"), ("D", "set")], 
             "C"),

            ("Question 16: Which built-in function converts a string \"10.5\" to a float?", 
             [("A", "int()"), ("B", "str()"), ("C", "float()"), ("D", "complex()")], 
             "C"),

            ("Question 17: In Python classes, how is a private variable conventionally defined?", 
             [("A", "_var (protected)"), ("B", "__var (private with name mangling)"), ("C", "var (public)"), ("D", "#var")], 
             "B"),

            ("Question 18: What is the recommended way to create a Python virtual environment (as per modern practice)?", 
             [("A", "python -m virtualenv .venv"), ("B", "python -m venv .venv"), ("C", "pip install venv"), ("D", "virtualenv create .venv")], 
             "B"),

            ("Question 19: What is the current stable version of Python as of January 2026?", 
             [("A", "Python 3.12"), ("B", "Python 3.13"), ("C", "Python 3.14"), ("D", "Python 3.15")], 
             "C"),

            ("Question 20: Which encoding is the default for Python 3 source code and strings?", 
             [("A", "ASCII"), ("B", "UTF-16"), ("C", "UTF-8"), ("D", "Latin-1")], 
             "C"),
        ],
        
        'section2': [  # Questions 21-100 (Second Section)
            ("Question 21: Which operator is used for floor division in Python?", 
             [("A", "/"), ("B", "//"), ("C", "%"), ("D", "**")], 
             "B"),

            ("Question 22: What is the result of 10 % 3 in Python?", 
             [("A", "3"), ("B", "1"), ("C", "0"), ("D", "3.333")], 
             "B"),

            ("Question 23: Which operator has higher precedence: addition or multiplication?", 
             [("A", "Addition"), ("B", "Multiplication"), ("C", "They have the same precedence"), ("D", "It depends on associativity")], 
             "B"),

            ("Question 24: What does the '==' operator check?", 
             [("A", "Assignment"), ("B", "Equality"), ("C", "Identity"), ("D", "Membership")], 
             "B"),

            ("Question 25: Which operator is used for identity comparison?", 
             [("A", "=="), ("B", "!="), ("C", "is"), ("D", "in")], 
             "C"),

            ("Question 26: What is the result of True and False?", 
             [("A", "True"), ("B", "False"), ("C", "None"), ("D", "Error")], 
             "B"),

            ("Question 27: What does 'a in list' check?", 
             [("A", "Identity"), ("B", "Membership"), ("C", "Equality"), ("D", "Assignment")], 
             "B"),

            ("Question 28: Which assignment operator is equivalent to a = a + b?", 
             [("A", "-="), ("B", "+="), ("C", "*="), ("D", "/=")], 
             "B"),

            ("Question 29: What is the precedence order: ** or * ?", 
             [("A", "** higher"), ("B", "* higher"), ("C", "Same"), ("D", "Depends")], 
             "A"),

            ("Question 30: What is the output of 2 ** 3 ** 2?", 
             [("A", "512"), ("B", "64"), ("C", "81"), ("D", "16")], 
             "A"),

            ("Question 31: Which operator has left-to-right associativity?", 
             [("A", "**"), ("B", "+"), ("C", "="), ("D", "is")], 
             "B"),

            ("Question 32: What does ~ operator do?", 
             [("A", "Bitwise NOT"), ("B", "Logical NOT"), ("C", "Negation"), ("D", "Complement")], 
             "A"),

            ("Question 33: What is 5 & 3 in binary?", 
             [("A", "1"), ("B", "5"), ("C", "3"), ("D", "7")], 
             "A"),

            ("Question 34: What is the result of not (True or False)?", 
             [("A", "True"), ("B", "False"), ("C", "None"), ("D", "Error")], 
             "B"),

            ("Question 35: Which operator is used for chaining comparisons?", 
             [("A", "and"), ("B", "or"), ("C", "in"), ("D", "Python allows a < b < c")], 
             "D"),

            ("Question 36: What is the type of result from 10 / 2?", 
             [("A", "int"), ("B", "float"), ("C", "complex"), ("D", "str")], 
             "B"),

            ("Question 37: What does a **= b do?", 
             [("A", "Exponent and assign"), ("B", "Multiply and assign"), ("C", "Add and assign"), ("D", "Divide and assign")], 
             "A"),

            ("Question 38: Which operator has lowest precedence?", 
             [("A", "**"), ("B", "or"), ("C", "*"), ("D", "+")], 
             "B"),

            ("Question 39: What is the output of 'a' in 'apple'?", 
             [("A", "True"), ("B", "False"), ("C", "Error"), ("D", "None")], 
             "A"),

            ("Question 40: What does id(a) == id(b) check?", 
             [("A", "Equality"), ("B", "Identity"), ("C", "Membership"), ("D", "Value")], 
             "B"),

            ("Question 41: Which is unary operator?", 
             [("A", "+"), ("B", "=="), ("C", "in"), ("D", "and")], 
             "A"),

            ("Question 42: What is 9 // 2?", 
             [("A", "4.5"), ("B", "4"), ("C", "5"), ("D", "Error")], 
             "B"),

            ("Question 43: What does ^ operator do?", 
             [("A", "XOR"), ("B", "OR"), ("C", "AND"), ("D", "NOT")], 
             "A"),

            ("Question 44: What is the result of [] is []?", 
             [("A", "True"), ("B", "False"), ("C", "Error"), ("D", "None")], 
             "B"),

            ("Question 45: Which operator is short-circuit?", 
             [("A", "&"), ("B", "and"), ("C", "*"), ("D", "**")], 
             "B"),

            ("Question 46: What is precedence of 'not' vs 'and'?", 
             [("A", "not higher"), ("B", "and higher"), ("C", "Same"), ("D", "Depends")], 
             "A"),

            ("Question 47: What is 1 << 2?", 
             [("A", "2"), ("B", "4"), ("C", "1"), ("D", "3")], 
             "B"),

            ("Question 48: What does //= do?", 
             [("A", "Floor divide and assign"), ("B", "Mod and assign"), ("C", "Exponent assign"), ("D", "Bitwise assign")], 
             "A"),

            ("Question 49: Which is membership operator?", 
             [("A", "is"), ("B", "in"), ("C", "=="), ("D", "not")], 
             "B"),

            ("Question 50: What is output of 10 == 10.0?", 
             [("A", "False"), ("B", "True"), ("C", "Error"), ("D", "None")], 
             "B"),

            ("Question 51: What does ~5 give?", 
             [("A", "-6"), ("B", "5"), ("C", "-5"), ("D", "Error")], 
             "A"),

            ("Question 52: Which has right-to-left associativity?", 
             [("A", "+"), ("B", "**"), ("C", "*"), ("D", "/")], 
             "B"),

            ("Question 53: What is 'a' not in 'abc'?", 
             [("A", "True"), ("B", "False"), ("C", "Error"), ("D", "None")], 
             "B"),

            ("Question 54: What is precedence of bitwise & vs +?", 
             [("A", "& higher"), ("B", "+ higher"), ("C", "Same"), ("D", "Bitwise higher than +")], 
             "A"),

            ("Question 55: What is result of False or 0?", 
             [("A", "False"), ("B", "0"), ("C", "True"), ("D", "None")], 
             "B"),

            ("Question 56: Which operator for dictionary membership?", 
             [("A", "in (keys)"), ("B", "=="), ("C", "is"), ("D", "not")], 
             "A"),

            ("Question 57: What is 2 + 3 * 4?", 
             [("A", "20"), ("B", "14"), ("C", "11"), ("D", "12")], 
             "B"),

            ("Question 58: What does a is not b check?", 
             [("A", "Not equal"), ("B", "Different objects"), ("C", "Not member"), ("D", "Logical not")], 
             "B"),

            ("Question 59: What is the output of 7 % -3?", 
             [("A", "1"), ("B", "-1"), ("C", "2"), ("D", "-2")], 
             "A"),

            ("Question 60: Which operator is used for matrix multiplication?", 
             [("A", "*"), ("B", "@"), ("C", "**"), ("D", "//")], 
             "B"),

            ("Question 61: What is the precedence of comparison vs logical and?", 
             [("A", "Comparison higher"), ("B", "and higher"), ("C", "Same"), ("D", "Logical lower")], 
             "A"),

            ("Question 62: What does - -5 evaluate to?", 
             [("A", "-5"), ("B", "5"), ("C", "Error"), ("D", "10")], 
             "B"),

            ("Question 63: What is 0 or [] or 'hi'?", 
             [("A", "0"), ("B", "[]"), ("C", "'hi'"), ("D", "False")], 
             "C"),

            ("Question 64: Which is not a bitwise operator?", 
             [("A", "<<"), ("B", ">>"), ("C", "//"), ("D", "^")], 
             "C"),

            ("Question 65: What is the result of 'a' == 'A'?", 
             [("A", "True"), ("B", "False"), ("C", "Error"), ("D", "None")], 
             "B"),

            ("Question 66: What does += do for strings?", 
             [("A", "Concatenate"), ("B", "Repeat"), ("C", "Error"), ("D", "Add")], 
             "A"),

            ("Question 67: What is precedence of lambda?", 
             [("A", "Highest"), ("B", "Lowest"), ("C", "After or"), ("D", "Before assignment")], 
             "B"),

            ("Question 68: What is ~ -1?", 
             [("A", "0"), ("B", "-2"), ("C", "1"), ("D", "Error")], 
             "A"),

            ("Question 69: What is 1j ** 2?", 
             [("A", "-1"), ("B", "1j"), ("C", "1"), ("D", "Error")], 
             "A"),

            ("Question 70: Which operator cannot be used with complex numbers?", 
             [("A", "+"), ("B", "*"), ("C", "%"), ("D", "/")], 
             "C"),

            ("Question 71: What is the output of 10 > 5 == True?", 
             [("A", "True"), ("B", "False"), ("C", "Error"), ("D", "1")], 
             "B"),

            ("Question 72: What does 'not in' check?", 
             [("A", "Absence in sequence"), ("B", "Not equal"), ("C", "Identity"), ("D", "Logical")], 
             "A"),

            ("Question 73: What is precedence of walrus := ?", 
             [("A", "Assignment level"), ("B", "Highest"), ("C", "Lowest"), ("D", "After lambda")], 
             "A"),

            ("Question 74: What is -9 // 2 ?", 
             [("A", "-5"), ("B", "-4"), ("C", "4"), ("D", "-4.5")], 
             "A"),

            ("Question 75: What does a & b do for integers?", 
             [("A", "Bitwise AND"), ("B", "Logical AND"), ("C", "Set intersection"), ("D", "All")], 
             "A"),

            ("Question 76: What is 0.1 + 0.2 == 0.3?", 
             [("A", "True"), ("B", "False"), ("C", "Error"), ("D", "Approx")], 
             "B"),

            ("Question 77: Which is ternary operator in Python?", 
             [("A", "if else"), ("B", "? :"), ("C", "and or"), ("D", "No ternary")], 
             "A"),

            ("Question 78: What is the associativity of = ?", 
             [("A", "Left to right"), ("B", "Right to left"), ("C", "None"), ("D", "Top to bottom")], 
             "B"),

            ("Question 79: What is output of [1] == (1,)?", 
             [("A", "True"), ("B", "False"), ("C", "Error"), ("D", "None")], 
             "B"),

            ("Question 80: What does ** have precedence over?", 
             [("A", "Unary -"), ("B", "*"), ("C", "+"), ("D", "All lower")], 
             "D"),

            ("Question 81: What is 2 << 1?", 
             [("A", "1"), ("B", "4"), ("C", "2"), ("D", "3")], 
             "B"),

            ("Question 82: What is the result of True + 1?", 
             [("A", "True"), ("B", "2"), ("C", "1"), ("D", "Error")], 
             "B"),

            ("Question 83: Which operator is used for dict value equality comparison?", 
             [("A", "=="), ("B", ">"), ("C", "is"), ("D", "in")], 
             "A"),

            ("Question 84: What is ~0?", 
             [("A", "-1"), ("B", "0"), ("C", "1"), ("D", "-0")], 
             "A"),

            ("Question 85: What is 5 | 3?", 
             [("A", "5"), ("B", "7"), ("C", "1"), ("D", "0")], 
             "B"),

            ("Question 86: What is 10 ^ 3?", 
             [("A", "9"), ("B", "1"), ("C", "13"), ("D", "30")], 
             "A"),

            ("Question 87: What is associativity of comparisons?", 
             [("A", "Left to right"), ("B", "Chained"), ("C", "Right"), ("D", "None")], 
             "B"),

            ("Question 88: What is output of bool([])?", 
             [("A", "True"), ("B", "False"), ("C", "Error"), ("D", "None")], 
             "B"),

            ("Question 89: What is 3 ** 2 ** 3?", 
             [("A", "729"), ("B", "27"), ("C", "81"), ("D", "512")], 
             "A"),

            ("Question 90: Which is not a logical operator?", 
             [("A", "and"), ("B", "or"), ("C", "not"), ("D", "xor")], 
             "D"),

            ("Question 91: What is precedence of if-else expression?", 
             [("A", "Lowest"), ("B", "High"), ("C", "After lambda"), ("D", "Assignment")], 
             "A"),

            ("Question 92: What does a %= b do?", 
             [("A", "Mod assign"), ("B", "Divide assign"), ("C", "Exp assign"), ("D", "Bit assign")], 
             "A"),

            ("Question 93: What is -10 % 3?", 
             [("A", "2"), ("B", "-2"), ("C", "1"), ("D", "-1")], 
             "A"),

            ("Question 94: What is output of 1 == 1.0 is True?", 
             [("A", "True"), ("B", "False"), ("C", "Error"), ("D", "1")], 
             "B"),

            ("Question 95: Which operator is used for unpacking?", 
             [("A", "*"), ("B", "**"), ("C", "Both"), ("D", "None")], 
             "C"),

            ("Question 96: What is precedence of @ (matrix multiplication)?", 
             [("A", "Same as *"), ("B", "Higher than *"), ("C", "Lower"), ("D", "None")], 
             "A"),

            ("Question 97: What is ~True?", 
             [("A", "-2"), ("B", "-1"), ("C", "False"), ("D", "Error")], 
             "A"),

            ("Question 98: What is the lowest precedence operator group?", 
             [("A", "lambda"), ("B", "or"), ("C", ":="), ("D", "if else")], 
             "D"),

            ("Question 99: What is the result of 1 > 2 > 3?", 
             [("A", "True"), ("B", "False"), ("C", "Error"), ("D", "None")], 
             "B"),

            ("Question 100: In Python, which of the following is evaluated first in 2 + 3 * 4 ** 2?", 
             [("A", "+"), ("B", "*"), ("C", "**"), ("D", "All same")], 
             "C"),
        ],
        'section1_author': None,  # Will be set to admin username who created section 1
        'section2_author': None,  # Will be set to admin username who created section 2
    },
    'JavaScript': {
        'section1': [],
        'section2': [],
        'section1_author': None,
        'section2_author': None
    },
    'SQL': {
        'section1': [],
        'section2': [],
        'section1_author': None,
        'section2_author': None
    },
    'Git': {
        'section1': [],
        'section2': [],
        'section1_author': None,
        'section2_author': None
    },
    'CSS and HTML': {
        'section1': [],
        'section2': [],
        'section1_author': None,
        'section2_author': None
    }
}

# Helper function for backward compatibility
def get_all_questions(category):
    """Returns all questions for a category (section1 + section2) for backward compatibility"""
    if category not in questions:
        return []
    data = questions[category]
    if isinstance(data, list):  # Old format
        return data
    return data['section1'] + data['section2']

def get_section_questions(category, section):
    """Get questions for specific section"""
    if category not in questions or section not in ['section1', 'section2']:
        return []
    return questions[category][section]

def get_section_author(category, section):
    """Get author of specific section"""
    if category not in questions:
        return None
    return questions[category].get(f'{section}_author')