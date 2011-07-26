import pcaspy


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
        self.s.setPrimType(pcaspy.aitEnumString)
        self.s.put(["sdcsd","sdcsd"])
        self.assertEqual(self.s.get(), ["sdcsd","sdcsd"])

    def test_numeric_array(self):
        self.s.put(list(range(2)))
        print(self.s.get())
        self.assertEqual(self.s.get(), [0.0,1.0])

    def tearDown(self):
        del self.s

if __name__ == '__main__':
    unittest.main()

