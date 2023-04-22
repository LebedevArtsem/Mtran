class PolishNode:
    def __init__(self, value):
        self.left = None
        self.right = None
        self.value = value


class PolishTree:
    variables = {}
    constants = []

    def __init__(self, variables, constants):
        self.variables = variables
        self.constants = constants

    def precedence(self, operator):
        if operator == '+' or operator == '-':
            return 1
        elif operator == '*' or operator == '/':
            return 2
        elif operator == "%":
            return 3
        elif operator == "^":
            return 4
        else:
            return 0

    def infix_to_postfix(self, expression):
        stack = []
        result = []
        open_quote = 0
        close_quote = 0
        isNumber = True

        for char in expression:
            a = char.token
            if char.token.isdigit() or char.token in self.variables or char.token in self.constants:
                result.append(char)
                if not isNumber:
                    return "error"
                else:
                    isNumber = False
            elif char.token == '(':
                open_quote += 1
                stack.append(char)
            elif char.token == ')':
                while stack and stack[-1].token != '(':
                    result.append(stack.pop())
                open_quote -= 1
                if open_quote >= 0:
                    stack.pop()  # удалить скобку "("
                else:
                    return "error"
            else:
                while stack and stack[-1].token != '(' and self.precedence(char.token) <= self.precedence(stack[-1].token):
                    result.append(stack.pop())
                stack.append(char)
                isNumber = True

        while stack:
            result.append(stack.pop())

        return result

    def construct_tree(self, polynomial):
        stack = []
        for char in polynomial:
            if char.token.isdigit() or char.token in self.variables or char.token in self.constants:
                node = PolishNode(char)
                stack.append(node)
            else:
                node = PolishNode(char)
                node.left = stack.pop()
                node.right = stack.pop()
                stack.append(node)
        return stack.pop()

    def tree_to_postfix(self, nodes):
        stack = []
        result = []
        for node in nodes:
            if node.depth == 0:
                continue
            while stack and stack[-1].depth >= node.depth:
                result.append(stack.pop().value.token)
            if node.value.token in ['+', '-']:
                if stack and stack[-1].depth >= node.depth:
                    while stack and stack[-1].value.token in ['*', '/']:
                        result.append(stack.pop().value)
            stack.append(node)
        while stack:
            result.append(stack.pop().value.token)
        return ' '.join(result)

    def postfix_to_infix(self, postfix):
        stack = []
        for token in postfix.split():
            if token in ['+', '-', '*', '/']:
                b = stack.pop()
                a = stack.pop()
                stack.append('({} {} {})'.format(a, token, b))
            else:
                stack.append(token)
        return stack.pop()
