class Ast():
    pass

class AstBinary(Ast):
    def __init__(self, left, right, operator):
        self.left = left
        self.right = right
        self.operator = operator

class AstNumber(Ast):
    def __init__(self, number):
        self.number = number

