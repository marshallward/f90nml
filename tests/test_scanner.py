from __future__ import print_function

import os
import sys
import unittest

# Include parent path in case we are running within the tests directory
sys.path.insert(1, '../')
from f90nml.scanner import scan

class Test(unittest.TestCase):

    def setUp(self):
        # Move to test directory if running from setup.py
        if os.path.basename(os.getcwd()) != 'tests':
            os.chdir('tests')

    # Names

    def test_blank(self):
        result = scan('')
        self.assertEqual([], result)

    def test_whitespace(self):
        result = scan(' \t\f\r\n')
        self.assertEqual([' \t\f\r\n'], result)

    # Delimited strings

    def test_name(self):
        result = scan('abc123')
        self.assertEqual(['abc123'], result)

    def test_assignment(self):
        result = scan('a=1')
        self.assertEqual(['a', '=', '1'], result)

    # Arrays

    def test_array_element(self):
        result = scan('a(1)')
        self.assertEqual(['a', '(', '1', ')'], result)

    def test_array_element_multidim(self):
        result = scan('a(1,2)')
        self.assertEqual(['a', '(', '1', ',', '2', ')'], result)

    def test_array_section(self):
        result = scan('a(1:3)')
        self.assertEqual(['a', '(', '1', ':', '3', ')'], result)

    def test_array_section_whole(self):
        result = scan('a(:)')
        self.assertEqual(['a', '(', ':', ')'], result)

    def test_array_section_multidim(self):
        result = scan('a(1:3,4:6)')
        self.assertEqual(
                ['a', '(', '1', ':', '3', ',', '4', ':', '6', ')'],
                result
        )

    # Derived types

    def test_derived_type_ref(self):
        result = scan('a%b')
        self.assertEqual(['a', '%', 'b'], result)

    # Strings

    def test_string_quote(self):
        result = scan('"abc"')
        self.assertEqual(['"abc"'], result)

    def test_string_quote_escape(self):
        result = scan('"abc""def"')
        self.assertEqual(['"abc""def"'], result)

    def test_string_apostrophe(self):
        result = scan("'abc'")
        self.assertEqual(["'abc'"], result)

    def test_string_apostrophe_escape(self):
        result = scan("'abc''def'")
        self.assertEqual(["'abc''def'"], result)

    def test_string_comment_token(self):
        result = scan('"abc!def"')
        self.assertEqual(['"abc!def"'], result)

    def test_string_comment_token_newline(self):
        result = scan('x="abc!def"\n')
        self.assertEqual(['x', '=', '"abc!def"', '\n'], result)

    def test_non_delimited_string_quote(self):
        result = scan('abc"def"')
        self.assertEqual(['abc"def"'], result)

    # Scalars

    def test_integer(self):
        result = scan('123')
        self.assertEqual(['123'], result)

    def test_integer_negate(self):
        result = scan('-123')
        self.assertEqual(['-123'], result)

    def test_integer_positive(self):
        result = scan('+123')
        self.assertEqual(['+123'], result)

    def test_integer_kind(self):
        self.assertRaises(KeyError, scan, '1_8')

    def test_real_decimal(self):
        result = scan('1.23')
        self.assertEqual(['1.23'], result)

    def test_real_leading_decimal(self):
        result = scan('.12')
        self.assertEqual(['.12'], result)

    def test_real_signed_leading_decimal(self):
        result = scan('-.12')
        self.assertEqual(['-.12'], result)

    def test_real_decimal_kind(self):
        self.assertRaises(KeyError, scan, '1.0_8')

    def test_real_leading_decimal_kind(self):
        self.assertRaises(KeyError, scan, '.1_8')

    # Exponent form

    def test_real_e(self):
        result = scan('1e3')
        self.assertEqual(['1e3'], result)

    def test_real_e_decimal(self):
        result = scan('1.2e3')
        self.assertEqual(['1.2e3'], result)

    def test_real_d(self):
        result = scan('1D3')
        self.assertEqual(['1D3'], result)

    def test_real_d_signed_exp(self):
        result = scan('-1.2D+3')
        self.assertEqual(['-1.2D+3'], result)

    def test_real_exponent_kind(self):
        self.assertRaises(KeyError, scan, '1e3_8')

    # The hideous no-exponent reals!
    def test_real_no_e(self):
        result = scan('1.2-3')
        self.assertEqual(['1.2-3'], result)

    def test_real_positive_no_e(self):
        result = scan('1.2+3')
        self.assertEqual(['1.2+3'], result)

    def test_positive_inf(self):
        result = scan('+inf')
        self.assertEqual(['+inf'], result)

    def test_negative_nan(self):
        result = scan('-nan')
        self.assertEqual(['-nan'], result)

    # Logicals and keyword operators

    def test_logical_true(self):
        result = scan('.true.')
        self.assertEqual(['.true.'], result)

    def test_logical_false(self):
        result = scan('.false.')
        self.assertEqual(['.false.'], result)

    def test_keyword_operator(self):
        result = scan('.not.')
        self.assertEqual(['.not.'], result)

    # Repeat values

    def test_repeat_value(self):
        result = scan('2*1.0')
        self.assertEqual(['2', '*', '1.0'], result)

    # Comments

    def test_comment_line(self):
        result = scan('!comment\n')
        self.assertEqual(['!comment\n'], result)

    def test_comment_after_value(self):
        result = scan('x=1!comment')
        self.assertEqual(['x', '=', '1', '!comment'], result)

    def test_comment_after_value_newline(self):
        result = scan('x=1!comment\n/')
        self.assertEqual(['x', '=', '1', '!comment\n', '/'], result)

    def test_comment_after_blank_newline(self):
        result = scan('x=1 !comment\n/')
        self.assertEqual(['x', '=', '1', ' !comment\n', '/'], result)

    def test_comment_after_string(self):
        result = scan('x="abc"!comment\n')
        self.assertEqual(['x', '=', '"abc"', '!comment\n'], result)

    def test_comment_in_group(self):
        result = scan('&grp\n  x=1!comment\n/\n')
        self.assertEqual(
            ['&', 'grp', '\n  ', 'x', '=', '1', '!comment\n', '/', '\n'],
            result
        )


if __name__ == '__main__':
    unittest.main()
