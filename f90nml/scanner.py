import string
import sys
import operator
import os

# The Fortran character set
alpha = string.ascii_letters
digit = string.digits
alnum = alpha + digit + '_'

blank = ' '
# NOTE: Not all of these can act as token separators, but for now we interpret
#   them as blanks.
blank += '\t\f\r\n'

# Special characters, as defined in the language standard
special = '=+-*/\\()[]{},.:;!"%&~<>?\'`^|$#@'

charset = alnum + blank + special


# Control flags
non_delimited_strings = True


def notchar(chars, ref=charset):
    """Remove `chars` from a reference character set."""
    base = ref
    for c in chars:
        base = ''.join(base.split(c))
    return base


def add_str_states(M, state, delim):
    assert delim in ("'", '"')

    state_esc = state + '_esc'

    # String delimiter (" or ')
    M[state] = (
        {c: state for c in notchar(delim)}
        | {delim: state_esc}
    )

    # Escaped delimiter
    M[state_esc] = (
        {delim: state}
        | {c: 'end' for c in notchar(delim)}
    )


# DFA scanner

M = {}
# TODO: Pull out dash (minus) and handle separately.
#   It *must* precede a number!
M['start'] = (
    {c: 'name' for c in alpha + '_'}
    | {c: 'num' for c in digit}
    | {"'": 'str_a'}
    | {'"': 'str_q'}
    | {'.': 'dec'}
    | {'+': 'op_plus'}
    | {'-': 'op_minus'}
    | {c: 'op' for c in notchar('+-."\'!#', special)}
)


# Blanks
# TODO: This is huge, perhaps move into a separate function
M['start'] |= {c: 'blank' for c in blank}
M['start'] |= {'!': 'cmt'}
M['start'] |= {'#': 'cmt'}  # TODO: Handle separately?

M['blank'] = {}
M['blank'] |= {c: 'blank' for c in blank}
M['blank'] |= {'!': 'cmt'}
M['blank'] |= {c: 'end' for c in notchar(blank + '!')}

# This doesn't actually get used more than once, but it is correct.
M['cmt'] = (
    {c: 'cmt' for c in notchar('\n')}
    | {'\n': 'end'}
)


# Identifiers (keywords, functions, variables, ...)
# NOTE: We permit identifiers to start with _ for preprocessor support
M['name'] = {c: 'name' for c in alnum}
M['name'] = {c: 'end' for c in notchar(alnum)}
if non_delimited_strings:
    M['name']["'"] = 'name'
    M['name']['"'] = 'name'


# Apostrophe-delimited strings
add_str_states(M, 'str_a', "'")

# Quote-delimited strings
add_str_states(M, 'str_q', '"')


# Literal numeric
# NOTE: Decimals must be separate due to logicals (.true./.false.)
M['num'] = (
    {c: 'num' for c in digit}
    | {c: 'num_float_e' for c in 'eEdD'}
    | {'.': 'num_frac'}
    | {c: 'num_float_sign' for c in '+-'}
    | {'_': 'num_kind'}
    | {c: 'end' for c in notchar(digit + '+-._eEdD')}
)

M['num_frac'] = (
    {c: 'num_frac' for c in digit}
    | {c: 'num_float_e' for c in 'eEdD'}
    | {c: 'num_float_sign' for c in '+-'}
    | {'_': 'num_kind'}
    | {c: 'end' for c in notchar(digit + '+-_eEdD')}
)

# Numeric E notation token
M['num_float_e'] = (
    {c: 'num_float_sign' for c in '+-'}
    | {c: 'num_float_exp' for c in digit}
    # Error: ^[0-9+-]
)

# Numeric E notation exponent sign
M['num_float_sign'] = (
    {c: 'num_float_exp' for c in digit}
    # Error: ^[0-9]
)

# Numeric E notation exponent
M['num_float_exp'] = (
    {c: 'num_float_exp' for c in digit}
    | {'_': 'num_kind'}
    | {c: 'end' for c in notchar(digit + '_')}
)

# Numeric kind token (_)
M['num_kind'] = (
    {c: 'num_kind_name' for c in alpha}
    | {c: 'num_kind_int' for c in digit}
)

# Numeric kind as a variable name
# NOTE: This is identical to name, but might be useful for tokenization
M['num_kind_name'] = (
    {c: 'num_kind_name' for c in alnum}
    | {c: 'end' for c in notchar(alnum)}
)

# Numeric kind as coded integer
M['num_kind_int'] = (
    {c: 'num_kind_int' for c in alnum}
    | {c: 'end' for c in notchar(alnum)}
)


# ----
# Old numeric stuff.. not sure how it holds up

# Decimal mark
# TODO: Fix me!  This only represents the leading decimal mark.
M['dec'] = (
    {c: 'num' for c in digit}
    | {'_': 'num_kind'}
    | {c: 'op_keyword' for c in notchar('eEdD', ref=alpha)}
    | {c: 'op_kw_test' for c in 'eEdD'}
    | {c: 'end' for c in notchar(digit + alpha + '_')}
)

# TODO: These permit "+." and "-." which are not valid!
# TODO: "name" is only handled for +-inf and +-nan.  It could be tightened but
#   the DFA will be unpretty.

M['op_plus'] = (
    {c: 'num' for c in digit}
    | {'.': 'num_frac'}
    | {c: 'name' for c in alpha}
)

M['op_minus'] = (
    {c: 'num' for c in digit}
    | {'.': 'num_frac'}
    | {c: 'name' for c in alpha}
)

M['op_kw_test'] = (
    {c: 'op_keyword' for c in alpha}
    | {c: 'num_float_sign' for c in '+-'}
    | {c: 'num_float_exp' for c in digit}
    # Error: ^[a-z0-9+-]
)

# End decimal
#---


# Single-character tokens (operators, declaration, etc)
M['op'] = (
    {c: 'end' for c in charset}
)


# TODO: We don't have keyword operators, just .true. and .false. values.
M['op_keyword'] = (
    {c: 'op_keyword' for c in alpha}
    | {'.': 'op'}
    | {c: 'end' for c in notchar(alpha + '.')}
)


def scan(file):
    lexemes = []

    lex = ''
    state = 'start'
    for line in file:
        ## debug
        #print('start line:', repr(line))

        linelx = []
        for char in line:
            try:
                state = M[state][char]
            except KeyError:
                # This catches potential unicode characters in a string.
                # TODO: What about non-delimited strings?
                if state in ('str_a', 'str_q') and char == '\n':
                    # However, non-closed strings are an error
                    raise

            ## Debug mode?
            #print(
            #    'char:', repr(char),
            #    'state:', state,
            #)

            if state not in ('end', 'cmt'):
                lex += char

            elif (state == 'end'):
                linelx.append(lex)
                ## debug
                #print('lexemes: ', linelx)

                # "Lookback" by re-evaluating char
                lex = char
                state = M['start'][char]
                ## Debug mode?
                #print(
                #    '(lookback) char:', repr(char),
                #    ' state:', state,
                #)

            # Not a backreference but prevents redundant character iteration
            elif (state == 'cmt'):
                #print('cmt:  linelx:', linelx)
                #print('cmt:     len:', len(''.join(linelx)))

                #idx = max(len(''.join(linelx)), 0)
                buf = ''.join(linelx) + lex
                idx = len(buf[buf.rfind('\n') + 1:])

                #print('cmt:    line:', repr(line))
                #print('cmt:     idx:', idx)

                #linelx.append(line[idx:])
                #print('cmt:  prelex:', repr(lex))
                lex += line[idx:]
                #print('cmt: postlex:', repr(lex))

                #if line[-1] == '\n':
                #    lex = '\n'
                #    #state = 'op'
                #else:
                #    lex = ''
                #    #state = 'start'
                state = 'blank'

                break

        ## debug mode
        #print('lexemes: ', linelx)
        #print(repr('·'.join(linelx)))

        lexemes.extend(linelx)

        #print('--------')

    # Append any trailing lexeme
    if lex:
        try:
            assert any('end' in M[state][c] for c in M[state])
        except AssertionError:
            print(M[state])
            raise

        lexemes.append(lex)

    return lexemes
