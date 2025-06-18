import hashlib
import os

def compute_md5_hash(filepath):
    md5_hash = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)
        return md5_hash.hexdigest()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        return None

def load_signature_database(filename):
    if not os.path.isfile(filename):
        print(f"Error: Signature file '{filename}' not found.")
        return set()
    try:
        with open(filename, 'r') as f:
            return {line.strip().lower() for line in f if line.strip()}
    except Exception as e:
        print(f"Error loading signature database: {e}")
        return set()

def scan_file(filepath, signature_db_path):
    file_hash = compute_md5_hash(filepath)
    if file_hash is None:
        return None, False

    signatures = load_signature_database(signature_db_path)
    if not signatures:
        return file_hash, False

    infected = file_hash.lower() in signatures
    return file_hash, infected

def scan_folder(folder_path, signature_db_path, progress_callback=None):
    results = {}
    signatures = load_signature_database(signature_db_path)
    if not signatures:
        print("Warning: No virus signatures loaded.")
        return results

    all_files = []
    for root, _, files in os.walk(folder_path):
        for filename in files:
            all_files.append(os.path.join(root, filename))

    total_files = len(all_files)

    for index, filepath in enumerate(all_files, start=1):
        md5_hash = compute_md5_hash(filepath)
        if md5_hash:
            infected = md5_hash.lower() in signatures
            results[filepath] = (md5_hash, infected)
        else:
            results[filepath] = (None, False)

        if progress_callback:
            progress_callback(index, total_files)

    return results
