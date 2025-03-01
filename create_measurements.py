#!/bin/env python3

import random
import sys

CITIES_FILE_PATH = 'data/simplemaps_worldcities_basicv1.77/worldcities.csv'

def progress_bar(iteration, total, prefix='', suffix='', length=30, fill='█'):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} {bar} {percent}% {suffix}')
    sys.stdout.flush()


def get_city_names() -> list:
    cities = []

    with open(CITIES_FILE_PATH, 'r') as cities_file:
        # skip header
        cities_file.readline()

        for line in cities_file:
            fields = line.split(',')
            city = fields[1].strip('"')
            cities.append(city)
    
    return cities


r = random.Random()
def get_temp_string() -> str:
    temp = r.random() * 100
    return f'{temp:.3}'


def build_file(file, num_rows: int, num_keys: int, quiet):
    UPDATE_FREQ = num_rows/1000

    # get a list of Keys
    keys = get_city_names()

    with open(file, 'w', buffering=4096 * 10000) as outFile:

        # generate the data
        for i in range(num_rows):
            city = random.choice(keys)
            temp = get_temp_string()
            outFile.write(f'{city},{temp}\n')
           
            if not quiet and i % UPDATE_FREQ == 0: 
                progress_bar(i, num_rows-1, prefix='Progress:', length=100)
            

# This should simply call the generate function. There shouldn't be any real functionality here except for what is needed to make the CLI function
if __name__ == '__main__':
    from argparse import ArgumentParser
    
    parser = ArgumentParser('create_measurements.py')
    parser.add_argument('rows', type=int, help='Number of Rows to generate')
    parser.add_argument('-k', '--keys', type=int, help='Number of Keys to use')
    parser.add_argument('-q', '--quiet', action='store_true')
    parser.add_argument('outfile', type=str)
    args = parser.parse_args()

    build_file(args.outfile, args.rows, args.keys, args.quiet)

    if not args.quiet:
        print()