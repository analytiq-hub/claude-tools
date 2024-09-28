#!/usr/bin/python

import os
import argparse
import fnmatch

# Global variable to store command-line arguments
args = None

def parse_gitignore(directory):
    gitignore_patterns = []
    gitignore_path = os.path.join(directory, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as gitignore_file:
            for line in gitignore_file:
                line = line.strip()
                if line and not line.startswith('#'):
                    gitignore_patterns.append(line)
    return gitignore_patterns

def get_all_gitignore_patterns(top_dir):
    all_patterns = {}
    for root, _, _ in os.walk(top_dir):
        patterns = parse_gitignore(root)
        if patterns:
            all_patterns[root] = patterns
    return all_patterns

def should_ignore(file_path, top_dir, gitignore_patterns):
    file_path = os.path.normpath(file_path)
    
    for pattern_dir, patterns in gitignore_patterns.items():
        rel_path = os.path.relpath(file_path, pattern_dir)
        for pattern in patterns:
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return True
    
    return False

def is_binary(file_path):
    """Check if a file is binary."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file.read(1024)
        return False
    except UnicodeDecodeError:
        return True

def write_file_to_output(file_path, outfile, top_dir, include_binary):
    # Calculate relative path
    rel_path = os.path.relpath(file_path, top_dir)
    
    # Add header with the relative file path
    outfile.write(f"// {rel_path}\n")
    
    # Check if the file is binary
    if is_binary(file_path):
        if include_binary:
            outfile.write(f"// (binary file)\n\n")
        else:
            if args.verbose:
                print(f"Skipping binary file: {file_path}")
        return

    # Try opening each file with UTF-8 encoding; fallback to ignore errors
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
            outfile.write(infile.read() + "\n\n")
        if args.verbose:
            print(f"Processed file: {file_path}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

def to_single_file(inputs, output_file, top_dir, include_binary):
    gitignore_patterns = get_all_gitignore_patterns(top_dir)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for input_path in inputs:
            if os.path.isfile(input_path):
                # Process individual file
                if not should_ignore(input_path, top_dir, gitignore_patterns):
                    write_file_to_output(input_path, outfile, top_dir, include_binary)
            elif os.path.isdir(input_path):
                # Process directory recursively
                for root, _, files in os.walk(input_path):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        if not should_ignore(file_path, top_dir, gitignore_patterns):
                            write_file_to_output(file_path, outfile, top_dir, include_binary)
            else:
                if args.verbose:
                    print(f"Skipping {input_path}: Not a file or directory.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert a directory or list of files to a single file with file paths as headers.")
    parser.add_argument('-i', '--input', nargs='+', help='One or more files or Directories to be processed')
    parser.add_argument('-o', '--output_file', required=True, help='Output file to store the concatenated content')
    parser.add_argument('-t', '--top', required=True, help='Top directory of the sandbox for relative path calculation')
    parser.add_argument('-b', '--include-binary', action='store_true', help='Include binary files in the output')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    to_single_file(args.input, args.output_file, args.top, args.include_binary)

