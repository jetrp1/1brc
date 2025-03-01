#!/bin/env python3

def calc_average(file_name):
    result_avg = {}
    result_min = {}
    result_max = {}
    result_count = {}
    station_names = set()

    with open(file_name, 'r') as dataset:
        for record in dataset:
            station, value = record.split(',')

            if station not in station_names:
                station_names.add(station)
                result_avg[station] = value
                result_min[station] = value
                result_max[station] = value
                result_count[station] = 1

            result_count[station] += 1
            result_avg[station] += value

            if result_max[station] < value:
                result_max[station] = value

            if result_min[station] > value:
                result_min[station] = value
    
    results = '{'

    for station in station_names:
        results.append(f'{station}={result_min[station]}/{result_avg[station]/result_count[station]:.1f}/{result_max[station]}, ')

    results.append('}')

    print(results)        


if __name__ == '__main__':
    from argparse import ArgumentParser, FileType
    
    parser = ArgumentParser('calculate_average_baseline.py')
    parser.add_argument('infile', type=str)
    args = parser.parse_args()

    calc_average()