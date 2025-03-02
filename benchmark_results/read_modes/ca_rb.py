# Written by Ryan Peel

def print_measurements(measurements: dict):
    results = '{'

    for station in measurements.keys():
        min, sum, max, count = measurements[station]
        results += f'{station}={min}/{sum/count:.1f}/{max}, '
    
    results += '}'

    print(results)


def calc_average(file_name):
    measurements = dict()
    # key: [min,sum,max,count]
    
    with open(file_name, 'r') as dataset:
        for record in dataset:
            station, value = record.split(',')
            value = float(value)

            # get current record
            if station in measurements:
                measurements[station][1] += value
                measurements[station][3] += 1

                # Min
                measurements[station][0] = min(measurements[station][0], value)

                # Max
                measurements[station][2] = max(measurements[station][2], value)

            # First time we add to the list
            else:
                measurements[station] = [value, value, value, 1]

    return measurements


if __name__ == '__main__':
    from argparse import ArgumentParser, FileType
    
    parser = ArgumentParser('calculate_average_baseline.py')
    parser.add_argument('infile', type=str)
    parser.add_argument('-c', '--core_count', type=int, required=False, help='Specify the number of cores to use in processing')
    parser.add_argument('-s', '--single_core', action='store_true', help='Sets the system to be single threaded operation')
    args = parser.parse_args()

#    print_measurements(calc_average(args.infile))

    with open(args.infile, 'rb') as file:
        line = file.readline()
        while line:
            line = file.readline()
