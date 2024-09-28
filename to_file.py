#!/usr/bin/python

import os
import argparse

def to_single_file(inputs, output_file, top_dir):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for input_path in inputs:
            if os.path.isfile(input_path):
                # Process individual file
                write_file_to_output(input_path, outfile, top_dir)
            elif os.path.isdir(input_path):
                # Process directory recursively
                for root, _, files in os.walk(input_path):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        write_file_to_output(file_path, outfile, top_dir)
            else:
                print(f"Skipping {input_path}: Not a file or directory.")

def write_file_to_output(file_path, outfile, top_dir):
    # Calculate relative path
    rel_path = os.path.relpath(file_path, top_dir)
    # Add header with the relative file path
    outfile.write(f"// {rel_path}\n")
    # Try opening each file with UTF-8 encoding; fallback to ignore errors
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
            outfile.write(infile.read() + "\n\n")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert a directory or list of files to a single file with file paths as headers.")
    parser.add_argument('-i', '--input', nargs='+', help='One or more files or Directories to be processed')
    parser.add_argument('-o', '--output_file', required=True, help='Output file to store the concatenated content')
    parser.add_argument('-t', '--top', required=True, help='Top directory of the sandbox for relative path calculation')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    to_single_file(args.input, args.output_file, args.top)

