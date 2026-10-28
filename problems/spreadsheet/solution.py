import re

TOKEN = re.compile(r"\s*(?:(\d+(?:\.\d+)?)|([A-Z]+\d+)|([A-Z]+)\(|(.))")
CELL = re.compile(r"([A-Z]+)(\d+)$")
FUNCTIONS = {"SUM": sum, "MAX": max, "MIN": min}


class SheetError(Exception):
    pass


def _col(letters):
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def _letters(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _cells(a, b):
    (ca, ra), (cb, rb) = CELL.match(a).groups(), CELL.match(b).groups()
    c1, c2 = sorted((_col(ca), _col(cb)))
    r1, r2 = sorted((int(ra), int(rb)))
    return [f"{_letters(c)}{r}" for c in range(c1, c2 + 1) for r in range(r1, r2 + 1)]


class Spreadsheet:
    def __init__(self):
        self.raw = {}

    def set(self, cell, raw):
        if raw == "":
            self.raw.pop(cell, None)
        else:
            self.raw[cell] = raw

    def get(self, cell):
        try:
            return self._value(cell, set())
        except SheetError as e:
            return str(e)

    # ---- evaluation
    def _value(self, cell, visiting):
        raw = self.raw.get(cell)
        if raw is None:
            return 0
        if not raw.startswith("="):
            try:
                return int(raw)
            except ValueError:
                try:
                    return float(raw)
                except ValueError:
                    return raw
        if cell in visiting:
            raise SheetError("#CYCLE!")
        visiting.add(cell)
        try:
            return _Parser(raw[1:], lambda c: self._number(c, visiting)).parse()
        finally:
            visiting.discard(cell)

    def _number(self, cell, visiting):
        value = self._value(cell, visiting)
        if isinstance(value, str):
            raise SheetError("#VALUE!")
        return value


class _Parser:
    def __init__(self, text, lookup):
        self.tokens = []
        for number, cell, func, other in TOKEN.findall(text):
            if number:
                self.tokens.append(("num", float(number) if "." in number else int(number)))
            elif cell:
                self.tokens.append(("cell", cell))
            elif func:
                self.tokens.append(("func", func))
            elif other.strip():
                self.tokens.append(("op", other))
        self.i = 0
        self.lookup = lookup

    def parse(self):
        value = self.expr()
        if self.i != len(self.tokens):
            raise SheetError("#ERROR!")
        return value

    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else (None, None)

    def take(self, op=None):
        token = self.peek()
        if token[0] is None or (op and token != ("op", op)):
            raise SheetError("#ERROR!")
        self.i += 1
        return token

    def expr(self):
        value = self.term()
        while self.peek() in (("op", "+"), ("op", "-")):
            if self.take()[1] == "+":
                value += self.term()
            else:
                value -= self.term()
        return value

    def term(self):
        value = self.factor()
        while self.peek() in (("op", "*"), ("op", "/")):
            if self.take()[1] == "*":
                value *= self.factor()
            else:
                divisor = self.factor()
                if divisor == 0:
                    raise SheetError("#DIV/0!")
                value /= divisor
        return value

    def factor(self):
        kind, value = self.take()
        if kind == "num":
            return value
        if kind == "cell":
            return self.lookup(value)
        if kind == "func":
            start = self.take()
            self.take(":")
            end = self.take()
            self.take(")")
            function = FUNCTIONS.get(value)
            if function is None or start[0] != "cell" or end[0] != "cell":
                raise SheetError("#ERROR!")
            return function([self.lookup(c) for c in _cells(start[1], end[1])])
        if (kind, value) == ("op", "("):
            inner = self.expr()
            self.take(")")
            return inner
        if (kind, value) == ("op", "-"):
            return -self.factor()
        raise SheetError("#ERROR!")
