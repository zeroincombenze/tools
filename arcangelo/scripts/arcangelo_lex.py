# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
# import sys
# import os

__version__ = "2.1.1"


class Lex(object):
    PRECEDENCE = {
        ",": 1,
        "=": 2,
        "+": 3,
        "-": 3,
        "*": 4,
        "/": 4,
        "^": 5,
    }

    ASSOCIATE = {
        "^": "right"
    }

    def __init__(self, tokens, action="attrs_2_formula"):
        self.action = action
        self.states = []
        self.tokens = [(tok[0], tok[1]) for tok in tokens]
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, expected=None):
        node = self.peek()
        if node:
            kind, value = node
            if expected and kind != expected:
                raise SyntaxError("Expected %s, got %s" % (expected, kind))
            self.pos += 1
        return node

    def atom(self):
        node = self.peek()
        if node:
            kind, value = node
            if kind == "name":
                self.eat(kind)
                return node
            elif kind == "int":
                self.eat(kind)
                return node
            elif kind == "op_lparen":
                self.eat(kind)
                node = self.expr(0)
                self.eat("op_rparen")
                return node
            else:
                raise SyntaxError("Unexpected token (%s, %s)" % (kind, value))
        return node

    def parse(self):
        return self.expr(0)

    def expr(self, min_prio):
        left = self.atom()
        while True:
            node = self.peek()
            if not node:
                break
            kind, value = node
            if kind not in ("operator", ):
                break
            prio = self.PRECEDENCE.get(value, 99)
            assoc = self.ASSOCIATE.get(value, "left")
            if prio < min_prio:
                break
            self.eat()  # consume operator
            next_min = prio + (0 if assoc == "right" else 1)
            right = self.expr(next_min)
            left = (node, left, right)
        return left
