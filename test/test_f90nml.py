import sys
import unittest

sys.path.append('../')
import f90nml

class Test(unittest.TestCase):

    def setUp(self):
        self.empty_nml = {'empty_nml': {}}
        self.types_nml = {'types_nml':
                            {'v_integer': 1,
                             'v_float': 1.0,
                             'v_complex': 1+2j,
                             'v_logical': True,
                             'v_string': 'Hello',
                            }
                          }

        self.vector_nml = {'vector_nml':
                            {'v': [1, 2, 3, 4, 5],
                             'v_idx': [1, 2, 3, 4],
                             'v_idx_ooo': [1, 2, 3, 4],
                             'v_range': [1, 2, 3, 4],
                             'v_implicit_start': [1, 2, 3, 4],
                             'v_implicit_end': [1, 2, 3, 4],
                             'v_implicit_all': [1, 2, 3, 4],
                             'v_null_start': [None, 2, 3, 4],
                             'v_null_interior': [1, 2, None, 4],
                             'v_null_end': [1, 2, 3, None],
                            }
                          }


    def test_empty(self):
        test_nml = f90nml.read('empty.nml')
        self.assertEqual(self.empty_nml, test_nml)

    def test_types(self):
        test_nml = f90nml.read('types.nml')
        self.assertEqual(self.types_nml, test_nml)

    def test_vector(self):
        test_nml = f90nml.read('vector.nml')
        self.assertEqual(self.vector_nml, test_nml)


if __name__ == '__main__':
    unittest.main()
