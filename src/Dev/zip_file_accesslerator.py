import zipfile
import os

def combine_files_to_zip(small_files_directory, output_zipfile):
    with zipfile.ZipFile(output_zipfile, 'w') as zipf:
        for root, _, files in os.walk(small_files_directory):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=file)

def extract_file_from_zip(zipfile_path, file_name, output_directory):
    with zipfile.ZipFile(zipfile_path, 'r') as zipf:
        zipf.extract(file_name, path=output_directory)

# Example usage:
small_files_directory = 'path/to/small/files'
output_zipfile = 'combined_files.zip'
combine_files_to_zip(small_files_directory, output_zipfile)

# Extracting a specific file from the ZIP file
zipfile_path = 'combined_files.zip'
file_name = 'example.txt'
output_directory = 'path/to/output/directory'
extract_file_from_zip(zipfile_path, file_name, output_directory)
