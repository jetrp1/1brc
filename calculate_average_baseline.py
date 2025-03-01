import sys

def calc_average(file_name):
    with open(file_name, 'r') as dataset:
        



if __name__ == '__main__':
    from argparse import ArgumentParser, FileType
    
    parser = ArgumentParser('calculate_average_baseline.py')
    parser.add_argument('infile', type=str)
    args = parser.parse_args()

    calc_average()