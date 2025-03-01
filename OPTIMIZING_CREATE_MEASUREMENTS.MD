# Optimizing the create_measurements.py tool  
I thought optimizing the create measurements tool could also be a interesting project, it has a slightly different set of needs, and, well its another challenge and good for practice. All versions of this will be found in the commit history. :) Also I realize that there is an implementation of this exact tool also located in the official 1BRC challenge, remember this is a learning experience for me.

Here you will find my notes and process I took for this optimization.

## The Basic Build
First things first, I need a basic functioning tool. This will be a pretty inefficient tool. 

Some requirements:
 - Key distribution should be fairly even
 - Able to specify the number of Rows
 - User friendly
   - It should have a progress bar
 - Should only use native python libraries

Now the full code of this can be found in the `unoptimized/create_measurements_unoptimized.py' file. 

I also built a few scripts to make benchmarking easier. 
- benchmark_cm.sh -  this is basically an alias
- benchmark_cm_avg.sh - takes the average over n runs (3)

For starters this takes wayyy too long to run against the full 1 billion rows, so to start we will use 1 million rows for the benchmarks. Running our benchmark we get:

```sh
$ ./benchmark_cm_avg.sh 1_000_000
Starting Benchmark
Run 1...
Progress: ████████████████████████████████████████████████████████████████████████████████████████████████████ 100.0% 
Run 2...
Progress: ████████████████████████████████████████████████████████████████████████████████████████████████████ 100.0% 
Run 3...
Progress: ████████████████████████████████████████████████████████████████████████████████████████████████████ 100.0% 
Average Execution Times:
  Real: 38.500s
  User: 24.740s
  Sys:  13.640s
```




## Optimizations

Now this is quickly going to become I/O limited and to further benchmark but I think I have done a good enough job at writing a unoptimized script that we have some room to improve it. 

Some ideas I have for improvement
- less/no writing to stdout
- random.Random get initialized every instance
- writing to the file in batches
- string parsing in get_city_names
- avoiding for loops? (I heard they are slower and maybe should use while loops instead)


### Adding the option to remove the progress bar

Printing to the screen takes a very long time, so i added a '-q' flag which disables the progress bar. I feel that this somewhat rides the line of what is allowed since the progress bar is a requirement of the tool. So in the spirit of the challenge I also changed how the progress bar updates, but I after this next run i'll keep the progress bar disabled.

Build File becomes:
```py
def build_file(file, num_rows: int, num_keys: int, quiet):
    UPDATE_FREQ = 1000  # frequency of updating the progress bar

    # get a list of Keys
    keys = get_city_names()

    with open(file, 'w') as outFile:

        # generate the data
        for i in range(num_rows):
            city = random.choice(keys)
            temp = get_temp_string()
            outFile.write(f'{city},{temp}\n')
            if not quiet and i % UPDATE_FREQ == 0:  # Hold functionality and less frequently updating the progress bar
                progress_bar(i, num_rows-1, prefix='Progress:', length=100)
```

testing with the less writing cuts out run time in half!

```sh
$ ./benchmark_cm_avg.sh 1_000_000
Starting Benchmark
Run 1...
Progress: ███████████████████████████████████████████████████████████████████████████████████████████████████- 99.9% 
Run 2...
Progress: ███████████████████████████████████████████████████████████████████████████████████████████████████- 99.9% 
Run 3...
Progress: ███████████████████████████████████████████████████████████████████████████████████████████████████- 99.9% 
Average Execution Times:
  Real: 19.849s
  User: 11.035s
  Sys:  8.789s
```

and testing with the progress bars disabled shaves off another second!

```sh
$ ./benchmark_cm_avg.sh 1_000_000
Starting Benchmark
Run 1...
Run 2...
Run 3...
Average Execution Times:
  Real: 18.688s
  User: 10.134s
  Sys:  8.549s
```

### random.Random get initialized every instance

Global Lookups can expensive in terms of compute time, but initializing a new random object each time is more expensive. Lets move the initialization of random.Random to the global space

```py
r = random.Random()
def get_temp_string() -> str:
    temp = r.random() * 100
    return f'{temp:.3}'
```

this gets us a huge improvement

```
$ ./benchmark_cm_avg.sh 1_000_000
Starting Benchmark
Benchmark completed!
Average Execution Times:
  Real: 1.475s
  User: 1.433s
  Sys:  .041s
```

looks like its time to increase the number of rows we create, lets increase from 1 million to 100 million. Here is the current run time for 100 million rows for reference.

```
$ ./benchmark_cm_avg.sh 100_000_000
Starting Benchmark
Benchmark completed!
Average Execution Times:
  Real: 144.619s
  User: 142.043s
  Sys:  2.348s
```

now I suspect that we have hit our I/O limits since pretty much all our time was spent in User time


### Writing to the file in batches

So I/O is our limiting factor now. Hard Drives and SSDs work in sectors at the hardware level, older drives typically use a sector size of 512 bytes and modern HDDs and SSDs usually have a sector size of 4k (4096) bytes. so lets try and write in chunks. Now i think it will be rather expensive to track the length of the buffer after each time we add to it, so instead we will just write the buffer after a specific number of lines have been processed. 

```py
def build_file(file, num_rows: int, num_keys: int, quiet):
    UPDATE_FREQ = num_rows/1000
    LINES_PER_WRITE = ???       # const for number of lines to write per cycle

    # get a list of Keys
    keys = get_city_names()

    with open(file, 'w') as outFile:
        buffer = str()

        # generate the data
        for i in range(num_rows):
            city = random.choice(keys)
            temp = get_temp_string()
            buffer = buffer + f'{city},{temp}\n'   # could this cause some issues?

            if i % LINES_PER_WRITE == 0:    # write only every LINES_PER_WRITE lines
                outFile.write(buffer)
                buffer = str()
           
            if not quiet and i % UPDATE_FREQ == 0: 
                progress_bar(i, num_rows-1, prefix='Progress:', length=100)
            
        outFile.write(buffer)   # don't forget to write the last bit of lines
        buffer = str()
```

How to we decide how many lines to write? well I'm not great with AWK so I asked chatGPT to write me an AWK script to get me the average over our 100 million lines file we made earlier.

```sh
$ awk '{ total += length } END { print total / NR }' ./benchmarking_data/measurements_benchmark.csv
14.0817
```

So 14 bytes per line, well 4096 / 14 = 292.5 so lets go with 293. It's oddly specific but our code can handle it. 

```sh
$ ./benchmark_cm_avg.sh 100_000_000
Starting Benchmark
Benchmark completed!
Average Execution Times:
  Real: 156.018s
  User: 153.153s
  Sys:  2.638s

```

Well, that made it worse. I fear that any improvement we get here isn't going to be very much. Lets shoot for writing every 1 million lines, this is trading off RAM for less write operations and allowing the SSD in my system to operate more efficiently.

```
$ ./benchmark_cm_avg.sh 100_000_000
Starting Benchmark
Benchmark completed!
Average Execution Times:
  Real: 139.037s
  User: 136.511s
  Sys:  2.475s
```

Well thats a bit better, a whole 5 seconds faster.


### Using Buffers instead of writing in batches

Another options is to use the builtin buffer system for writing to the file. Maybe python's implementation of this concept is better than mine. Here is the updated build file function:

```py
def build_file(file, num_rows: int, num_keys: int, quiet):
    UPDATE_FREQ = num_rows/1000

    # get a list of Keys
    keys = get_city_names()

    with open(file, 'w', buffering=1024 * 1000) as outFile:  # 1024 * 1000 means we will use a buffer of 1MB

        # generate the data
        for i in range(num_rows):
            city = random.choice(keys)
            temp = get_temp_string()
            outFile.write(f'{city},{temp}\n')
           
            if not quiet and i % UPDATE_FREQ == 0: 
                progress_bar(i, num_rows-1, prefix='Progress:', length=100)
```

After trying several different buffer sizes i decided on using a 40MB buffer size as that seemed to give the best performance. If someone is running this on a system with very little RAM then this large of a buffer might be an issue. 

```
$ ./benchmark_cm_avg.sh 100_000_000
Starting Benchmark
Benchmark completed!
Average Execution Times:
  Real: 121.608s
  User: 120.437s
  Sys:  1.144s
```

## Conclusion