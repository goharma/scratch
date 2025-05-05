#!/bin/bash

# Check if the input file is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <input_file> [script_to_run]"
  echo "  <input_file>: Path to the file containing lines to process."
  echo "  [script_to_run]: Path to the script to execute for each line. Defaults to 'process_line.sh'."
  exit 1
fi

input_file="$1"
script_to_run="${2:-process_line.sh}"

# Check if the input file exists and is readable
if [ ! -r "$input_file" ]; then
  echo "Error: Input file '$input_file' not found or not readable."
  exit 1
fi

# Check if the script to run exists and is executable
if [ ! -x "$script_to_run" ]; then
  echo "Error: Script to run '$script_to_run' not found or not executable."
  exit 1
fi

line_count=0
batch_size=10
lines_buffer=()

# Function to process the current batch of lines
process_batch() {
  if [ "${#lines_buffer[@]}" -gt 0 ]; then
    echo "Processing batch of ${#lines_buffer[@]} lines..."
    for line in "${lines_buffer[@]}"; do
      "$script_to_run" "$line" &
    done
    wait # Wait for all background processes in the batch to complete
    lines_buffer=() # Clear the buffer
  fi
}

# Read the input file line by line
while IFS= read -r line; do
  lines_buffer+=("$line")
  line_count=$((line_count + 1))

  # Process the batch if it reaches the batch size
  if [ "$line_count" -eq "$batch_size" ]; then
    process_batch
    line_count=0
  fi
done < "$input_file"

# Process any remaining lines in the buffer
process_batch

echo "Finished processing all lines from '$input_file'."

exit 0
