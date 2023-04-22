from prettytable import PrettyTable
from Parser import Parser
from SyntaxManager import SyntaxManager
from Translator import Translator

class Token:
    token = ""
    position = 0
    line = 0

    def __init__(self, token, position, line):
        self.line = line
        self.token = token
        self.position = position


syn = SyntaxManager()

keywords = syn.get_keywords()

simple_arithmetic_operators = syn.simple_arithmetic_operators

comparison_operators = syn.comparison_operators

arithmetic_operators = syn.arithmetic_operators

separators = syn.separators

state = 1

f = open("input.txt")
text = f.read()

i = 0
pos = 0
lexema = ""
type = ""
line = 1
error_message = ""

keyword_table = PrettyTable()
variable_table = PrettyTable()
separator_table = PrettyTable()
operator_table = PrettyTable()
constant_table = PrettyTable()
keyword_table.field_names = ["Keyword", "Description"]
variable_table.field_names = ["Variable", "Description"]
separator_table.field_names = ["Separator", "Description"]
operator_table.field_names = ["Operator", "Description"]
constant_table.field_names = ["Constant", "Description"]
is_float = False
variables = {}
constants = {}
all_tokens = []


def add_to_token(lexema):
    global pos
    global line

    token = Token(lexema, pos, line)
    all_tokens.append(token)


def counter():
    global i
    global pos

    pos += 1
    i += 1


def state_reading_file():
    global state
    global type
    global line
    global pos
    global lexema
    global is_float

    if i == len(text):
        state = 10
    elif text[i] == ' ' or text[i] == '\n':
        if (text[i] == '\n'):
            type = ""
            line += 1
            pos = 0
        counter()
    elif text[i] == '.':
        lexema = '.'
        state = 6
    elif text[i].isalpha():
        lexema = ""
        lexema += text[i]
        counter()
        state = 8
    elif text[i].isdigit():
        is_float = False
        lexema = ""
        lexema += text[i]
        counter()
        state = 2
    elif text[i] == "!" or text[i] == "=" or text[i] == "<" or text[i] == ">" or text[i] in simple_arithmetic_operators:
        lexema = ""
        lexema += text[i]
        counter()
        state = 3
    elif text[i] == "$":
        state = 5
    elif text[i] == '"':
        lexema = ""
        lexema += text[i]
        counter()
        state = 4
    else:
        state = 7


def state_number():
    global lexema
    global state
    global is_float
    global error_message

    if i != len(text) and text[i].isdigit():
        lexema += text[i]
        counter()
    elif i != len(text) and text[i] == ".":
        if (is_float == True):
            error_message = "incorrect value"
            state = 9
        is_float = True
        lexema += text[i]
        counter()
    elif i != len(text) and text[i].isalpha():
        lexema += text[i]
        error_message = "incorrect value"
        state = 9
    else:
        word = constant_table.get_string()
        sublex = " " + lexema + " "
        if sublex not in word:
            if is_float:
                constant_table.add_row([lexema, "float"])
                constants[lexema] = "float"
            else:
                constant_table.add_row([lexema, "int"])
                constants[lexema] = "int"
        add_to_token(lexema)
        lexema = ""
        state = 1


def state_operator():
    global lexema
    global state
    global error_message

    if i != len(text) and (text[i] == "!" or text[i] == "=" or text[i] == "<" or text[i] == ">" or text[
        i] in simple_arithmetic_operators):
        lexema += text[i]
        counter()
    else:
        sublex = " " + lexema + " "
        word = operator_table.get_string()
        if sublex not in word:
            if lexema == "=":
                operator_table.add_row([lexema, "assignment"])
            elif lexema in comparison_operators:
                operator_table.add_row([lexema, "comparison"])
            elif lexema in arithmetic_operators:
                operator_table.add_row([lexema, "arithmetical"])
            else:
                error_message = "incorrect operator"
                state = 9
                return
        add_to_token(lexema)
        lexema = ""
        state = 1


def state_string():
    global state
    global lexema
    global error_message

    if i != len(text) and text[i] != '"' and text[i] != "\n":
        lexema += text[i]
        counter()
    else:
        if i != len(text) and text[i] == "\"":
            lexema += text[i]
            constant_table.add_row([lexema, "string"])
            constants[lexema] = "string"
            add_to_token(lexema)
            lexema = ""
            state = 1
            counter()
        else:
            error_message = "missing closing quote"
            state = 9


def state_variable_string():
    global state
    global error_message

    if text[i] == "$":
        separator_table.add_row((["$", "separator"]))
        add_to_token("$")
        counter()
    if text[i] != '"':
        error_message = "missing quote"
        state = 9
    else:
        open_quote = 0
        close_quote = 0
        open_bracket = 0
        close_bracket = 0
        for j in range(i, len(text)):
            if text[j] == "{":
                open_bracket += 1
            if text[j] == "}":
                close_bracket += 1
            if text[j] == '"':
                if open_quote == 0:
                    open_quote += 1
                else:
                    close_quote += 1
                    break
        if open_bracket != close_bracket:
            error_message = "unvaluable string"
            state = 9
        elif close_quote == 0:
            error_message = "unvaluable string"
            state = 9
        else:
            state = 1


def state_dot():
    global lexema
    global state

    separator_table.add_row(([lexema, "separator"]))
    add_to_token(lexema)
    lexema = ''
    counter()
    state = 1


def state_separator():
    global lexema
    global state
    global type
    global error_message

    lexema = ""
    lexema += text[i]
    if lexema in separators:
        if (lexema == ";"):
            type = ""
        word = separator_table.get_string()

        if lexema not in word:
            separator_table.add_row([lexema, "separator"])
        add_to_token(lexema)
        lexema = ""
        state = 1
        counter()
    else:
        error_message = "unsupported token"
        state = 9


def state_main():
    global lexema
    global state
    global error_message
    global type
    global variables

    if i != len(text) and (text[i].isalpha() or text[i].isdigit() or text[i] == "_"):
        lexema += text[i]
        counter()
    else:
        if lexema in keywords:
            word = keyword_table.get_string()
            sublex = " " + lexema + " "
            if sublex not in word:
                keyword_table.add_row([lexema, "keyword"])
            if lexema == "int" or lexema == "float" or lexema == "string":
                type = lexema
        else:
            if lexema not in variables:
                variables[lexema] = type
            word = variable_table.get_string()
            sublex = " " + lexema + " "
            if sublex not in word:
                variable_table.add_row([lexema, f"{variables.get(lexema)}"])
        add_to_token(lexema)
        lexema = ""
        state = 1


def state_error():
    print(f"line: {line}, pos: {pos}. {error_message}: {lexema}")


def state_end():
    print(keyword_table)
    print(variable_table)
    print(separator_table)
    print(operator_table)
    print(constant_table)


state_dictionary = {
    1: state_reading_file,
    2: state_number,
    3: state_operator,
    4: state_string,
    5: state_variable_string,
    6: state_dot,
    7: state_separator,
    8: state_main,
    9: state_error,
    10: state_end,
}


def print_tree(tree):
    for i in tree:
        print(" " * 4 * i.depth, i.value.token)


if __name__ == '__main__':

    state = 1
    while state != 9 and state != 10:
        state_dictionary[state]()

    state_dictionary[state]()
    parser = Parser(all_tokens, variables, constants)
    # print(constants)
    if all_tokens:
        ast_tree = parser.parse()

        print_tree(ast_tree)

        tranlator = Translator(ast_tree, variables)
        if ast_tree:
            tranlator.translate()
            tranlator.execute()
