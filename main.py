import g
import os

from enum   import Enum
from typing import List, Set, Dict

"""
Notes for QBE

w/l/s/d         : Base-types
w (word)        : 32-bit integer
l (long)        : 64-bit integer
s (single)      : 32-bit floating point
d (double)      : 64-bit floating point

b/h             : Extended-types
b (byte)        : 8-bit integer
h (half-word)   : 16-bit integer
"""

NUMBER   = "NUMBER"
STRING   = "STRING"

ASSIGN   = "="
PLUS     = "+"
MINUS    = "-"
BANG     = "!"
ASTERISK = "*"
SLASH    = "/"
MODULUS  = "%"

class Type(Enum):
    pass

class Integer(Type):
    b = 8
    h = 16
    w = 32
    l = 64

class Float(Type):
    s = 32
    d = 64

class Token():
    def __init__(self, token_type:str, literal):
        self.type    = token_type
        self.literal = literal

def create_token(token_type:str, literal:str) -> Token:
    return Token(token_type, literal)

class Lexer():
    def __init__(self, r:str):
        self.r: str = r
        self.tokens: List[Token] = []

    def lex(self) -> None:
        for char in self.r:
            if char == " ": continue        # Ignore white spaces
            elif char == "\n": continue     # Ignore new lines
            elif char == "\t": continue     # Ignore tabs
            elif char == ASSIGN:  self.tokens.append(create_token(ASSIGN, "="))
            elif char == PLUS:  self.tokens.append(create_token(PLUS, "+"))
            elif char == MINUS: self.tokens.append(create_token(MINUS, "-"))
            elif char == BANG: self.tokens.append(create_token(BANG, "!"))
            elif char == ASTERISK: self.tokens.append(create_token(ASTERISK, "*"))
            elif char == SLASH: self.tokens.append(create_token(SLASH, "/"))
            elif char == MODULUS: self.tokens.append(create_token(MODULUS, "%"))
            elif char.isnumeric(): self.tokens.append(create_token(NUMBER, char))
            else:
                print(f"Lexer cannot parse this character : {char}, ignoring this.")

        return None

    def pretty_print(self) -> None:
        for i, token in enumerate(self.tokens):
            print("#", i, " | ", token.type, token.literal)
        return None

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

class Parser():
    def __init__(self, tokens:List[Token]):
        self.tokens: List[Token] = tokens
        self.asts: List[Ast] = []
        self.count = 0

    def parse(self) -> None:
        while (self.count != len(self.tokens)):
            self.asts.append(self.expr())
        return None

    def expr(self) -> Ast:
        return self.comparison()

    def comparison(self) -> Ast:
        expr = self.atomic()
        if self.tokens[self.count].type == PLUS:
            self.count+=1
            right = self.atomic()
            # TODO fix in future : quick hack: -2, cause self.count+=1 and self.atomic() is an addition
            return AstBinary(expr,
                             right,
                             self.tokens[self.count-2].literal)
        else:
            return self.atomic()

    def atomic(self) -> Ast:
        if self.tokens[self.count].type == NUMBER:
            ast_number = AstNumber(self.tokens[self.count].literal)
            self.count+=1
            return ast_number
        else:
            print("Reach atomic level parsing but found nothing")

def emit_function(name:str, t:Type) -> None:
    # For now just export all the functions
    g.ir += f"export function {t.name} ${name}()"
    return None

def emit_string(char:str) -> None:
    g.ir += f"{char}\n"
    return None

# emit_string with no new line
def emit_string_nl(char:str) -> None:
    g.ir += f"{char}"
    return None

def emit_start() -> None:
    emit_string("@start")
    return None

def emit_end() -> None:
    emit_string("@end")
    return None

def emit_loop() -> None:
    emit_string("loop")
    return None

def emit_empty_line() -> None:
    emit_string("")
    return None

# Just pass the data in by hand, instead of trying
# to make a generalized way to emit them
def emit_data(name:str, data:str) -> None:
    emit_string(f"data ${name}" +  " = {" +
            f"{data}" + "}")
    return None

def emit_binary(left, right, operator) -> None:
    return None

# Just emit directly to g.ir
def emit_asts(asts:List[Ast]):
    # For now, just wrap everything in one main function

    emit_data("builder1", "b \"%d\\n\", b 0")
    # functions don't exist as of now

    emit_empty_line()
    emit_function("main", Integer.w)
    emit_string("{")

    emit_start()

    for ast in asts:
        if type(ast) == AstBinary:
            if ast.operator == "+":
                emit_string(f"%x =w add {ast.left.number}, {ast.right.number}")
                emit_string("call $printf(l $builder1, w %x)")

    emit_end()

    emit_string("ret 0")
    emit_string("}")
    return None

def export_main() -> None:
    # Put all constant data at the top
    emit_data("fmt", "b \"Test!!\\n\", b 0")
    emit_data("test", "b \"Hello There\\n\", b 0")

    emit_empty_line()

    emit_function("main", Integer.w)
    emit_string("{")

    emit_start()
    emit_string("call $printf(l $fmt)")
    emit_string("call $printf(l $test)")
    emit_end()

    emit_string("ret 0")
    emit_string("}")

    return None

def main() -> None:
    export_main()
    print(g.ir)
    return None

if __name__ == '__main__':
    sample_text: str = """5 + 2"""

    lexer: Lexer = Lexer(sample_text)
    lexer.lex()
    # lexer.pretty_print()

    parser: Parser = Parser(lexer.tokens)
    parser.parse()

    emit_asts(parser.asts)
    print(g.ir)

    # Placeholder
    # main()
