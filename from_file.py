#!/usr/bin/python

import os

def single_file_to_directory(input_file, base_directory):
    with open(input_file, 'r') as infile:
        current_file = None
        file_content = []

        for line in infile:
            if line.startswith("// "):  # This is a path header
                # If there's already a file being processed, write its content
                if current_file:
                    write_file_content(current_file, file_content)
                
                # Set up the new file path
                file_path = line.strip()[3:]
                current_file = os.path.join(base_directory, file_path)
                file_content = []  # Reset content for new file
            else:
                file_content.append(line)

        # Write the last file content
        if current_file:
            write_file_content(current_file, file_content)

def write_file_content(file_path, file_content):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as outfile:
        outfile.writelines(file_content)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python from_file.py <input_file> <base_directory>")
        sys.exit(1)
    single_file_to_directory(sys.argv[1], sys.argv[2])