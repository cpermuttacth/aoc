#!/usr/bin/env python3

import re
from collections import deque

def get_desc():
    return 21, 'Day 21: Scrambled Letters and Hash'


def calc(log, values, code, reverse):
    if reverse:
        values = reversed(values)
    for cur in values:
        found = False
        if not found:
            m = re.search("swap position (.*) with position (.*)", cur)
            if m:
                found = True
                code = list(code)
                code[int(m.group(1))], code[int(m.group(2))] = code[int(m.group(2))], code[int(m.group(1))]
                code = "".join(code)
        if not found:
            m = re.search("swap letter (.*) with letter (.*)", cur)
            if m:
                found = True
                a, b = code.index(m.group(1)), code.index(m.group(2))
                code = list(code)
                code[a], code[b] = code[b], code[a]
                code = "".join(code)
        if not found:
            m = re.search("rotate (left|right) (.*) step(s|)", cur)
            if m:
                found = True
                code = deque(code)
                if m.group(1) == "left":
                    code.rotate(-int(m.group(2)) * (-1 if reverse else 1))
                else:
                    code.rotate(int(m.group(2)) * (-1 if reverse else 1))
                code = "".join(code)
        if not found:
            m = re.search("rotate based on position of letter (.*)", cur)
            if m:
                found = True
                i = code.index(m.group(1))
                code = deque(code)
                if reverse:
                    target = 0
                    code.rotate(-1)
                    while ("".join(code)).index(m.group(1)) != target:
                        code.rotate(-1)
                        target += 1
                        if target == 4:
                            code.rotate(-1)
                else:
                    code.rotate(1 + i)
                    if i >= 4:
                        code.rotate(1)
                code = "".join(code)
        if not found:
            m = re.search("reverse positions (.*) through (.*)", cur)
            if m:
                found = True
                code = code[0:int(m.group(1))] + "".join(reversed(code[int(m.group(1)):int(m.group(2))+1])) + code[int(m.group(2))+1:]
        if not found:
            m = re.search("move position (.*) to position (.*)", cur)
            if m:
                found = True
                code = list(code)
                a, b = m.group(1), m.group(2)
                if reverse:
                    a, b = b, a
                temp = code.pop(int(a))
                code.insert(int(b), temp)
                code = "".join(code)
        if not found:
            raise Exception(cur)

    return code


def test(log):
    values = [
        "swap position 4 with position 0",
        "swap letter d with letter b",
        "reverse positions 0 through 4",
        "rotate left 1 step",
        "move position 1 to position 4",
        "move position 3 to position 0",
        "rotate based on position of letter b",
        "rotate based on position of letter d",
    ]

    if calc(log, values, "abcde", False) == "decab":
        log.show("Passed part 1")
        if calc(log, values, "decab", True) == "deabc":
            log.show("Passed part 2")
            return True
    return False


def run(log, values):
    log.show(calc(log, values, "abcdefgh", False))
    log.show(calc(log, values, "fbgdceah", True))
