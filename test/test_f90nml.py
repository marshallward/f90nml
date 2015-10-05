import os
import sys
import unittest

sys.path.insert(1, '../')
import f90nml
from f90nml.fpy import pybool
from f90nml.namelist import Namelist
from f90nml.findex import FIndex


class Test(unittest.TestCase):

    def setUp(self):
        self.empty_nml = {'empty_nml': {}}

        self.null_nml = {
                'null_nml': {'null_value': None},
                'null_comma_nml': {'null_comma': None},
                'null_nocomma_rpt_nml': {
                    'null_one': None,
                    'null_two': None,
                    }
                }

        self.unset_nml = {
                'unset_nml': {
                    'x': None,
                    'y': None
                    }
                }

        self.types_nml = {
                'types_nml': {
                    'v_integer': 1,
                    'v_float': 1.0,
                    'v_complex': 1+2j,
                    'v_logical': True,
                    'v_string': 'Hello',
                    }
                }

        self.vector_nml = {
                'vector_nml': {
                    'v': [1, 2, 3, 4, 5],
                    'v_idx': [1, 2, 3, 4],
                    'v_idx_ooo': [1, 2, 3, 4],
                    'v_range': [1, 2, 3, 4],
                    'v_implicit_start': [1, 2, 3, 4],
                    'v_implicit_end': [1, 2, 3, 4],
                    'v_implicit_all': [1, 2, 3, 4],
                    'v_null_start': [None, 2, 3, 4],
                    'v_null_interior': [1, 2, None, 4],
                    'v_null_end': [1, 2, 3, None],
                    'v_zero': [1, 0, 3],
                    'v_stride': [1, None, 3, None, 5, None, 7],
                    'v_single': [1],
                    'v_implicit_merge': [1, 2],
                    'v_explicit_merge': [1, 2],
                    }
                }

        self.multidim_nml = {
                'multidim_nml': {
                    'v2d': [[1, 2], [3, 4]],
                    'v3d': [[[1, 2], [3, 4]], [[5, 6], [7, 8]]],
                    'w3d': [[[1, 2, 3, 4],
                             [5, 6, 7, 8],
                             [9, 10, 11, 12]],
                            [[13, 14, 15, 16],
                             [17, 18, 19, 20],
                             [21, 22, 23, 24]]],
                    'v2d_explicit': [[1, 2], [3, 4]],
                    'v2d_outer': [[1], [2], [3], [4]],
                    'v2d_inner': [[1, 2, 3, 4]],
                    }
                }

        self.md_rowmaj_nml = {
                'multidim_nml': {
                    'v2d': [[1, 3], [2, 4]],
                    'v3d': [[[1, 5], [3, 7]], [[2, 6], [4, 8]]],
                    'w3d': [[[1, 13], [5, 17], [9, 21]],
                            [[2, 14], [6, 18], [10, 22]],
                            [[3, 15], [7, 19], [11, 23]],
                            [[4, 16], [8, 20], [12, 24]]],
                    'v2d_explicit': [[1, 3], [2, 4]],
                    'v2d_outer': [[1, 2, 3, 4]],
                    'v2d_inner': [[1], [2], [3], [4]],
                    }
                }

        self.float_nml = {
                'float_nml': {
                    'v_float': 1.,
                    'v_decimal_end': 1.,
                    'v_negative': -1.,
                    'v_single': 1.,
                    'v_double': 1.,
                    'v_single_upper': 1.,
                    'v_double_upper': 1.,
                    'v_positive_index': 10.,
                    'v_negative_index': 0.1,
                    }
                }

        self.string_nml = {
                'string_nml': {
                    'str_basic': 'hello',
                    'str_no_delim': 'hello',
                    'str_no_delim_no_esc': "a''b",
                    'single_esc_delim': "a 'single' delimiter",
                    'double_esc_delim': 'a "double" delimiter',
                    'double_nested': "''x'' \"y\"",
                    'str_list': ['a', 'b', 'c'],
                    'slist_no_space': ['a', 'b', 'c'],
                    'slist_no_quote': ['a', 'b', 'c'],
                    }
                }

        self.dtype_nml = {
                'dtype_nml': {
                    'dt_scalar': {'val': 1},
                    'dt_stack': {'outer': {'inner': 2}},
                    'dt_vector': {'vec': [1, 2, 3]}
                    },
                'dtype_multi_nml': {
                    'dt': {
                        'x': 1,
                        'y': 2,
                        'z': 3,
                        }
                    },
                'dtype_nested_nml': {
                    'f': {
                        'g': {
                            'x': 1,
                            'y': 2,
                            'z': 3,
                            }
                        }
                    },
                'dtype_field_idx_nml': {
                    'f': {
                        'x': [1, 2, 3]}
                    },
                'dtype_vec_nml': {
                    'a': {
                        'b': [
                            {'c': 1, 'd': 2},
                            {'c': 3, 'd': 4},
                            {'c': 5, 'd': 6}
                            ]
                        }
                    },
                'dtype_sparse_vec_nml': {
                    'a': {
                        'b': [None, {'c': 2}]
                        }
                    },
                'dtype_single_value_vec_nml': {
                    'a': [{'b': 1}]
                    },
                'dtype_single_vec_merge_nml': {
                    'a': {
                        'b': [{'c': 1, 'd': 2}]
                        }
                    }
                }

        self.bcast_nml = {
                'bcast_nml': {
                    'x': [2.0, 2.0],
                    'y': [None, None, None],
                    'z': [True, True, True, True],
                    },
                'bcast_endnull_nml': {
                    'x': [2.0, 2.0],
                    'y': [None, None, None],
                    }
                }

        self.comment_nml = {
                'comment_nml': {
                    'v_cmt_inline': 123,
                    'v_cmt_in_str': 'This token ! is not a comment',
                    'v_cmt_after_str': 'This ! is not a comment',
                    }
                }

        self.comment_alt_nml = {
                'comment_alt_nml': {
                    'x': 1,
                    'z': 3}
                }

        self.grp_repeat_nml = {
                'grp_repeat_nml': [{'x': 1}, {'x': 2}],
                'case_check_nml': [{'y': 1}, {'y': 2}],
                }

        self.f77_nml = {
                'f77_nml': {'x': 123},
                'next_f77_nml': {'y': 'abc'},
                }

        self.dollar_nml = {'dollar_nml': {'v': 1.}}

        self.multiline_nml = {
                'multiline_nml': {
                    'x': [
                        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                        1, 1, 1, 1, 1, 1, 1, 1
                        ]
                    }
                }

        self.ext_token_nml = {'ext_token_nml': {'x': 1}}

    # Support functions
    def assert_file_equal(self, source_fname, target_fname):
        with open(source_fname) as source:
            with open(target_fname) as target:
                source_str = source.read()
                target_str = target.read()
                self.assertEqual(source_str, target_str)

    def assert_write(self, nml, target_fname):
        tmp_fname = 'tmp.nml'
        f90nml.write(nml, tmp_fname)
        try:
            self.assert_file_equal(tmp_fname, target_fname)
        finally:
            os.remove(tmp_fname)

    # Tests
    def test_empty(self):
        test_nml = f90nml.read('empty.nml')
        self.assertEqual(self.empty_nml, test_nml)
        self.assert_write(test_nml, 'empty.nml')

    def test_null(self):
        test_nml = f90nml.read('null.nml')
        self.assertEqual(self.null_nml, test_nml)
        self.assert_write(test_nml, 'null_target.nml')

    def test_unset(self):
        test_nml = f90nml.read('unset.nml')
        self.assertEqual(self.unset_nml, test_nml)
        self.assert_write(test_nml, 'unset.nml')

    def test_types(self):
        test_nml = f90nml.read('types.nml')
        self.assertEqual(self.types_nml, test_nml)
        self.assert_write(test_nml, 'types.nml')

    def test_vector(self):
        test_nml = f90nml.read('vector.nml')
        self.assertEqual(self.vector_nml, test_nml)
        self.assert_write(test_nml, 'vector_target.nml')

    def test_multidim(self):
        test_nml = f90nml.read('multidim.nml')
        self.assertEqual(self.multidim_nml, test_nml)
        self.assert_write(test_nml, 'multidim_target.nml')

    def test_rowmaj_multidim(self):
        test_nml = f90nml.read('multidim.nml', row_major=True)
        self.assertEqual(self.md_rowmaj_nml, test_nml)

    def test_flag_syntax(self):
        self.assertRaises(ValueError, f90nml.read, 'index_empty.nml',
                          row_major='abc')
        self.assertRaises(ValueError, f90nml.read, 'index_empty.nml',
                          strict_logical='abc')

    def test_float(self):
        test_nml = f90nml.read('float.nml')
        self.assertEqual(self.float_nml, test_nml)
        self.assert_write(test_nml, 'float_target.nml')

    def test_string(self):
        test_nml = f90nml.read('string.nml')
        self.assertEqual(self.string_nml, test_nml)
        self.assert_write(test_nml, 'string_target.nml')

    def test_dtype(self):
        test_nml = f90nml.read('dtype.nml')
        self.assertEqual(self.dtype_nml, test_nml)
        self.assert_write(test_nml, 'dtype_target.nml')

    def test_bcast(self):
        test_nml = f90nml.read('bcast.nml')
        self.assertEqual(self.bcast_nml, test_nml)
        self.assert_write(test_nml, 'bcast_target.nml')

    def test_comment(self):
        test_nml = f90nml.read('comment.nml')
        self.assertEqual(self.comment_nml, test_nml)
        self.assert_write(test_nml, 'comment_target.nml')

    def test_comment_alt(self):
        parser = f90nml.Parser()
        parser.comment_tokens = '#'
        test_nml = parser.read('comment_alt.nml')
        self.assertEqual(self.comment_alt_nml, test_nml)

    def test_grp_repeat(self):
        test_nml = f90nml.read('grp_repeat.nml')
        self.assertEqual(self.grp_repeat_nml, test_nml)
        self.assert_write(test_nml, 'grp_repeat_target.nml')

    def test_f77(self):
        test_nml = f90nml.read('f77.nml')
        self.assertEqual(self.f77_nml, test_nml)
        self.assert_write(test_nml, 'f77_target.nml')

    def test_dollar(self):
        test_nml = f90nml.read('dollar.nml')
        self.assertEqual(self.dollar_nml, test_nml)
        self.assert_write(test_nml, 'dollar_target.nml')

    def test_multiline(self):
        test_nml = f90nml.read('multiline.nml')
        self.assertEqual(self.multiline_nml, test_nml)
        self.assert_write(test_nml, 'multiline.nml')

    def test_ext_token(self):
        test_nml = f90nml.read('ext_token.nml')
        self.assertEqual(self.ext_token_nml, test_nml)

    def test_write_existing_file(self):
        tmp_fname = 'tmp.nml'
        open(tmp_fname, 'w').close()
        test_nml = f90nml.read('empty.nml')
        self.assertRaises(IOError, test_nml.write, tmp_fname)
        os.remove(tmp_fname)

    def test_pop_key(self):
        test_nml = f90nml.read('empty.nml')
        test_nml.pop('empty_nml')
        self.assertEqual(test_nml, f90nml.namelist.Namelist())

    def test_patch(self):
        patch_nml = f90nml.read('types_patch.nml')
        f90nml.patch('types.nml', patch_nml, 'tmp.nml')
        test_nml = f90nml.read('tmp.nml')
        try:
            self.assertEqual(test_nml, patch_nml)
        finally:
            os.remove('tmp.nml')

    def test_patch_valueerror(self):
        self.assertRaises(ValueError, f90nml.patch, 'types.nml', 'xyz',
                          'tmp.nml')

    def test_default_patch(self):
        patch_nml = f90nml.read('types_patch.nml')
        f90nml.patch('types.nml', patch_nml)
        test_nml = f90nml.read('types.nml~')
        try:
            self.assertEqual(test_nml, patch_nml)
        finally:
            os.remove('types.nml~')

    def test_no_selfpatch(self):
        patch_nml = f90nml.read('types_patch.nml')
        self.assertRaises(ValueError, f90nml.patch,
                          'types.nml', patch_nml, 'types.nml')

    def test_comment_patch(self):
        nml = {'comment_nml': {'v_cmt_inline': 456}}
        try:
            f90nml.patch('comment.nml', nml, 'tmp.nml')
            self.assert_file_equal('comment_patch.nml', 'tmp.nml')
        finally:
            os.remove('tmp.nml')

    def test_index_syntax(self):
        self.assertRaises(ValueError, f90nml.read, 'index_empty.nml')
        self.assertRaises(ValueError, f90nml.read, 'index_bad.nml')
        self.assertRaises(ValueError, f90nml.read, 'index_bad_start.nml')
        self.assertRaises(ValueError, f90nml.read, 'index_empty_end.nml')
        self.assertRaises(ValueError, f90nml.read, 'index_bad_end.nml')
        self.assertRaises(ValueError, f90nml.read, 'index_empty_stride.nml')
        self.assertRaises(ValueError, f90nml.read, 'index_bad_stride.nml')
        self.assertRaises(ValueError, f90nml.read, 'index_zero_stride.nml')

    def test_f90repr(self):
        nml = Namelist()
        self.assertEqual(nml.f90repr(1), '1')
        self.assertEqual(nml.f90repr(1.), '1.0')
        self.assertEqual(nml.f90repr(1+2j), '(1.0, 2.0)')
        self.assertEqual(nml.f90repr(True), '.true.')
        self.assertEqual(nml.f90repr(False), '.false.')
        self.assertEqual(nml.f90repr('abc'), "'abc'")

        for ptype in ({}, [], set()):
            self.assertRaises(ValueError, nml.f90repr, ptype)

    def test_pybool(self):
        for fstr_true in ('true', '.true.', 't', '.t.'):
            self.assertEqual(pybool(fstr_true), True)

        for fstr_false in ('false', '.false.', 'f', '.f.'):
            self.assertEqual(pybool(fstr_false), False)

        for fstr_true in ('ture', '.t'):
            self.assertEqual(pybool(fstr_true, strict_logical=False), True)

        for fstr_false in ('flase', '.f'):
            self.assertEqual(pybool(fstr_false, strict_logical=False), False)

        for fstr in ('ture', '.t', 'flase', '.f'):
            self.assertRaises(ValueError, pybool, fstr)

        for fstr in ('g', '.', 'xyz'):
            self.assertRaises(ValueError, pybool, fstr, strict_logical=False)

    def test_close_patch_on_error(self):
        patch = {'tmp_nml': {'tmp_val': 0}}
        self.assertRaises(ValueError, f90nml.patch, 'index_empty.nml', patch,
                                                    'tmp.nml')
        os.remove('tmp.nml')

    def test_indent(self):
        test_nml = f90nml.read('types.nml')

        test_nml.indent = 2
        self.assert_write(test_nml, 'types_indent_2.nml')

        test_nml.indent = '\t'
        self.assert_write(test_nml, 'types_indent_tab.nml')

        self.assertRaises(ValueError, setattr, test_nml, 'indent', -4)
        self.assertRaises(ValueError, setattr, test_nml, 'indent', 'xyz')
        self.assertRaises(TypeError, setattr, test_nml, 'indent', [1, 2, 3])

    def test_colwidth(self):
        test_nml = f90nml.read('multiline.nml')
        test_nml.colwidth = 40
        self.assert_write(test_nml, 'multiline_colwidth.nml')

        self.assertRaises(ValueError, setattr, test_nml, 'colwidth', -1)
        self.assertRaises(TypeError, setattr, test_nml, 'colwidth', 'xyz')

    def test_end_comma(self):
        test_nml = f90nml.read('types.nml')
        test_nml.end_comma = True
        self.assert_write(test_nml, 'types_end_comma.nml')

        self.assertRaises(TypeError, setattr, test_nml, 'end_comma', 'xyz')

    def test_uppercase(self):
        test_nml = f90nml.read('types.nml')
        test_nml.uppercase = True
        self.assert_write(test_nml, 'types_uppercase.nml')

        self.assertRaises(TypeError, setattr, test_nml, 'uppercase', 'xyz')

    def test_floatformat(self):
        test_nml = f90nml.read('float.nml')
        test_nml.floatformat = '.3f'
        self.assert_write(test_nml, 'float_format.nml')

        self.assertRaises(TypeError, setattr, test_nml, 'floatformat', 123)

    def test_logical_repr(self):
        test_nml = f90nml.read('logical.nml', strict_logical=False)
        test_nml.true_repr = 'T'
        test_nml.false_repr = 'F'

        self.assertEqual(test_nml.false_repr, test_nml.logical_repr[0])
        self.assertEqual(test_nml.true_repr, test_nml.logical_repr[1])
        self.assert_write(test_nml, 'logical_repr.nml')

        test_nml.logical_repr = 'F', 'T'
        self.assert_write(test_nml, 'logical_repr.nml')

        self.assertRaises(TypeError, setattr, test_nml, 'true_repr', 123)
        self.assertRaises(TypeError, setattr, test_nml, 'false_repr', 123)
        self.assertRaises(ValueError, setattr, test_nml, 'true_repr', 'xyz')
        self.assertRaises(ValueError, setattr, test_nml, 'false_repr', 'xyz')
        self.assertRaises(TypeError, setattr, test_nml, 'logical_repr', 'xyz')
        self.assertRaises(ValueError, setattr, test_nml, 'logical_repr', [])

    def test_findex_iteration(self):
        rng = [(None, 5, None)]
        fidx = iter(FIndex(rng))

        for i, j in enumerate(fidx, start=1):
            self.assertEqual(i, j[0])

    def test_dict_write(self):
        self.assert_write(self.types_nml, 'types_dict.nml')


if __name__ == '__main__':
    if os.path.isfile('tmp.nml'):
        os.remove('tmp.nml')
    unittest.main()
