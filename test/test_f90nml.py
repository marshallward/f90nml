import sys
import unittest

sys.path.append('../')
import f90nml

class Test(unittest.TestCase):

    def setUp(self):
        self.empty_nml = {'empty_nml': {}}

    def test_empty(self):
        test_nml = f90nml.read('empty.nml')
        self.assertTrue(self.empty_nml, test_nml)

if __name__ == '__main__':
    unittest.main()
