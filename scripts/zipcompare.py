import zipfile
import os
import hashlib

class ZipCompareError(Exception):
    """Base exception for zipcompare errors."""


class ZipFileNotFoundError(ZipCompareError):
    """Exception for missing ZIP file."""


class DirectoryNotFoundError(ZipCompareError):
    """Exception for missing directory."""


def get_zip_file_info(zip_path):
    """Get file information from a ZIP archive."""
    if not os.path.isfile(zip_path):
        raise ZipFileNotFoundError(f"ZIP file '{zip_path}' does not exist.")
    
    zip_info = {}
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for zip_entry in zipf.infolist():
            if not zip_entry.is_dir():
                zip_info[zip_entry.filename] = zip_entry.file_size
    return zip_info


def get_directory_file_info(dir_path):
    """Get file information from a directory."""
    if not os.path.isdir(dir_path):
        raise DirectoryNotFoundError(f"Directory '{dir_path}' does not exist")
    
    dir_info = {}
    for root, _, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), dir_path)
            file_size = os.path.getsize(os.path.join(root, file))
            # Normalize path separator for comparison
            dir_info[file_path.replace(os.sep, '/')] = file_size
    return dir_info


def compare_zip_and_directory(zip_path, dir_path):
    """Compare a ZIP archive and a directory for file names and sizes."""
    zip_info = get_zip_file_info(zip_path)
    dir_info = get_directory_file_info(dir_path)
    
    zip_files = set(zip_info.keys())
    dir_files = set(dir_info.keys())
    
    # Check for differences in file names
    only_in_zip = zip_files - dir_files
    only_in_dir = dir_files - zip_files
    
    # Check for differences in file sizes.
    # NB - MD5 check would be better.
    size_mismatch = {file: (zip_info[file], dir_info[file]) for file in (zip_files & dir_files) if zip_info[file] != dir_info[file]}
    
    return {
        'only_in_zip': only_in_zip,
        'only_in_dir': only_in_dir,
        'size_mismatch': size_mismatch
    }

def print_set(title, items):
    """Print each item in a set on a new line."""
    print(f"\n{title}:")
    if items:
        for item in items:
            print(f"  - {item}")
    else:
        print("  (None)")


def print_dict(title, items):
    """Print each key-value pair in a dictionary on a new line."""
    print(f"\n{title}:")
    if items:
        for key, value in items.items():
            print(f"  - {key}: {value}")
    else:
        print("  (None)")


if __name__ == '__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Compare a ZIP file with a directory without extracting.')
    parser.add_argument('zip_path', help='Path to the ZIP file')
    parser.add_argument('dir_path', help='Path to the directory')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.zip_path):
        sys.exit(f"Error: ZIP file '{args.zip_path}' does not exist.")
        
    
    if not os.path.isdir(args.dir_path):
        sys.exit(f"Error: Directory '{args.dir_path}' does not exist.")
    
    comparison_result = compare_zip_and_directory(args.zip_path, args.dir_path)
    
    print("\nComparison Results:")
    print_set("Files only in ZIP", comparison_result['only_in_zip'])
    print_set("Files only in Directory", comparison_result['only_in_dir'])
    print_dict("Files with size mismatch", comparison_result['size_mismatch'])
