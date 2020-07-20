"""Fortran namelist tokenizer.

:copyright: Copyright 2017 Marshall Ward, see AUTHORS for details.
:license: Apache License, Version 2.0, see LICENSE for details.
"""
import string


class Tokenizer(object):
    """Fortran namelist tokenizer."""

    # I don't use these two
    special_chars = ' =+-*/\\()[]{},.:;!"%&~<>?\'`|$#@'     # Table 3.1
    lexical_tokens = '=+-*/()[],.:;%&<>'                    # Meaningful?

    # I only use this one
    punctuation = '=*/\\()[]{},:;%&~<>?`|$#@'    # Unhandled Table 3.1 tokens

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

        # Standard token sets
        self.comment_tokens = '!'

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

            elif self.char in self.comment_tokens or self.group_token is None:
                # Abort the iteration and build the comment token
                word = line[self.idx:-1]
                self.char = '\n'

            elif self.char in '"\'' or self.prior_delim:
                word = self.parse_string()

            elif self.char in Tokenizer.punctuation:
                word = self.char
                self.update_chars()

            else:
                while (not self.char.isspace()
                       and self.char not in Tokenizer.punctuation):
                    word += self.char
                    self.update_chars()

            tokens.append(word)

        return tokens

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

    def update_chars(self):
        """Update the current charters in the tokenizer."""
        # NOTE: We spoof non-Unix files by returning '\n' on StopIteration
        self.prior_char, self.char = self.char, next(self.characters, '\n')
        self.idx += 1
