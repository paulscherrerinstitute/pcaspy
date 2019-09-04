from pcaspy import cas

try:
    import numpy
except ImportError:
    print('Skipping numpy tests')
    numpy = None

import unittest

class TestGDD(unittest.TestCase):
    def setUp(self):
        self.s = cas.gdd()

    def test_copy(self):
        d = cas.gdd()
        d.put([1,2,3,4])
        self.s.put(d)
        self.assertEqual(self.s.get(), [1,2,3,4])

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
        if numpy is None:
            return
        self.s.put(numpy.int32(12))
        self.assertEqual(self.s.get(), 12)

    def test_numpy_array(self):
        if numpy is None:
            return
        self.s.put(numpy.arange(2, dtype='i4'))
        self.assertEqual(self.s.get(), [0, 1])

    def test_numpy_unsupported_dtype(self):
        if numpy is None:
            return
        self.s.put(numpy.arange(2, dtype='i8'))
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

    def test_string_to_char_array(self):
        self.s.setPrimType(cas.aitEnumUint8)
        self.s.setDimension(1)
        self.s.setBound(0, 0, 10)
        self.s.put('sdcsd')
        self.assertEqual(self.s.get(), 'sdcsd')
        self.s.put('')
        self.assertEqual(self.s.get(), '')

    def test_string_to_numeric_scalar(self):
        self.s.setPrimType(cas.aitEnumUint16)
        self.s.put('sc') # no conversion, 0
        self.assertEqual(self.s.get(), 0)
        self.s.put('a')  # heximal 10
        self.assertEqual(self.s.get(), 10)
        self.s.put('10') # decimal 10
        self.assertEqual(self.s.get(), 10)

    def tearDown(self):
        del self.s

if __name__ == '__main__':
    unittest.main()
