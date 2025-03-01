#!/bin/env bash
echo 'Starting Benchmark'
outfile='benchmarking_data/measurements_benchmark.csv'
time ./create_measurements.py $1 -q $outfile