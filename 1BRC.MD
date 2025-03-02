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

I am using a create_measurements.py file that I built myself since I do not want to install a java environment on my system.

### Baseline

I have created myself a baseline to work from. Is really poor, and averages around 25 mins on my machine. I have heard of other people's attempts getting down to the sub 10 second range, that will be my goal for this.

### Diagnostic Tools

I have several different sizes of the measurements CSV that way I can test early changes faster. The Sizes are:
- 1 Million
- 10 Million
- 100 Million
- 1 Billion

### Optimization Ideas

Some ideas for optimizing this code:
- Parallel Processing
- string parsing
- pypy
- reading the file faster
- using a flamegraph to find problem issues

### PYPY

PyPy3 has shown to improve performance in many projects so ill run pretty much everything from now on using pypy. Below are the differences in the baseline time using pypy3 versus cPython3




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

1.4 times as fast!


### Parallel Processing

Parallel Processing I think will be the biggest improvement, so lets do that first. I'll create a dispatcher function and a measure block function. the dispatcher will load in the data and start off a job. the code will dynamically choose the number of cores to use unless otherwise specified







