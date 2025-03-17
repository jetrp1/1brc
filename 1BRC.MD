# 1BRC in Python

This is my attempt for the 1Billion Rows Challenge in Python

### Inspiration and Attribution

Some Ideas for this came from a few sources. They are listed below
- Doug Mercer [video](https://www.youtube.com/watch?v=utTaPW32gKY&t=125s)
- [Discussion](https://github.com/gunnarmorling/1brc/discussions/62) from the official repo 

Some things to note, while I could simply follow these and have a working and fast implementation that will not help me learn. So while i am taking ideas from these I am not following them. Although I expect that my implementation will be fairly similar by the time I am done.  

### My Rules

Pretty much the same as the java implementation. 
 - Keep it Pure python, only use standard libraries

### Measurement

I'll use hyperfine to benchmark my script. I'll do 3 Runs with one warm up run.

### Data Generation

I am using a create_measurements.py file that I built myself since I do not want to install a java environment on my system. you can find it in the repo and i even did a bit of a speed analysis on it.

### Goal

I have created myself a baseline to work from. It is really poor, and averages around 25 mins on my machine. I ran Doug Mercer's doug booty v4 version on my machine and it ran in around 2 mins so my goal is to get to a similar range. 

Some things to note, my machine is a lot slower then others in the competition. Additionally I do not have enough ram to start a ram disk like many other folks are using. These two factors are why the script runs to much slower on my machine than the time Doug gets in his video.

### Diagnostic Tools

Some tools I used:
- Multiple sizes of measurements files
- hyperfine
- time (gnu tool)
- viztracer (profiler)

### Optimization Ideas

Some ideas for optimizing this code:
- Parallel Processing
- string parsing
- pypy
- reading the file faster
- using a flamegraph to find problem issues

### PYPY

PyPy3 has shown to improve performance in many projects so ill run pretty much everything from now on using pypy. Below are the differences in the baseline time using pypy3 versus cPython3

| Command | Mean [s] | Min [s] | Max [s] | Relative |
|:---|---:|---:|---:|---:|
| `pypy3 ./calculate_average_baseline.py ./measurements/1B_Measurements.csv` | 979.168 ± 3.948 | 976.766 | 983.724 | 1.00 |
| `python3 ./calculate_average_baseline.py ./measurements/1B_Measurements.csv` | 1733.957 ± 11.034 | 1721.578 | 1742.757 | 1.77 ± 0.01 |


### File Reading

So first thing I thought of was weather or not the various read modes had any affect on the run times. So I made 3 files which only read the file line by line and do not do anything else, one per read mode. 

| Command | Mean [s] | Min [s] | Max [s] | Relative |
|:---|---:|---:|---:|---:|
| `pypy3 ./ca_r.py ./measurements/100M_Measurements.csv` | 16.624 ± 0.565 | 15.996 | 17.091 | 1.88 ± 0.06 |
| `pypy3 ./ca_rb.py ./measurements/100M_Measurements.csv` | 8.841 ± 0.024 | 8.817 | 8.864 | 1.00 |
| `pypy3 ./ca_r+b.py ./measurements/100M_Measurements.csv` | 15.350 ± 0.422 | 14.982 | 15.810 | 1.74 ± 0.05 |

Thats a rather stark difference, but I question weather the extra work needed to parse binary data and do the various encoding negates this performance improvement. I'll modify the main script with the necessary changes.

| Command | Mean [s] | Min [s] | Max [s] | Relative |
|:---|---:|---:|---:|---:|
| `pypy3 ./calculate_average_r.py ./measurements/100M_Measurements.csv` | 100.081 ± 0.838 | 99.287 | 100.958 | 1.46 ± 0.01 |
| `pypy3 ./calculate_average_rb.py ./measurements/100M_Measurements.csv` | 68.539 ± 0.283 | 68.349 | 68.864 | 1.00 |

and against the 1B rows:

| Command | Mean [s] | Min [s] | Max [s] | Relative |
|:---|---:|---:|---:|---:|
| `pypy3 ./calculate_average_rb.py ./measurements/1B_Measurements.csv` | 666.263 ± 5.518 | 660.911 | 671.934 | 1.00 |


### Parallel Processing

Parallel Processing I think will be the biggest improvement. I'll create a dispatcher function and a measure block function. the dispatcher will load in the data and start off a job. the code will dynamically choose the number of cores to use unless otherwise specified.

| Command | Mean [s] | Min [s] | Max [s] | Relative |
|:---|---:|---:|---:|---:|
| `pypy3 ./calculate_average_mt.py ./measurements/1B_Measurements.csv` | 246.554 ± 0.181 | 246.352 | 246.700 | 1.00 |

### Switching to a memory map for reading in files

Ive seen a lot of people use mmap for reading in the file and I want to try that. My primary concern is that i do not have lots or ram on my system. Only 16gb and this is going to map this file (14gb) to my system memory. I want to avoid swapping also. So first I'll implement the mmap and run that to see if there are any improvements or if my system crashes due to and out of memory issue.

So my system did not crash, and we have a improved time also.

| Command | Mean [s] | Min [s] | Max [s] | Relative |
|:---|---:|---:|---:|---:|
| `pypy3 ./calculate_average_mmap.py ./measurements/1B_Measurements.csv` | 189.611 ± 0.293 | 189.359 | 189.932 | 1.00 |

So there is probably more to do here, but im not sure what that is, so lets move onto something else.

### String Parsing and using Integers instead of floats

So I know that string parsing is expensive, so since our data is so uniform instead of using the split function lets just find the comma and use list indexing instead. Now that alone isn't going to produce too much of a change, but now since we know that the integers will always have one digit after the decimal place we can treat these values as integers which should be much faster.

the code is gross and not very readable, but it is fast:

| Command | Mean [s] | Min [s] | Max [s] | Relative |
|:---|---:|---:|---:|---:|
| `pypy3 ./calculate_average_int.py ./measurements/1B_Measurements.csv` | 144.804 ± 0.524 | 144.327 | 145.365 | 1.00 |

### Final Results

SO with all our improvements we have taken the script from running 1733 seconds down to 144 seconds. Ill say that is quite the improvement and within the goal set also. Not too bad. 
