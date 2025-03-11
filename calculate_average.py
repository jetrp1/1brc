# Written by Ryan Peel
from multiprocessing import Pool
import os
import mmap

MMAP_PAGE_SIZE = os.sysconf("SC_PAGE_SIZE")

def print_measurements(measurements: dict):
    results = '{'

    for station in measurements.keys():
        min, sum, max, count = measurements[station]
        results += f'{station.decode()}={min/10:.1f}/{sum/10/count:.1f}/{max/10:.1f}, '
    
    results += '}'

    print(results)

# Could this be done in parallel?
# wouls that really have any real improvement?
def combine_results(results):
    final = {}
    for result in results:
        for station, record in result.items():
                if station in final:
                    final[station][0] = min(final[station][0], record[0])
                    final[station][1] = final[station][1] + record[1]
                    final[station][2] = max(final[station][2], record[2])
                    final[station][3] = final[station][3] + record[3]
                else:
                    final[station] = record

    return final

def dispatcher(file_name, thread_count):
    file_size = os.path.getsize(file_name)

    if thread_count == 1:
        final_results = calc_average_block(file_name, 0, file_size)
    else:
        chunk_size = file_size // thread_count
        with open(file_name, 'r+b') as f:
            with mmap.mmap(
                f.fileno(), 0, access=mmap.ACCESS_READ
            ) as mapped_file:
                
                chunk_start = 0
                chunk_list = []

                while chunk_start < file_size:
                    chunk_end = min(file_size, chunk_start + chunk_size)
                    chunk_end = mapped_file.find(b'\n', chunk_end)
                    if chunk_end == -1:
                        chunk_end = file_size
                    else: 
                        chunk_end = chunk_end + 1

                    chunk_list.append([file_name, chunk_start, chunk_end])
                    chunk_start = chunk_end

                # Start each process
        with Pool(processes=thread_count) as pool:
            results = pool.starmap(calc_average_block, chunk_list)

            final_results = combine_results(results)
    
    return final_results
 
def align_offset(offset, page_size):
    return (offset // page_size) * page_size


def calc_average_block(file_name, chunk_start, chunk_end):
    # We get OS Errors if we are not aligned to the system page sizes
    offset = align_offset(chunk_start, MMAP_PAGE_SIZE)
    measurements = {}

    with open(file_name, 'rb') as f:
        length = chunk_end - offset

        with mmap.mmap(
            f.fileno(), length, access=mmap.ACCESS_READ, offset=offset 
        ) as maped_file:
            # Get aligned with the first line
            maped_file.seek(chunk_start - offset)

            # this is putting a blank line on the end of the file
            for line in iter(maped_file.readline, b""):
                process_line(line, measurements)
    
    return measurements


def process_line(line, measurements):
    comma_idx = line.find(b',')
    station = line[:comma_idx] 

    # get value as int
    value = to_int(line[comma_idx+1:-1])

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

def to_int(x: bytes) -> int:
    # Parse sign
    if x[0] == 45:
        sign = -1
        idx = 1
    else:
        sign = 1
        idx = 0
        
    # -1 will always be the idx of the decimal
    # maybe this is not true from the dataset in the main script but it is in mine.
    # type bytes cannot be added to the result, we have to do each value one at a time

    # parse value before decimal
    if x[idx+1] == 46: # one digit decimal
        return sign * (((x[idx]-48) * 10) + (x[idx+2] - 48))
    else:
        return sign * (((x[idx]-48) * 100) + ((x[idx+1]-48) * 10) + (x[idx+3] - 48))

if __name__ == '__main__':
    from argparse import ArgumentParser, FileType
    
    parser = ArgumentParser('calculate_average_baseline.py')
    parser.add_argument('infile', type=str)
    parser.add_argument('-c', '--core_count', type=int, required=False, help='Specify the number of cores to use in processing')
    args = parser.parse_args()

    if args.core_count:
        coreCount = args.core_count
    else:
        coreCount = os.cpu_count()

    results = dispatcher(args.infile, 1)
    print_measurements(results)
