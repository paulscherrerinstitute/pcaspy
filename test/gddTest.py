import pcaspy

import numpy

import unittest

class TestGDD(unittest.TestCase):
    def setUp(self):
        self.s = pcaspy.gdd()
    def test_string(self):
        self.s.put("sdcsd")
        self.assertEqual(self.s.get(), "sdcsd")

    def test_numeric(self):
        self.s.put(12)
        self.assertEqual(self.s.get(), 12)

    def test_string_array(self):
        self.s.put(["sdcsd","sdcsd"])
        self.assertEqual(self.s.get(), ["sdcsd","sdcsd"])

    def test_numeric_array(self):
        self.s.put(range(2))
        self.assertEqual(self.s.get(), [0,1])

    def test_numpy_scaler(self):
        self.s.put(numpy.int32(12))
        self.assertEqual(self.s.get(), 12)

    def test_numpy_array(self):
        self.s.put(numpy.arange(2))
        self.assertEqual(self.s.get(), [0, 1])

    def test_dim_enlarge(self):
        self.s.put(1)
        self.assertEqual(self.s.get(), 1)

        self.s.put(range(2))
        self.assertEqual(self.s.get(), [0, 1])

    def test_convert_to_numeric(self):
        self.s.put(1)
        self.assertEqual(self.s.get(), 1)

        self.s.put('2')
        self.assertEqual(self.s.get(), 2)

        self.s.put('qwf')
        self.assertEqual(self.s.get(), 2)

    def test_convert_to_string(self):
        self.s.put('sdcsd')
        self.assertEqual(self.s.get(), 'sdcsd')
        
        self.s.put(2)
        self.assertEqual(float(self.s.get()), 2)

    def test_char_array(self):
        self.s.setPrimType(pcaspy.aitEnumUint8)
        self.s.put('asddfff')
        self.assertEqual(self.s.get(), 'asddfff')

    def test_char_scaler(self):
        self.s.setPrimType(pcaspy.aitEnumUint8)
        self.s.put('a')
        self.assertEqual(self.s.get(), 'a')

    def tearDown(self):
        del self.s

if __name__ == '__main__':
    unittest.main()

