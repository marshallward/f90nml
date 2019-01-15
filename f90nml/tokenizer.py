"""Fortran namelist tokenizer.

:copyright: Copyright 2017 Marshall Ward, see AUTHORS for details.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
import itertools
import string


class Tokenizer(object):
    """Fortran namelist tokenizer."""

    # I don't use these two
    special_chars = ' =+-*/\\()[]{},.:;!"%&~<>?\'`|$#@'     # Table 3.1
    lexical_tokens = '=+-*/()[],.:;%&<>'                    # Meaningful?

    # I only use this one
    punctuation = '=+-*/\\()[]{},:;%&~<>?`|$#@'    # Unhandled Table 3.1 tokens

    def __init__(self):
        """Initialise the tokenizer."""
        self.characters = None
        self.prior_char = None
        self.char = None
        self.idx = None
        self.whitespace = string.whitespace.replace('\n', '')
        self.prior_delim = None

        # Set to true if inside a namelist group
        self.group_token = None

    def parse(self, line):
        """Tokenize a line of Fortran source."""
        tokens = []

        self.idx = -1   # Bogus value to ensure idx = 0 after first iteration
        self.characters = iter(line)
        self.update_chars()

        while self.char != '\n':
            # Update namelist group status
            if self.char in ('&', '$'):
                self.group_token = self.char

            if self.group_token and (
                    (self.group_token, self.char) in (('&', '/'), ('$', '$'))):
                self.group_token = False

            word = ''
            if self.char in self.whitespace:
                while self.char in self.whitespace:
                    word += self.char
                    self.update_chars()

            elif self.char in ('!', '#') or self.group_token is None:
                # Abort the iteration and build the comment token
                word = line[self.idx:-1]
                self.char = '\n'

            elif self.char in '"\'' or self.prior_delim:
                word = self.parse_string()

            elif self.char.isalpha():
                word = self.parse_name(line)

            elif self.char in ('+', '-'):
                # Lookahead to check for IEEE value
                self.characters, lookahead = itertools.tee(self.characters)
                ieee_val = ''.join(itertools.takewhile(str.isalpha, lookahead))
                if ieee_val.lower() in ('inf', 'infinity', 'nan'):
                    word = self.char + ieee_val
                    self.characters = lookahead
                    self.prior_char = ieee_val[-1]
                    self.char = next(lookahead, '\n')
                else:
                    word = self.parse_numeric()

            elif self.char.isdigit():
                word = self.parse_numeric()

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
        """Tokenize a Fortran name, such as a variable or subroutine."""
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
        """Tokenize a Fortran string."""
        word = ''

        if self.prior_delim:
            delim = self.prior_delim
            self.prior_delim = None
        else:
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
            elif self.char == '\n':
                self.prior_delim = delim
                break
            else:
                word += self.char
                self.update_chars()

        return word

    def parse_numeric(self):
        """Tokenize a Fortran numerical value."""
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
        """Update the current charters in the tokenizer."""
        # NOTE: We spoof non-Unix files by returning '\n' on StopIteration
        self.prior_char, self.char = self.char, next(self.characters, '\n')
        self.idx += 1
