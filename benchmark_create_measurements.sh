#!/bin/env bash
echo 'Starting Benchmark'
outfile='measurements_benchmark.csv'
time ./create_measurements.py $1 $outfile
rm $outfile