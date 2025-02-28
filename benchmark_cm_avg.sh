#!/bin/env bash
echo 'Starting Benchmark'

outfile='benchmarking_data/measurements_benchmark.csv'
num_runs=3
total_real=0
total_user=0
total_sys=0

for i in $(seq 1 $num_runs); do
    echo -ne "Run $i/$num_runs...\r"  # Overwrites the line instead of printing new ones

    # Run the script silently, capturing only execution times
    { time ./create_measurements.py "$1" "$outfile" > /dev/null; } 2> time_output.txt

    # Extract execution times
    real_time=$(grep real time_output.txt | awk '{print $2}')
    user_time=$(grep user time_output.txt | awk '{print $2}')
    sys_time=$(grep sys time_output.txt | awk '{print $2}')

    # Function to convert time format (if in min:sec) to pure seconds
    convert_time() {
        local time_val=$1
        if [[ $time_val == *m* ]]; then
            min=$(echo "$time_val" | cut -d'm' -f1)
            sec=$(echo "$time_val" | cut -d'm' -f2 | tr -d 's')
            echo "$min * 60 + $sec" | bc
        else
            echo "$time_val" | tr -d 's'
        fi
    }

    real_time=$(convert_time "$real_time")
    user_time=$(convert_time "$user_time")
    sys_time=$(convert_time "$sys_time")

    # Accumulate times
    total_real=$(echo "$total_real + $real_time" | bc)
    total_user=$(echo "$total_user + $user_time" | bc)
    total_sys=$(echo "$total_sys + $sys_time" | bc)

done

# Clear the progress line before printing results
echo -ne "\r\033[K"

# Calculate averages
average_real=$(echo "scale=3; $total_real / $num_runs" | bc)
average_user=$(echo "scale=3; $total_user / $num_runs" | bc)
average_sys=$(echo "scale=3; $total_sys / $num_runs" | bc)

# Display results
echo "Benchmark completed!"
echo "Average Execution Times:"
echo "  Real: ${average_real}s"
echo "  User: ${average_user}s"
echo "  Sys:  ${average_sys}s"

# Cleanup
rm time_output.txt
