import string
import itertools


class Tokenizer(object):

    # I don't use these two
    special_chars = ' =+-*/\\()[]{},.:;!"%&~<>?\'`|$#@'     # Table 3.1
    lexical_tokens = '=+-*/()[],.:;%&<>'                    # Meaningful?

    # I only use this one
    punctuation = '=+-*/\\()[]{},:;%&~<>?`|$#@'    # Unhandled Table 3.1 tokens

    def __init__(self):
        self.characters = None
        self.prior_char = None
        self.char = None
        self.idx = None
        self.whitespace = string.whitespace.replace('\n', '')

    def parse(self, line):
        """Tokenize a line of Fortran source."""

        tokens = []

        self.idx = -1   # Bogus value to ensure idx = 0 after first iteration
        self.characters = iter(line)
        self.update_chars()

        while self.char != '\n':
            word = ''
            if self.char in self.whitespace:
                while self.char in self.whitespace:
                    word += self.char
                    self.update_chars()

            elif self.char in '"\'':
                word = self.parse_string()

            elif self.char.isalpha():
                word = self.parse_name(line)

            elif self.char.isdigit() or self.char == '-':
                word = self.parse_numeric()

            elif self.char in ('!', '#'):
                # Abort the iteration and build the comment token
                word = line[self.idx:-1]
                self.char = '\n'

            elif self.char == '.':
                self.update_chars()
                if self.char.isdigit():
                    frac = self.parse_numeric()
                    word = '.' + frac
                else:
                    word = '.'
                    while self.char.isalpha():
                        word += self.char
                        self.update_chars()
                    if self.char == '.':
                        word += self.char
                        self.update_chars()

            elif self.char in Tokenizer.punctuation:
                word = self.char
                self.update_chars()

            else:
                # This should never happen
                raise ValueError

            tokens.append(word)

        return tokens

    def parse_name(self, line):
        end = self.idx
        for char in line[self.idx:]:
            if not char.isalnum() and char not in '\'"_':
                break
            end += 1

        word = line[self.idx:end]

        self.idx = end - 1
        # Update iterator, minus first character which was already read
        self.characters = itertools.islice(self.characters, len(word) - 1,
                                           None)
        self.update_chars()

        return word

    def parse_string(self):
        word = ''

        delim = self.char
        word += self.char
        self.update_chars()

        while True:
            if self.char == delim:
                # Check for escaped delimiters
                self.update_chars()
                if self.char == delim:
                    word += 2 * delim
                    self.update_chars()
                else:
                    word += delim
                    break
            else:
                word += self.char
                self.update_chars()

        return word

    def parse_numeric(self):
        word = ''
        frac = False

        if self.char == '-':
            word += self.char
            self.update_chars()

        while self.char.isdigit() or (self.char == '.' and not frac):
            # Only allow one decimal point
            if self.char == '.':
                frac = True
            word += self.char
            self.update_chars()

        # Check for float exponent
        if self.char in 'eEdD':
            word += self.char
            self.update_chars()

        if self.char in '+-':
            word += self.char
            self.update_chars()
        while self.char.isdigit():
            word += self.char
            self.update_chars()

        return word

    def update_chars(self):
        self.prior_char, self.char = self.char, next(self.characters)
        self.idx += 1
