import unittest

from main import Lexer, Parser
from main import NUMBER, STRING, ASSIGN, PLUS, \
                MINUS, BANG, ASTERISK, SLASH, \
                MODULUS
from ast import Ast, AstBinary, AstNumber
from enum   import Enum
from typing import List, Set, Dict

class TestLexer(unittest.TestCase):
    def test_lexer(self):
        sample:str = "1 + 2"
        lexer: Lexer = Lexer(sample)
        lexer.lex()

        self.assertEqual(len(lexer.tokens), 3)
        self.assertEqual(lexer.tokens[0].type, NUMBER)
        self.assertEqual(lexer.tokens[0].literal,"1")
        self.assertEqual(lexer.tokens[1].type, PLUS)
        self.assertEqual(lexer.tokens[1].literal,"+")
        self.assertEqual(lexer.tokens[2].type, NUMBER)
        self.assertEqual(lexer.tokens[2].literal,"2")

class TestParser(unittest.TestCase):
    def test_parser(self):
        sample:str = "1 + 2"
        lexer: Lexer = Lexer(sample)
        lexer.lex()
        parser: Parser = Parser(lexer.tokens)
        parser.parse()

        self.assertEqual(len(parser.asts), 1)
        self.assertEqual(type(parser.asts[0]), AstBinary)
        self.assertEqual(parser.asts[0].left.number, "1")
        self.assertEqual(parser.asts[0].right.number, "2")
        self.assertEqual(parser.asts[0].operator, "+")


if __name__ == '__main__':
    # Run tests
    unittest.main()
