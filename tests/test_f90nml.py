from __future__ import print_function

import math
import os
import sys
import unittest

try:
    from StringIO import StringIO   # Python 2.x
except ImportError:
    from io import StringIO         # Python 3.x

try:
    from collections import OrderedDict     # Python 3.x
except ImportError:
    from ordereddict import OrderedDict     # Python 2.x

try:
    import numpy
    has_numpy = True
except ImportError:
    has_numpy = False

try:
    import yaml
    has_yaml = True
except ImportError:
    has_yaml = False

# Include parent path in case we are running within the tests directory
sys.path.insert(1, '../')
import f90nml
import f90nml.cli
from f90nml.fpy import pybool
from f90nml.namelist import Namelist
from f90nml.findex import FIndex


class Test(unittest.TestCase):

    def setUp(self):
        # Move to test directory if running from setup.py
        if os.path.basename(os.getcwd()) != 'tests':
            os.chdir('tests')

        # Construct the reference namelist values

        self.empty_file = {}

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
                'v_start_zero': [1, 2, 3, 4],
                'v_start_minusone': [1, 2, 3, 4, 5],
                'v_zero_adj': [1, None, 3, 4],
                'v_zero_adj_ooo': [1, None, 3, 4],
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
                'v_complex': [1+2j, 3+4j, 5+6j],
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
                'v2d_sparse': [[1, 2], [None, None], [5, 6]]
            }
        }

        self.multidim_ooo_nml = {
            'multidim_ooo_nml': {
                'a': [[1], [None, 2]],
                'b': [[1], [None, None, 3]],
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
                'v2d_sparse': [[1, None, 5], [2, None, 6]]
            }
        }

        self.dense_array_nml = {
            'sparse_array_nml': {
                'x': [
                    [1, None, None],
                    [None, None, None],
                    [None, None, 2],
                ]
            }
        }

        self.sparse_array_nml = {
            'sparse_array_nml': {
                'x': [
                    [1],
                    [],
                    [None, None, 2],
                ]
            }
        }

        self.default_one_index_nml = {
            'default_index_nml': {
                'v': [1, 2, 3, 4, 5]
            }
        }

        self.default_zero_index_nml = {
            'default_index_nml': {
                'v': [1, 2, None, 3, 4, 5]
            }
        }

        self.global_index_nml = {
            'global_index_nml': {
                'v_zero': [1, 2, 3, 4],
                'v_neg': [1, 2, 3, 4],
                'v_pos': [None, 1, 2, 3, 4]
            }
        }

        self.float_nml = {
            'float_nml': {
                'v_float': 1.,
                'v_decimal_start': .1,
                'v_decimal_end': 1.,
                'v_negative': -1.,
                'v_single': 1.,
                'v_double': 1.,
                'v_single_upper': 1.,
                'v_double_upper': 1.,
                'v_positive_index': 10.,
                'v_negative_index': 0.1,
                'v_no_exp_pos': 1.,
                'v_no_exp_neg': 1.,
                'v_no_exp_pos_dot': 1.,
                'v_no_exp_neg_dot': 1.,
                'v_neg_no_exp_pos': -1.,
                'v_neg_no_exp_neg': -1.,
                'v_pos_decimal': 0.01,
                'v_neg_decimal': -0.01,
            }
        }

        self.string_nml = {
            'string_nml': {
                'str_basic': 'hello',
                'str_no_delim': 'hello',
                'str_no_delim_token': '+hello',
                'str_no_delim_no_esc': "a''b",
                'single_esc_delim': "a 'single' delimiter",
                'double_esc_delim': 'a "double" delimiter',
                'double_nested': "''x'' \"y\"",
                'str_list': ['a', 'b', 'c'],
                'slist_no_space': ['a', 'b', 'c'],
                'slist_no_quote': ['a', 'b', 'c'],
                'slash': 'back\\slash',
            }
        }

        self.string_multiline_nml = {
            'string_multiline_nml': {
                'empty': '',
                'trailing_whitespace': '  '
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
                    'b': [{'c': 2}]     # NOTE: start_index is 2
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

        self.dtype_case_nml = {
            'dtype_mixed': {
                'b': {
                    'c_d_e': [{'id': 1}, {'id': 2}]
                }
            },
            'dtype_list_in_list': {
                'b': {
                    'c': [
                        {'id': 1},
                        {'id': 2},
                        {'id': 3},
                        {'id': 4, 'd': {'e': [10, 11]}}
                    ]
                }
            },
            'dtype_upper_scalar': {
                'b': {
                    'c': 1,
                    'd': [{'id': 2}],
                }
            },
            'dtype_upper_list': {
                'b': {
                    'c': [{'id': 1}, {'id': 2}]
                }
            },
            'dtype_index_overwrite': {
                'b': {
                    'c': [{'d': 1, 'e': 2, 'f': 3, 'g': 4, 'h': 5}]
                }
            },
            'dtype_list_staggered': {
                'b': {
                    'c': [
                        {'a': 1}, None, None, {'a': 1},
                        None, None, None, {'a': 1}
                    ]
                }
            }
        }

        self.bcast_nml = {
            'bcast_nml': {
                'x': [2.0, 2.0],
                'y': [None, None, None],
                'z': [True, True, True, True],
            },
            'bcast_nml_comma': {
                'x': [2.0, 2.0],
                'y': [None, None, None],
                'z': [True, True, True, True],
            },
            'bcast_endnull_nml': {
                'x': [2.0, 2.0],
                'y': [None, None, None],
            },
            'bcast_endnull_nml_comma': {
                'x': [2.0, 2.0],
                'y': [None, None, None],
            },
            'bcast_mixed_nml': {
                'x': [1, 1, 1, 2, 3, 4],
                'y': [1, 1, 1, 2, 2, 3],
            },
            'bcast_mixed_null_nml': {
                'x': [1, None, None, None, 3, 4],
                'y': [1, 1, 1, None, None, None, 3, 4],
                'z': [1, None, None, None, None, 4],
            },
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

        self.list_patch_nml = {
            'list_patch_nml': {
                'x': ['1', '2', '3', '4', '5']
            }
        }

        self.repatch_nml = {
            'repatch_nml': {
                'x': [5, 6],
                'y': {'z': 7}
            }
        }

        self.winfmt_nml = {'blah': {'blah': 1}}

        self.extern_cmt_nml = {
            'efitin': {
                'abc': 0,
            }
        }

        self.ieee_nml = {
            'ieee_nml': {
                'base_inf': float('inf'),
                'neg_inf': float('-inf'),
                'plus_inf': float('inf'),
                'base_nan': float('nan'),
                'plus_nan': float('nan'),
                'neg_nan': float('nan'),
            }
        }

        if has_numpy:
            self.numpy_nml = {
                'numpy_nml': OrderedDict((
                        ('np_integer', numpy.int64(1)),
                        ('np_float', numpy.float64(1.0)),
                        ('np_complex', numpy.complex128(1+2j)),
                    )
                )
            }

        if os.path.isfile('tmp.nml'):
            os.remove('tmp.nml')

    # Support functions
    def assert_file_equal(self, source_fname, target_fname):
        with open(source_fname) as source:
            with open(target_fname) as target:
                source_str = source.read()
                target_str = target.read()
                self.assertEqual(source_str, target_str)

    def assert_write(self, nml, target_fname, sort=False):
        self.assert_write_path(nml, target_fname, sort)
        self.assert_write_file(nml, target_fname, sort)

    def assert_write_path(self, nml, target_fname, sort=False):
        tmp_fname = 'tmp.nml'
        f90nml.write(nml, tmp_fname, sort=sort)
        try:
            self.assert_file_equal(tmp_fname, target_fname)
        finally:
            os.remove(tmp_fname)

    def assert_write_file(self, nml, target_fname, sort=False):
        tmp_fname = 'tmp.nml'
        with open(tmp_fname, 'w') as tmp_file:
            f90nml.write(nml, tmp_file, sort=sort)
            self.assertFalse(tmp_file.closed)
        try:
            self.assert_file_equal(tmp_fname, target_fname)
        finally:
            os.remove(tmp_fname)

    def get_cli_output(self, args, get_stderr=False):
        argv_in, stdout_in, stderr_in = sys.argv, sys.stdout, sys.stderr

        sys.argv = args
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        try:
            f90nml.cli.parse()
        except SystemExit:
            pass

        sys.stdout.seek(0)
        stdout = sys.stdout.read()
        sys.stdout.close()

        sys.stderr.seek(0)
        stderr = sys.stderr.read()
        sys.stderr.close()

        sys.argv, sys.stdout, sys.stderr = argv_in, stdout_in, stderr_in

        # TODO: Some way to check both would be more useful...
        if get_stderr:
            return stderr
        else:
            return stdout

    # Tests
    def test_empty_file(self):
        test_nml = f90nml.read('empty_file')
        self.assertEqual(self.empty_file, test_nml)

    def test_empty_nml(self):
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

    def test_vector_default_index(self):
        test_nml = f90nml.read('vector.nml')
        test_nml.default_start_index = 2
        self.assertEqual(self.vector_nml, test_nml)
        self.assert_write(test_nml, 'vector_default_idx.nml')

    def test_multidim(self):
        test_nml = f90nml.read('multidim.nml')
        self.assertEqual(self.multidim_nml, test_nml)
        self.assert_write(test_nml, 'multidim_target.nml')

    def test_multidim_ooo(self):
        test_nml = f90nml.read('multidim_ooo.nml')
        self.assertEqual(self.multidim_ooo_nml, test_nml)
        self.assert_write(test_nml, 'multidim_ooo_target.nml')

    def test_rowmaj_multidim(self):
        parser = f90nml.Parser()
        parser.row_major = True
        test_nml = parser.read('multidim.nml')
        self.assertEqual(self.md_rowmaj_nml, test_nml)

    def test_dense_arrays(self):
        parser = f90nml.Parser()
        test_nml = parser.read('sparse_array.nml')
        self.assertEqual(self.dense_array_nml, test_nml)

    def test_sparse_arrays(self):
        parser = f90nml.Parser()
        parser.sparse_arrays = True
        test_nml = parser.read('sparse_array.nml')
        self.assertEqual(self.sparse_array_nml, test_nml)

    def test_vector_too_long(self):
        sys_stderr = sys.stderr
        sys.stderr = StringIO()
        test_nml = f90nml.read('values_exceed_index.nml')
        # TODO: Check values
        sys.stderr = sys_stderr

    def test_parser_property_invalid(self):
        parser = f90nml.Parser()
        self.assertRaises(TypeError, setattr, parser, 'comment_tokens', 123)
        self.assertRaises(TypeError, setattr, parser,
                          'default_start_index', 'abc')
        self.assertRaises(TypeError, setattr, parser, 'sparse_arrays', 'abc')
        self.assertRaises(TypeError, setattr, parser,
                          'global_start_index', 'abc')
        self.assertRaises(TypeError, setattr, parser, 'row_major', 'abc')
        self.assertRaises(TypeError, setattr, parser, 'strict_logical', 'abc')

    def test_float(self):
        test_nml = f90nml.read('float.nml')
        self.assertEqual(self.float_nml, test_nml)
        self.assert_write(test_nml, 'float_target.nml')

    def test_string(self):
        test_nml = f90nml.read('string.nml')
        self.assertEqual(self.string_nml, test_nml)
        self.assert_write(test_nml, 'string_target.nml')

    def test_string_multiline(self):
        test_nml = f90nml.read('string_multiline.nml')
        self.assertEqual(self.string_multiline_nml, test_nml)

    def test_dtype(self):
        test_nml = f90nml.read('dtype.nml')
        self.assertEqual(self.dtype_nml, test_nml)
        self.assert_write(test_nml, 'dtype_target.nml')

    def test_ieee(self):
        test_nml = f90nml.read('ieee.nml')

        # NaN values cannot be tested for equality, so explicitly test values
        self.assertTrue(set(test_nml) == set(self.ieee_nml))
        for grp in test_nml:
            self.assertTrue(set(test_nml[grp]) == set(self.ieee_nml[grp]))
            for key in test_nml[grp]:
                ieee_grp, test_grp = self.ieee_nml[grp], test_nml[grp]
                if key.endswith('_nan'):
                    self.assertTrue(math.isnan(test_grp[key]))
                else:
                    self.assertTrue(ieee_grp[key], test_grp[key])

        self.assert_write(test_nml, 'ieee_target.nml')

    def test_dtype_case(self):
        test_nml = f90nml.read('dtype_case.nml')
        self.assertEqual(self.dtype_case_nml, test_nml)
        self.assert_write(test_nml, 'dtype_case_target.nml')

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

    def test_multiline_index(self):
        test_nml = f90nml.read('multiline_index.nml')
        self.assertEqual(self.multiline_nml, test_nml)
        self.assert_write(test_nml, 'multiline_index.nml')

    def test_long_varname(self):
        test_nml = f90nml.read('types.nml')
        test_nml.column_width = 10
        self.assert_write(test_nml, 'types.nml')

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

    def test_patch_paths(self):
        patch_nml = f90nml.read('types_patch.nml')
        f90nml.patch('types.nml', patch_nml, 'tmp.nml')
        test_nml = f90nml.read('tmp.nml')
        try:
            self.assertEqual(test_nml, patch_nml)
        finally:
            os.remove('tmp.nml')

    def test_patch_files(self):
        patch_nml = f90nml.read('types_patch.nml')
        with open('types.nml') as f_in:
            with open('tmp.nml', 'w') as f_out:
                f90nml.patch(f_in, patch_nml, f_out)
                self.assertFalse(f_in.closed)
                self.assertFalse(f_out.closed)
        try:
            test_nml = f90nml.read('tmp.nml')
            self.assertEqual(test_nml, patch_nml)
        finally:
            os.remove('tmp.nml')

    def test_patch_case(self):
        patch_nml = f90nml.read('types_patch.nml')
        f90nml.patch('types_uppercase.nml', patch_nml, 'tmp.nml')
        test_nml = f90nml.read('tmp.nml')
        try:
            self.assertEqual(test_nml, patch_nml)
        finally:
            os.remove('tmp.nml')

    def test_patch_typeerror(self):
        self.assertRaises(TypeError, f90nml.patch, 'types.nml', 'xyz',
                          'tmp.nml')

    def test_patch_list(self):
        f90nml.patch('list_patch.nml', self.list_patch_nml, 'tmp.nml')
        test_nml = f90nml.read('tmp.nml')
        try:
            self.assertEqual(test_nml, self.list_patch_nml)
        finally:
            os.remove('tmp.nml')

    def test_repatch(self):
        f90nml.patch('repatch.nml', self.repatch_nml, 'tmp.nml')
        test_nml = f90nml.read('tmp.nml')
        try:
            self.assertEqual(test_nml, self.repatch_nml)
        finally:
            os.remove('tmp.nml')

    def test_default_patch(self):
        patch_nml = f90nml.read('types_patch.nml')
        f90nml.patch('types.nml', patch_nml)
        test_nml = f90nml.read('types.nml~')
        try:
            self.assertEqual(test_nml, patch_nml)
        finally:
            os.remove('types.nml~')

        # The above behavior is only for paths, not files
        with open('types.nml') as nml_file:
            self.assertRaises(ValueError, f90nml.patch, nml_file, patch_nml)

    def test_patch_null(self):
        try:
            f90nml.patch('types.nml', {}, 'tmp.nml')
            self.assert_file_equal('types.nml', 'tmp.nml')
        finally:
            os.remove('tmp.nml')

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

    def test_parser_default_index(self):
        parser = f90nml.Parser()

        parser.default_start_index = 1
        test_nml = parser.read('default_index.nml')
        self.assertEqual(self.default_one_index_nml, test_nml)

        parser.default_start_index = 0
        test_nml = parser.read('default_index.nml')
        self.assertEqual(self.default_zero_index_nml, test_nml)

    def test_global_index(self):
        parser = f90nml.Parser()
        parser.global_start_index = 1
        test_nml = parser.read('global_index.nml')
        self.assertEqual(self.global_index_nml, test_nml)

    def test_namelist_default_index(self):
        d = {'x_nml': {'x': [1, 2, 3]}}
        test_nml = f90nml.Namelist(d, default_start_index=1)
        # TODO: Check value

    def test_index_syntax(self):
        self.assertRaises(ValueError, f90nml.read, 'index_empty.nml')
        self.assertRaises(ValueError, f90nml.read, 'index_bad.nml')
        self.assertRaises(ValueError, f90nml.read, 'index_bad_start.nml')
        self.assertRaises(ValueError, f90nml.read, 'index_empty_end.nml')
        self.assertRaises(ValueError, f90nml.read, 'index_bad_end.nml')
        self.assertRaises(ValueError, f90nml.read, 'index_empty_stride.nml')
        self.assertRaises(ValueError, f90nml.read, 'index_bad_stride.nml')
        self.assertRaises(ValueError, f90nml.read, 'index_zero_stride.nml')

    def test_bad_start_index(self):
        nml = Namelist()
        self.assertRaises(TypeError, setattr, nml, 'start_index', 'abc')
        self.assertRaises(TypeError, setattr, nml, 'default_start_index',
                          'abc')

    def test_iter_in_getitem(self):
        d = {'a': {'b': 1.}}
        nml = Namelist(d)
        self.assertEqual(nml[('a', 'b')], 1.)
        self.assertEqual(nml[['a', 'b']], 1.)
        self.assertEqual(nml['a']['b'], 1.)

    def test_groups(self):
        d = {'a': {'b': 1.}}
        nml = Namelist(d)
        key, value = next(nml.groups())
        self.assertEqual(key, ('a', 'b'))
        self.assertEqual(value, 1.)

    def test_f90repr(self):
        nml = Namelist()
        self.assertEqual(nml._f90repr(1), '1')
        self.assertEqual(nml._f90repr(1.), '1.0')
        self.assertEqual(nml._f90repr(1+2j), '(1.0, 2.0)')
        self.assertEqual(nml._f90repr(True), '.true.')
        self.assertEqual(nml._f90repr(False), '.false.')
        self.assertEqual(nml._f90repr('abc'), "'abc'")

        for ptype in ({}, [], set()):
            self.assertRaises(ValueError, nml._f90repr, ptype)

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

    def test_column_width(self):
        test_nml = f90nml.read('multiline.nml')
        test_nml.column_width = 40
        self.assert_write(test_nml, 'multiline_colwidth.nml')

        self.assertRaises(ValueError, setattr, test_nml, 'column_width', -1)
        self.assertRaises(TypeError, setattr, test_nml, 'column_width', 'xyz')

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

    def test_float_format(self):
        test_nml = f90nml.read('float.nml')
        test_nml.float_format = '.3f'
        self.assert_write(test_nml, 'float_format.nml')

        self.assertRaises(TypeError, setattr, test_nml, 'float_format', 123)

    def test_logical_repr(self):
        parser = f90nml.Parser()
        parser.strict_logical = False
        test_nml = parser.read('logical.nml')
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

    def test_dict_assign(self):
        test_nml = f90nml.Namelist()
        test_nml['dict_group'] = {'a': 1, 'b': 2}
        try:
            test_nml.write('tmp.nml')
        finally:
            os.remove('tmp.nml')

    def test_winfmt(self):
        test_nml = f90nml.read('winfmt.nml')
        self.assertEqual(self.winfmt_nml, test_nml)

    def test_eof_no_cr(self):
        test_nml = f90nml.read('no_eol_in_eof.nml')
        # TODO: Test values

    def test_namelist_patch(self):
        nml = f90nml.Namelist({
            'a_nml': {
                'x': 1,
                'y': 2,
            }
        })

        # Check overwriting values
        nml.patch({'a_nml': {'x': 3}})

        self.assertEqual(nml['a_nml']['x'], 3)
        self.assertEqual(nml['a_nml']['y'], 2)

        # Check appending values doesn't remove previous
        nml.patch({'a_nml': {'z': 5}})

        self.assertEqual(nml['a_nml']['x'], 3)
        self.assertEqual(nml['a_nml']['y'], 2)
        self.assertEqual(nml['a_nml']['z'], 5)

        # Check adding a new section also works
        nml.patch({
            'b_nml': {'q': 33},
            'a_nml': {'z': 4}
        })

        self.assertEqual(nml['a_nml']['z'], 4)
        self.assertEqual(nml['b_nml']['q'], 33)
        self.assertRaises(KeyError, nml['b_nml'].__getitem__, 'z')

    def test_sorted_output(self):
        test_nml = f90nml.read('types.nml')
        self.assert_write(test_nml, 'types_sorted.nml', sort=True)

    def test_extern_cmt(self):
        test_nml = f90nml.read('extern_cmt.nml')
        self.assertEqual(self.extern_cmt_nml, test_nml)

    def test_print_nml(self):
        nml = f90nml.read('types.nml')

        stdout = StringIO()
        print(nml, file=stdout)
        stdout.seek(0)
        source_str = stdout.read()
        stdout.close()

        with open('types.nml') as target:
            target_str = target.read()

        self.assertEqual(source_str, target_str)

    def test_print_group(self):
        nml = f90nml.read('types.nml')

        stdout = StringIO()
        print(nml['types_nml'], file=stdout)
        stdout.seek(0)
        source_str = stdout.read().rstrip('\n')
        stdout.close()

        target_str = repr(nml['types_nml'])

        self.assertEqual(source_str, target_str)

    def test_gen_dtype(self):
        d = {'dtype_nml': {'a': [{'b': 1, 'c': 2}, {'b': 3, 'c': 4}]}}
        nml = f90nml.Namelist(d)
        out = StringIO()
        print(nml, file=out)
        # TODO: Check output
        out.close()

    def test_gen_multidim(self):
        d = {'md_nml': {'x': [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}}
        nml = f90nml.Namelist(d)
        out = StringIO()
        print(nml, file=out)
        # TODO: Check output
        out.close()

    if has_numpy:
        def test_numpy_write(self):
            self.assert_write(self.numpy_nml, 'numpy_types.nml')

    # CLI tests
    def test_cli_help(self):
        cmd = ['f90nml']
        self.get_cli_output(cmd)

    def test_cli_read(self):
        cmd = ['f90nml', 'types.nml']
        source_str = self.get_cli_output(cmd)

        with open('types.nml') as target:
            target_str = target.read()
            self.assertEqual(source_str, target_str)

    def test_cli_gen(self):
        cmd = ['f90nml', '-g', 'gen_nml', '-v', 'x=1']
        source_str = self.get_cli_output(cmd)

        with open('gen.nml') as target:
            target_str = target.read()

        self.assertEqual(source_str, target_str)

    def test_cli_replace(self):
        cmd = ['f90nml', '-g', 'types_nml', '-v', 'v_integer=5',
               '-v', 'v_logical=.false.', 'types.nml']
        source_str = self.get_cli_output(cmd)

        with open('types_cli_set.nml') as target:
            target_str = target.read()

        self.assertEqual(source_str, target_str)

    def test_cli_replace_no_group(self):
        cmd = ['f90nml', '-v', 'v_integer=5', '-v', 'v_logical=.false.',
               'types.nml']
        source_str = self.get_cli_output(cmd)

        # TODO: Check stderr
        error_str = ("f90nml: warning: Assuming variables are in group "
                     "'types_nml'.\n")

        with open('types_cli_set.nml') as target:
            target_str = target.read()
            self.assertEqual(source_str, target_str)

    def test_cli_replace_write(self):
        cmd = ['f90nml', '-g', 'types_nml', '-v', 'v_integer=5',
               '-v', 'v_logical=.false.', 'types.nml', 'tmp.nml']
        self.get_cli_output(cmd)

        with open('tmp.nml') as source:
            with open('types_cli_set.nml') as target:
                source_str = source.read()
                target_str = target.read()

        self.assertEqual(source_str, target_str)

    def test_cli_patch(self):
        cmd = ['f90nml', '-p', '-g', 'comment_nml', '-v', 'v_cmt_inline=456',
               'comment.nml']
        source_str = self.get_cli_output(cmd)

        with open('comment_patch.nml') as target:
            target_str = target.read()

        self.assertEqual(source_str, target_str)

    def test_cli_bad_format(self):
        cmd = ['f90nml', '-f', 'blah', 'types.nml']
        source_str = self.get_cli_output(cmd, get_stderr=True)
        # TODO: Automate the format list
        target_str = ("f90nml: error: format must be one of the following: "
                      "('json', 'yaml', 'nml')\n")

        self.assertEqual(source_str, target_str)

    def test_cli_json_write(self):
        cmd = ['f90nml', 'types.nml', 'tmp.json']
        out = self.get_cli_output(cmd)

        self.assert_file_equal('types.json', 'tmp.json')

        # TODO: These are just throwaway tests that need to be moved after the
        # sorting issues have been sorted
        cmd = ['f90nml', 'vector.nml', 'tmp.json']
        out = self.get_cli_output(cmd)

        cmd = ['f90nml', 'dtype.nml', 'tmp.json']
        out = self.get_cli_output(cmd)

        os.remove('tmp.json')

    def test_cli_json_fmt(self):
        cmd = ['f90nml', '-f', 'json', 'types.nml']
        source_str = self.get_cli_output(cmd)

        with open('types.json') as target:
            target_str = target.read()

        self.assertEqual(source_str, target_str)

    def test_cli_json_read(self):
        cmd = ['f90nml', 'types.json']
        source_str = self.get_cli_output(cmd)
        # TODO: Check output after resolving the ordering issue

        # Quickly test some of the list features
        cmd = ['f90nml', 'vector.json']
        source_str = self.get_cli_output(cmd)

    def test_cli_json_patch_fail(self):
        error_str = 'f90nml: error: Only namelist files can be patched.\n'

        # JSON input patch
        cmd = ['f90nml', '-p', '-v', 'steps=432', 'types.json']
        source_str = self.get_cli_output(cmd, get_stderr=True)
        self.assertEqual(source_str, error_str)

        # JSON output patch
        cmd = ['f90nml', '-p', '-v', 'steps=432', 'config.nml', 'tmp.json']
        source_str = self.get_cli_output(cmd, get_stderr=True)
        self.assertEqual(source_str, error_str)

    if has_yaml:
        def test_cli_yaml_write(self):
            cmd = ['f90nml', 'types.nml', 'tmp.yaml']
            out = self.get_cli_output(cmd)

            self.assert_file_equal('types.yaml', 'tmp.yaml')
            os.remove('tmp.yaml')

        def test_cli_yaml_read(self):
            cmd = ['f90nml', 'types.yaml']
            source_str = self.get_cli_output(cmd)
            # TODO: Check output after resolving the ordering issue

    def test_cli_missing_yaml(self):
        orig_has_yaml = f90nml.cli.has_yaml
        f90nml.cli.has_yaml = False

        cmd = ['f90nml', 'types.yaml']
        source_str = self.get_cli_output(cmd, get_stderr=True)

        target_str = ('f90nml: error: YAML module could not be found.\n'
            '  To enable YAML support, install PyYAML or use the f90nml[yaml] '
            'package.\n')
        self.assertEqual(source_str, target_str)

        f90nml.cli.has_yaml = orig_has_yaml


if __name__ == '__main__':
    if os.path.isfile('tmp.nml'):
        os.remove('tmp.nml')
    unittest.main()
