from SyntaxManager import SyntaxManager
from PolishTree import PolishTree


class Translator:
    tree = []
    k = 0
    code = ''
    line = 0
    temp_depth = 0
    syn = SyntaxManager()
    variables = {}

    def __init__(self, tree, variables):
        self.tree = tree
        self.variables = variables

    def next_token(self):
        if self.k != len(self.tree) - 1:
            self.k += 1

    def parenthesis_expression(self):
        self.next_token()  # skip (

        while self.tree[self.k].value.token != ")":
            self.code += f"{self.tree[self.k].value.token} "
            self.next_token()

        self.code += ":\n"

        self.next_token()  # skip )
        return

    def expression_statement(self):
        if self.tree[self.k].value.token in self.syn.keywords:
            self.statement()

        elif self.tree[self.k].value.token in self.variables:
            result = self.math_expression()
            tab = (self.tree[self.k].depth - self.temp_depth) * '\t'
            self.code += f"{tab}{result}"

    def statement(self):
        if self.tree[self.k].value.token == 'if':
            self.if_statement()

        elif self.tree[self.k].value.token == 'while':
            self.while_statement()

        elif self.tree[self.k].value.token == 'do':
            self.do_while_statement()

        elif self.tree[self.k].value.token == 'for':
            self.for_statement()

        elif self.tree[self.k].value.token == 'continue' or self.tree[self.k].value.token == 'break':
            tab = (self.tree[self.k].depth - self.temp_depth) * '\t'
            self.code += f"{tab}{self.tree[self.k].value.token} \n"
            self.next_token()
            return

        elif self.tree[self.k].value.token == 'Console':
            end = False
            self.next_token()
            tab = (self.tree[self.k].depth - self.temp_depth) * '\t'
            self.code += f"{tab}print("
            if self.tree[self.k].value.token == "WriteLine":
                end = False
            elif self.tree[self.k].value.token == "Write":
                end = True

            self.next_token()  # skip Write(line?)
            self.next_token()  # skip (

            if self.tree[self.k].value.token == '$':
                self.code += "f"
                self.next_token()

            while self.tree[self.k].value.token != ")":
                self.code += self.tree[self.k].value.token
                self.next_token()
            if end:
                self.code += ", end = \"\")\n"
            else:
                self.code += ")\n"

            self.next_token()  # skip )
        return

    def if_statement(self):
        # self.add_to_code(self.tree[self.k].token, self.tree[self.k].depth)

        tab = (self.tree[self.k].depth - self.temp_depth) * '\t'
        self.code += f"{tab}{self.tree[self.k].value.token} "

        self.next_token()

        self.parenthesis_expression()

        self.translate()

        if self.tree[self.k].value.token == 'else':
            self.code += "else:\n"

            self.next_token()
            self.translate()

        return

    def while_statement(self):
        tab = (self.tree[self.k].depth - self.temp_depth) * '\t'
        self.code += f"{tab}{self.tree[self.k].value.token} "

        self.next_token()  # skip while

        self.parenthesis_expression()

        self.translate()

        return

    def for_statement(self):
        tab = (self.tree[self.k].depth - self.temp_depth) * '\t'

        self.next_token()  # skip for

        first_range = ""
        second_range = []
        third_range = ""

        self.next_token()  # skip (
        variable = self.tree[self.k].value.token
        self.next_token()
        first_range = self.get_expression()

        self.code += f"{tab}{variable}{first_range}\n"
        self.code += f"{tab}while "

        comparison = self.tree[self.k].value.token
        self.next_token()  # skip i
        equal_symbol_depth = self.tree[self.k].depth
        comparison += self.tree[self.k].value.token
        self.next_token()  # skip <=...

        while equal_symbol_depth < self.tree[self.k].depth:
            second_range.append(self.tree[self.k])
            self.next_token()

        polish = PolishTree([], [])
        postfix = polish.tree_to_postfix(second_range)
        comparison += polish.postfix_to_infix(postfix)

        self.code += f"{comparison}:\n"

        third_range = self.math_expression()

        self.next_token()

        self.translate()

        tab = (self.tree[self.k - 1].depth - self.temp_depth - 1) * '\t'
        self.code += f"{tab}{third_range}"

        # self.next_token()  # skip }
        return

    def math_expression(self):
        variable = self.tree[self.k].value.token
        self.next_token()
        expression = ""
        if self.tree[self.k].value.token in self.syn.initialization_operators:
            expression += self.get_expression() + "\n"
        elif self.tree[self.k].value.token == "++":
            expression = "+=1\n"
            self.next_token()
        elif self.tree[self.k].value.token == "--":
            expression = "-=1\n"
            self.next_token()
        else:
            expression = "= ''\n"

        result = f"{variable}{expression}"

        return result

    def get_expression(self):
        equal_symbol_depth = self.tree[self.k].depth
        result = f"{self.tree[self.k].value.token}"
        self.next_token()
        expression = []
        while equal_symbol_depth < self.tree[self.k].depth:
            expression.append(self.tree[self.k])
            self.next_token()

        polish = PolishTree([], [])
        postfix = polish.tree_to_postfix(expression)
        result += polish.postfix_to_infix(postfix)

        return result

    def translate(self):
        while self.k != len(self.tree) - 1:
            if self.tree[self.k].value.token == "{":
                self.next_token()
                self.temp_depth += 1
            elif self.tree[self.k].value.token == "}":
                self.next_token()
                self.temp_depth -= 1
                return
            else:
                self.expression_statement()

        return

    def execute(self):
        print("Execute file")
        exec(self.code)
