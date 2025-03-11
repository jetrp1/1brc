# Written by Ryan Peel
from multiprocessing import Process, Queue
import os

def print_measurements(measurements: dict):
    results = '{'

    for station in measurements.keys():
        min, sum, max, count = measurements[station]
        results += f'{station.decode()}={min}/{sum/count:.1f}/{max}, '
    
    results += '}'

    print(results)

def dispatcher(file_name, thread_count):
    file_size = os.path.getsize(file_name)
    chunk_size = file_size // thread_count
    prevEnd = 0
    procs = [] 
    q = Queue()

    with open(file_name, 'rb') as f:

        def is_new_line(position):
            if position == 0:
                return True
            else:
                f.seek(position - 1)
                c = f.read(1)

                return (c == b"\n")

        chunk_start = 0
        while chunk_start < file_size:
            chunk_end = min(file_size, chunk_start + chunk_size)

            while not is_new_line(chunk_end):
                chunk_end -= 1

            # Start each process
            proc = Process(target=calc_average_block, args=[file_name, chunk_start, chunk_end, q])
            procs.append(proc)
            proc.start()

            chunk_start = chunk_end

    # Complete the processes
    for p in procs:
        p.join()

    result = {}
    # go through dicts in queue
    while not q.empty():
        curr_dict = q.get()

        for station in curr_dict:
            record = curr_dict[station]
            if station in result:
                result[station][0] = min(result[station][0], record[0])
                result[station][1] = result[station][1] + record[1]
                result[station][2] = max(result[station][2], record[2])
                result[station][3] = result[station][3] + record[3]
            else:
                result[station] = record
    
    return result


def calc_average_block(file_name, offset, chunk_end, q):
    measurements = dict()

    with open(file_name, 'rb') as f:
        f.seek(offset)

        for record in f:
            if f.tell() > chunk_end:
                break
        
        station, value = record.split(b',')
        value = float(value)

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

    q.put(measurements)


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

    results = dispatcher(args.infile, coreCount)
    print_measurements(results)