import g
import os
import sys
import argparse

from ast    import Ast, AstBinary, AstNumber
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

class Data():
    def __init__(self, name:str, format_string:str):
        self.name:str = name
        self.format_string:str = format_string

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
        # Just check for both since they are on the same level of precedence
        if self.tokens[self.count].type == PLUS or self.tokens[self.count].type == MINUS:
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

# prefix all format strings with aoi_format_string so that
# its clearer
def build_string_name(name:str="aoi_format_string") -> Data:
    if name not in g.string_builders:
        g.string_builders[name] = 0
    else:
        g.string_builders[name] += 1

    return name + str(g.string_builders[name])

def build_data(name:str, format_string:str) -> Data:
    # TODO: this only supports numbers
    split_len = len(format_string.split("%"))
    num_format_str = ""
    for i in range(split_len - 1):
        if i == 0:
            num_format_str += "%d"
        else:
            num_format_str += " %d"
    output_format_str = f"b \"{num_format_str}\\n\", b 0"
    return Data(name, output_format_str)

# Just emit directly to g.ir
def emit_asts(asts:List[Ast]):
    # For now, just wrap everything in one main function
    # functions don't exist as of now
    emit_empty_line()
    emit_function("main", Integer.w)
    emit_string("{")

    emit_start()
    for ast in asts:
        if type(ast) == AstBinary:
            if ast.operator == "+":
                format_string = build_string_name()
                emit_string(f"%x =w add {ast.left.number}, {ast.right.number}")
                emit_string(f"call $printf(l ${format_string}, w %x)")
                g.data.append(build_data(format_string, "w %x"))
            elif ast.operator == "-":
                format_string = build_string_name()
                emit_string(f"%x =w sub {ast.left.number}, {ast.right.number}")
                emit_string(f"call $printf(l ${format_string}, w %x)")
                g.data.append(build_data(format_string, "w %x"))
    emit_end()

    emit_string("ret 0")
    emit_string("}")

    emit_empty_line()
    # Hardcode the bytes part of the data for now
    for data in g.data:
        emit_data(data.name, data.format_string)

    return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please input a file into the program, `python main.py file.aoi`")
        sys.exit(-1)

    files = sys.argv[1:]
    if len(files) == 1:
        input_file = files[0]
        lines = [line for line in open(input_file)]

        lexer: Lexer = Lexer(''.join(map(str, lines)))
        lexer.lex()

        parser: Parser = Parser(lexer.tokens)
        parser.parse()

        emit_asts(parser.asts)
        print(g.ir)

