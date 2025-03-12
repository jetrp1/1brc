# Written by Ryan Peel
from multiprocessing import Pool
import os
import mmap

MMAP_PAGE_SIZE = os.sysconf("SC_PAGE_SIZE")

def print_measurements(measurements: dict):
    """prints the results dict in the correct format

    Args:
        measurements (dict): results dict, see dispatcher for format specification
    """
    results = '{'

    for station in measurements.keys():
        min, sum, max, count = measurements[station]
        results += f'{station.decode()}={min/10:.1f}/{sum/10/count:.1f}/{max/10:.1f}, '
    
    results += '}'

    print(results)

# Could this be done in parallel?
# wouls that really have any real improvement?
def combine_results(results: list) -> dict:
    """Combines multiple result dictionaries into one 

    Args:
        results (list): a list of result dictionaries

    Returns:
        dict: the combined dictionaries, see the dispatcher for format specification.
    """
    
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

def dispatcher(file_path: str, thread_count: int) -> dict:
    """This function is the process dispatcher for the multithreading functions. It will determin how to split up the job and then will dispatch thread_count processes to complete the job.

    Args:
        file_path (str): the file path to the measurements file
        thread_count (int): the number of CPU cores to use for parallel execution.

    Returns:
        dict: contians an entry for each station with the nessecary data for printing the results. format: station: [min, sum, max, count]
    """
    
    
    file_size = os.path.getsize(file_path)

    if thread_count == 1:
        final_results = calc_average_block(file_path, 0, file_size)
    else:
        chunk_size = file_size // thread_count
        with open(file_path, 'r+b') as f:
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

                    chunk_list.append([file_path, chunk_start, chunk_end])
                    chunk_start = chunk_end

                # Start each process
        with Pool(processes=thread_count) as pool:
            results = pool.starmap(calc_average_block, chunk_list)

            final_results = combine_results(results)
    
    return final_results

def align_offset(offset: int, page_size: int) -> int:
    """Aligns the offset to the system page size for better mmap functionality.

    Args:
        offset (int): the starting offset
        page_size (int): system page size

    Returns:
        int: the offset moves back to align with a multiple of the system page size
    """
    return (offset // page_size) * page_size


def calc_average_block(file_path: str, chunk_start: int, chunk_end: int) -> dict:
    """This is the worker process which will process a section of the file. It will start at the byte offset chunk_start and stop at the byte offset chunk_end

    Args:
        file_path (str): file path of the measurements file
        chunk_start (int): the start of the chunk this process will use
        chunk_end (int): the end point in the file for this process

    Returns:
        dict: contians an entry for each station with the nessecary data for printing the results. format: station: [min, sum, max, count]
    """
    
    # We get OS Errors if we are not aligned to the system page sizes
    offset = align_offset(chunk_start, MMAP_PAGE_SIZE)
    measurements = {}

    with open(file_path, 'rb') as f:
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


def process_line(line: bytes, measurements: dict):
    """Processes one line from the measurements file and updates the dictionary in place

    Args:
        line (bytes): a bytes object representing a string of characters
        measurements (dict): the dictionary for which we store the results. see the dispatcher for formatting
    """
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
    """converts the formatted bytes string from the measurements file and convert to an integer, preserving the precision by shifting the decimal right one position.

    Args:
        x (bytes): the bytes string containing the number to parse

    Returns:
        int: the integer representation of the value
    """
    # Parse sign
    if x[0] == 45:
        sign = -1
        idx = 1
    else:
        sign = 1
        idx = 0
        
    # -1 will always be the idx of the decimal
    # maybe this is not true from the dataset in the main repo but it is in mine.
    # type bytes cannot be added to the result, we have to do each byte one at a time

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

