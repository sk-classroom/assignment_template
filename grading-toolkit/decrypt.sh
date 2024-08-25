#!/bin/bash

# Check if correct number of arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_file> <output_file> <password>"
    exit 1
fi

# Assign arguments to variables for clarity
input_file="$1"
output_file="$2"
password="$3"

# Check if input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: Input file '$input_file' does not exist."
    exit 1
fi

# Perform decryption
openssl enc -d -aes256 -in $input_file -out $output_file -pass pass:$password
