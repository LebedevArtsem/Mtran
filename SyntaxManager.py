class SyntaxManager:
    variable_types = [
        "int",
        "float",
        "string",
        "char",
        "double",
        "long",
        "short",
        "bool"
    ]
    keywords = [
        "if",
        "else",
        "for",
        "while",
        "do",
        "continue",
        "break",
        "Console",
        "WriteLine",
        "Write"
    ]
    separators = [
        "(",
        ")",
        ",",
        ";",
        "{",
        "}",
        ".",
        "$"
    ]
    arithmetic_operators = [
        "+",
        "-",
        "*",
        "/",
        "%",
        "++",
        "--",
        "+=",
        "-=",
        "*=",
        "/=",
        "%="
    ]

    initialization_operators = [
        "+=",
        "-=",
        "*=",
        "/=",
        "%=",
        "="
    ]

    comparison_operators = [
        "==",
        "!=",
        "<=",
        ">=",
        "<",
        ">"
    ]
    simple_arithmetic_operators = [
        "+",
        "-",
        "*",
        "/",
        "%",
        "^"
    ]

    def get_keywords(self):
        all_keywords = self.keywords + self.variable_types
        return all_keywords
