class Tokenizer(object):

    # I don't use these two
    special_chars = ' =+-*/\\()[]{},.:;!"%&~<>?\'`|$#@'     # Table 3.1
    lexical_tokens = '=+-*/()[],.:;%&<>'                    # Meaningful?

    # I only use this one
    punctuation = '=+-*/\\()[]{},:;%&~<>?`|$#@'    # Unhandled Table 3.1 tokens

    # Token pairs (syntax and operators)
    # TODO: (/ and /) are currently removed, for reasons discussed below.
    pairs = ('::', '=>', '**', '//', '==', '/=', '<=', '>=')

    def __init__(self):
        self.characters = None
        self.prior_char = None
        self.char = None
        self.idx = None

        self.prior_delim = None

    def parse(self, line, macros={}):
        """Tokenize a line of Fortran source."""

        tokens = []

        self.idx = -1   # Bogus value to ensure idx = 0 after first iteration
        self.characters = iter(line)
        self.update_chars()

        while self.char != '\n':
            word = ''
            if self.char in ' \t':
                while self.char in ' \t':
                    word += self.char
                    self.update_chars()

            elif self.char in '"\'' or self.prior_delim:
                word = self.parse_string()
                if (self.prior_char, self.char) == ('&', '\n'):
                    tokens.append(word)
                    word = self.prior_char

            elif self.char.isalpha() or self.char == '_':
                # NOTE: Variables cannot start with underscore
                #       But keep for now to accommodate preprocessed tags
                while self.char.isalnum() or self.char in  '\'"_':
                    word += self.char
                    self.update_chars()

            elif self.char.isdigit():
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

                # NOTE: The following check does not work for (/ and /) because
                # it produces false tokens inside `operator (/)` declarations.
                # One potential solution is to check for the `operator` token
                # inside of `tokens`, but it's a little more complicated...
                # For now, I just omit (/ and /).

                if self.prior_char + self.char in self.pairs:
                    word = self.prior_char + self.char
                    tokens.append(word)
                    self.update_chars()
                    continue

            else:
                # This should never happen
                raise ValueError

            # Modify token if needed
            if word in macros:
                # TODO: Multiword substitutions are not tokenized!
                print('replacing {} with {}'.format(word, macros[word]))
                word = macros[word]

            tokens.append(word)

        return tokens

    def parse_string(self):
        word = ''

        if self.prior_delim:
            delim = self.prior_delim
            self.prior_delim = None
        else:
            delim = self.char
            word += self.char
            self.update_chars()

        next_delim = None
        while True:
            if self.char == '&':
                self.update_chars()
                if self.char == '\n':
                    next_delim = delim
                    break
                else:
                    word += '&'
            elif self.char == delim:
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

        self.prior_delim = next_delim

        return word

    def parse_numeric(self):
        word = ''
        frac = False

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

        if self.char == '_':
            word += self.char
            self.update_chars()
            named = self.char.isalpha()

            while (self.char.isdigit() or
                   (self.char.isalpha() or self.char == '_' and named)):
                word += self.char
                self.update_chars()

        return word

    def update_chars(self):
        self.prior_char, self.char = self.char, next(self.characters)
        self.idx += 1
