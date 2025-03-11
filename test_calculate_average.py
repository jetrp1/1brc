import unittest
import calculate_average


class TestCalculateAverage(unittest.TestCase):
    def setUp(self):
        self.lines = [
            b'stationA,-10.4\n',
            b'stationA,-1.2\n',
            b'stationA,14.2\n',
            b'stationB,5.0\n',
            b'stationB,10.0\n',
            b'stationB,15.0\n',
        ]


    def test_to_int(self):
        self.assertEqual(calculate_average.to_int(b'-14.5'),-145)
        self.assertEqual(calculate_average.to_int(b'-1.5'),-15)
        self.assertEqual(calculate_average.to_int(b'14.5'),145)
        self.assertEqual(calculate_average.to_int(b'00.0'),0)
        
    
    def test_process_line(self):
        measurements = {}
        calculate_average.process_line(self.lines[0], measurements)

        result = {b'stationA':[-104,-104,-104,1]}
        self.assertDictEqual(measurements, result)

        calculate_average.process_line(self.lines[1], measurements)
        result = {b'stationA':[-104,-116,-12,2]}
        self.assertDictEqual(measurements, result)

        calculate_average.process_line(self.lines[2], measurements)
        result = {b'stationA':[-104,26,142,3]}
        self.assertDictEqual(measurements, result)

        calculate_average.process_line(self.lines[3], measurements)
        result = {b'stationA':[-104,26,142,3], b'stationB':[50,50,50,1]}
        self.assertDictEqual(measurements, result)
        
        calculate_average.process_line(self.lines[4], measurements)
        result = {b'stationA':[-104,26,142,3], b'stationB':[50,150,100,2]}
        self.assertDictEqual(measurements, result)
        
        calculate_average.process_line(self.lines[5], measurements)
        result = {b'stationA':[-104,26,142,3], b'stationB':[50,300,150,3]}
        self.assertDictEqual(measurements, result)

    def test_align_offset(self):
        self.assertEqual(calculate_average.align_offset(5142, 4096),4096)
        self.assertEqual(calculate_average.align_offset(1248, 4096),0)
        self.assertEqual(calculate_average.align_offset(9825, 4096),8192)

    def test_combine_results(self):
        result_list = [{b'stationA':[-104,26,142,3], b'stationB':[50,300,150,3], b'stationC':[12,51,45,1]},
                       {b'stationA':[20,301,152,7], b'stationB':[50,300,150,3]}]
        result = {b'stationA':[-104,327,152,10], b'stationB':[50,600,150,6], b'stationC':[12,51,45,1]}

        self.assertDictEqual(calculate_average.combine_results(result_list), result)

    # should i test the dispatcher? If so How do i test the dispatcher?



if __name__ == '__main__':
    unittest.main()