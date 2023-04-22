import sys
from SyntaxManager import SyntaxManager
from PolishTree import PolishTree


class Node:
    value = ""
    depth = 0

    def __init__(self, value, depth):
        self.value = value
        self.depth = depth


class Parser:
    all_tokens = []
    variables = {}
    constants = {}
    variables_check_type = []
    syn = SyntaxManager
    declared_variables = []
    variable_types = syn.variable_types
    keywords = syn.keywords

    tree = []
    k = 0
    depth = 0
    is_cycle = False

    open_brace = 0
    close_brace = 0

    def __init__(self, all_tokens, variables, constants):
        self.all_tokens = all_tokens
        self.variables = variables
        self.constants = constants

    def add_to_tree(self, value):
        node = Node(value, self.depth)
        self.tree.append(node)

    def next_token(self):
        if self.k != len(self.all_tokens) - 1:
            self.k += 1

    def error(self, token, msg):
        print(f'Token {token.token} line {token.line} position {token.position} \nParser error:', msg)
        sys.exit(1)

    def parenthesis_expression(self, stop_symbol):
        if self.all_tokens[self.k].token != '(':
            self.error(self.all_tokens[self.k].token, '"(" expected')
        self.depth += 1
        self.add_to_tree(self.all_tokens[self.k])
        self.next_token()

        self.comparable_expression(stop_symbol)

        if self.all_tokens[self.k].token != ')':
            self.error(self.all_tokens[self.k], '")" expected')

        self.add_to_tree(self.all_tokens[self.k])
        self.next_token()
        return

    def block_statement(self):
        if self.all_tokens[self.k].token != '{':
            self.error(self.all_tokens[self.k], '"{" expected')
        self.open_brace += 1
        self.depth += 1
        self.add_to_tree(self.all_tokens[self.k])
        self.next_token()

        self.parse()

        if self.all_tokens[self.k].token != '}':
            self.error(self.all_tokens[self.k], '"}" expected')

        self.add_to_tree(self.all_tokens[self.k])
        self.depth -= 2
        self.next_token()
        return

    def if_statement(self):
        self.add_to_tree(self.all_tokens[self.k])

        self.next_token()

        self.parenthesis_expression(")")

        self.block_statement()

        if self.all_tokens[self.k].token == 'else':

            self.depth -= 1
            self.add_to_tree(self.all_tokens[self.k])

            self.next_token()

            if self.all_tokens[self.k].token == 'if':
                self.if_statement()
                self.next_token()  # not sure
            else:
                self.block_statement()

        return

    def while_statement(self):
        self.is_cycle = True
        self.add_to_tree(self.all_tokens[self.k])
        self.next_token()

        self.parenthesis_expression(")")

        self.block_statement()

        return

    def do_while_statement(self):
        self.is_cycle = True
        self.add_to_tree(self.all_tokens[self.k])
        self.next_token()

        self.block_statement()

        if self.all_tokens[self.k].token != 'while':
            self.error(self.all_tokens[self.k], '"while" expected')

        self.add_to_tree(self.all_tokens[self.k])
        self.next_token()
        self.parenthesis_expression(")")

        if self.all_tokens[self.k].token != ';':
            self.error(self.all_tokens[self.k], '";" expected')

        return

    def for_statement(self):
        self.is_cycle = True
        self.add_to_tree(self.all_tokens[self.k])
        self.next_token()

        self.depth += 1

        if self.all_tokens[self.k].token != '(':
            self.error(self.all_tokens[self.k], '"(" expected')

        self.add_to_tree(self.all_tokens[self.k])
        self.next_token()

        if self.all_tokens[self.k].token == 'int' or self.all_tokens[self.k].token == 'float':
            self.declaration()
        elif self.all_tokens[self.k].token in self.variables:
            self.declaration()
        else:
            self.error(self.all_tokens[self.k], 'variable expected')

        self.comparable_expression(";")

        self.next_token()

        if self.all_tokens[self.k].token in self.variables:
            self.add_to_tree(self.all_tokens[self.k])
            self.next_token()
        else:
            self.error(self.all_tokens[self.k], 'variable expected')

        if self.all_tokens[self.k].token == "++" or self.all_tokens[self.k].token == "--":
            self.add_to_tree(self.all_tokens[self.k])
            self.next_token()
        elif self.all_tokens[self.k].token in self.syn.initialization_operators:
            self.add_to_tree(self.all_tokens[self.k])
            self.next_token()
            self.depth += 1
            self.get_expression(")")
            self.k -= 1
            self.depth -= 1

        if self.all_tokens[self.k].token != ')':
            self.error(self.all_tokens[self.k], '")" expected')

        self.add_to_tree(self.all_tokens[self.k])

        self.next_token()

        self.block_statement()

        return

    def statement(self):
        if self.all_tokens[self.k].token == 'if':
            self.if_statement()

        elif self.all_tokens[self.k].token == 'while':
            self.while_statement()

        elif self.all_tokens[self.k].token == 'do':
            self.do_while_statement()

        elif self.all_tokens[self.k].token == 'for':
            self.for_statement()

        elif self.all_tokens[self.k].token == 'continue' or self.all_tokens[self.k].token == 'break':
            if self.is_cycle and (
                    self.all_tokens[self.k].token == 'continue' or self.all_tokens[self.k].token == 'break'):
                self.add_to_tree(self.all_tokens[self.k])
                self.next_token()

                if self.all_tokens[self.k].token != ';':
                    self.error(self.all_tokens[self.k], '";" expected')

            elif not self.is_cycle and (
                    self.all_tokens[self.k].token == 'continue' or self.all_tokens[self.k].token == 'break'):
                self.error(self.all_tokens[self.k], f'a {self.all_tokens[self.k]} can not be used without a loop')

        elif self.all_tokens[self.k].token == 'Console':

            self.add_to_tree(self.all_tokens[self.k])
            self.next_token()
            if self.all_tokens[self.k].token != '.':
                self.error(self.all_tokens[self.k], '"." expected')
            else:
                self.next_token()

            if self.all_tokens[self.k].token != 'WriteLine' and self.all_tokens[self.k].token != 'Write':
                self.error(self.all_tokens[self.k], 'function expected')
            else:
                self.add_to_tree(self.all_tokens[self.k])
                self.next_token()

            if self.all_tokens[self.k].token != '(':
                self.error(self.all_tokens[self.k], '"(" expected')
            else:
                self.depth += 1
                self.add_to_tree(self.all_tokens[self.k])

            self.next_token()

            if self.all_tokens[self.k].token == '$':
                self.add_to_tree(self.all_tokens[self.k])
                self.next_token()

            self.add_to_tree(self.all_tokens[self.k])
            self.next_token()

            if self.all_tokens[self.k].token == ";" and self.all_tokens[self.k].token not in self.variables:
                self.error(self.all_tokens[self.k], '")" expected')

            self.add_to_tree(self.all_tokens[self.k])
            self.depth -= 1
            self.next_token()

            if self.all_tokens[self.k].token != ';':
                self.error(self.all_tokens[self.k], '; expected')

        return

    def expression_statement(self):
        if self.all_tokens[self.k].token in self.syn.keywords:
            self.statement()

        elif self.all_tokens[self.k].token in self.syn.variable_types:
            self.declaration()

        elif self.all_tokens[self.k].token in self.variables:
            self.math_expression()

        elif self.all_tokens[self.k].token == ";":
            self.next_token()

        else:
            self.error(self.all_tokens[self.k], 'unknown error')

    def check_variable_is_declared(self):
        for i in self.declared_variables:
            if self.all_tokens[self.k].token == i.value.token:
                return True
        return False

    def math_expression(self):
        if self.all_tokens[self.k].token in self.variables:
            if not self.check_variable_is_declared():
                self.error(self.all_tokens[self.k], 'variable is not declared 282')
            self.variables_check_type.append(self.variables[self.all_tokens[self.k].token])
            self.add_to_tree(self.all_tokens[self.k])
            self.next_token()

        if self.all_tokens[self.k].token in self.syn.initialization_operators:
            if self.variables_check_type[0] == "string" and \
                    (self.all_tokens[self.k].token != "=" and self.all_tokens[self.k].token != "+="):
                self.error(self.all_tokens[self.k], 'unsupported operator')
            self.add_to_tree(self.all_tokens[self.k])
            self.next_token()
        elif self.all_tokens[self.k].token == "++" or self.all_tokens[self.k].token == "--":
            if self.variables_check_type[0] == "string":
                self.error(self.all_tokens[self.k], 'unsupported operator')
            self.add_to_tree(self.all_tokens[self.k])
            self.next_token()

            if not self.all_tokens[self.k].token == ";":
                self.error(self.all_tokens[self.k], '";" expected')

            return

        self.depth += 1

        self.get_expression()

        self.depth -= 1
        return

    def comparable_expression(self, stop_symbol):
        expression = []
        while self.all_tokens[self.k].token not in self.syn.comparison_operators:
            if self.all_tokens[self.k].token in self.variables \
                    and not self.check_variable_is_declared():
                self.error(self.all_tokens[self.k], 'variable is not declared 310')
            if self.all_tokens[self.k].token in self.variables or self.all_tokens[self.k].token in self.constants or \
                    self.all_tokens[self.k].token in self.syn.simple_arithmetic_operators:
                expression.append(self.all_tokens[self.k])
                self.next_token()
            else:
                self.error(self.all_tokens[self.k], 'comparable error')

        if not expression:
            self.error(self.all_tokens[self.k], 'constant or variable missed')

        polish = PolishTree(self.variables, self.constants)
        postfix = polish.infix_to_postfix(expression)
        if postfix == "error":
            self.error(self.all_tokens[self.k], 'logic error')
        root = polish.construct_tree(postfix)
        self.polish_to_tree(root)

        self.add_to_tree(self.all_tokens[self.k])  # add ==, <=...
        self.next_token()
        self.depth += 1
        expression = []
        while self.all_tokens[self.k].token != stop_symbol:
            if self.all_tokens[self.k].token in self.variables \
                    and not self.check_variable_is_declared():
                self.error(self.all_tokens[self.k], 'variable is not declared 332')
            if self.all_tokens[self.k].token in self.variables or self.all_tokens[self.k].token in self.constants or \
                    self.all_tokens[self.k].token in self.syn.simple_arithmetic_operators:
                expression.append(self.all_tokens[self.k])
                self.next_token()
            else:
                self.error(self.all_tokens[self.k], 'comparable error')

        if not expression:
            self.error(self.all_tokens[self.k], 'constant or variable missed')

        polish = PolishTree(self.variables, self.constants)
        postfix = polish.infix_to_postfix(expression)
        if postfix == "error":
            self.error(self.all_tokens[self.k], 'logic error')
        root = polish.construct_tree(postfix)
        self.polish_to_tree(root)
        self.depth -= 1
        return

    def polish_to_tree(self, node, level=0):
        if node is not None:
            self.polish_to_tree(node.right, level + 1)
            n = Node(node.value, self.depth + level)
            self.tree.append(n)
            self.polish_to_tree(node.left, level + 1)

    def declaration(self):
        self.variables_check_type.append(self.all_tokens[self.k].token)
        self.next_token()

        if self.all_tokens[self.k].token in self.variables:
            if not self.check_variable_is_declared():
                variable = Node(self.all_tokens[self.k], self.depth)
                self.declared_variables.append(variable)
            else:
                self.error(self.all_tokens[self.k], 'variable is already declared')
            self.add_to_tree(self.all_tokens[self.k])
            self.next_token()

        else:
            self.error(self.all_tokens[self.k], 'variable expected')

        if self.all_tokens[self.k].token == ",":
            self.next_token()
            while self.all_tokens[self.k].token != ";" and self.all_tokens[self.k].token != "=":
                if self.all_tokens[self.k].token in self.variables:
                    if not self.check_variable_is_declared():
                        variable = Node(self.all_tokens[self.k], self.depth)
                        self.declared_variables.append(variable)
                    else:
                        self.error(self.all_tokens[self.k], 'variable is already declared')
                    self.add_to_tree(self.all_tokens[self.k])
                    self.next_token()
                else:
                    self.error(self.all_tokens[self.k], 'variable expected')

        if self.all_tokens[self.k].token == ";":
            self.variables_check_type.clear()
            self.next_token()
            return

        if self.all_tokens[self.k].token != "=":
            self.error(self.all_tokens[self.k], '"=" expected')

        self.add_to_tree(self.all_tokens[self.k])
        self.next_token()
        self.depth += 1

        self.get_expression()

        self.depth -= 1
        return

    def get_expression(self, stop_symbol=";"):
        expression = []
        while True:
            if self.all_tokens[self.k].token == stop_symbol:
                break

            if self.all_tokens[self.k].token in self.variables and not self.check_variable_is_declared():
                self.error(self.all_tokens[self.k], 'variable is not declared 409')

            if self.all_tokens[self.k].token in self.variables:
                self.variables_check_type.append(self.variables[self.all_tokens[self.k].token])
            elif self.all_tokens[self.k].token in self.constants:
                self.variables_check_type.append(self.constants[self.all_tokens[self.k].token])
            elif self.all_tokens[self.k].token in self.syn.simple_arithmetic_operators:
                self.variables_check_type.append(self.all_tokens[self.k].token)
            elif self.all_tokens[self.k].token != ")" and self.all_tokens[self.k].token != "(":
                self.error(self.all_tokens[self.k], '";" missed 422')

            expression.append(self.all_tokens[self.k])
            self.next_token()

        if not expression:
            self.error(self.all_tokens[self.k], 'constant or variable missed')

        self.check_variables_same_type()

        polish = PolishTree(self.variables, self.constants)
        postfix = polish.infix_to_postfix(expression)
        if postfix == "error":
            self.error(self.all_tokens[self.k], 'logic error')
        root = polish.construct_tree(postfix)

        self.polish_to_tree(root)

        self.next_token()

        return

    def delete_variables(self):
        i = len(self.declared_variables) - 1
        while True:
            if self.declared_variables[i].depth >= self.depth:
                self.declared_variables.pop()
                i -= 1
            else:
                return

    def check_variables_same_type(self):
        type = self.variables_check_type[0]

        if type == "string":
            self.check_variables_string_type(type)
        elif type == "int":
            self.check_variables_int_type(type)
        elif type == "float":
            self.check_variables_float_type(type)
        else:
            self.error(self.all_tokens[self.k], 'unsupported yet types')

        self.variables_check_type.clear()
        return

    def check_variables_string_type(self, type):
        for i in self.variables_check_type:
            if i in self.syn.simple_arithmetic_operators and i != "+":
                self.error(self.all_tokens[self.k], 'unsupported operator')
            elif i != type and i != ")" and i != "(":
                self.error(self.all_tokens[self.k], 'missed types')
        return

    def check_variables_int_type(self, type):
        for i in self.variables_check_type:
            if i != type and i not in self.syn.simple_arithmetic_operators and i != ")" and i != "(":
                self.error(self.all_tokens[self.k], 'missed types')
        return

    def check_variables_float_type(self, type):
        for i in self.variables_check_type:
            if i != type and i != "int" and i not in self.syn.simple_arithmetic_operators and i != ")" and i != "(":
                self.error(self.all_tokens[self.k], 'missed types')
        return

    def parse(self):
        while self.k != len(self.all_tokens) - 1:

            if self.all_tokens[self.k].token == "}":
                if self.open_brace == 0:
                    self.error(self.all_tokens[self.k], 'wrong "}"')
                else:
                    self.open_brace -= 1
                    self.delete_variables()
                return

            self.expression_statement()

        return self.tree
