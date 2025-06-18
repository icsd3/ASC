import hashlib
import os

def compute_md5_hash(filepath):
    """Compute the MD5 hash of a file."""
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
    """Load virus signatures (MD5 hashes) from a file."""
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
    """Scan the file by comparing its MD5 hash against known signatures.

    Returns:
        tuple(md5_hash: str or None, infected: bool)
    """
    file_hash = compute_md5_hash(filepath)
    if file_hash is None:
        return None, False

    signatures = load_signature_database(signature_db_path)
    if not signatures:
        return file_hash, False

    infected = file_hash.lower() in signatures
    return file_hash, infected

def scan_folder(folder_path, signature_db_path, progress_callback=None):
    """Scan all files recursively in the folder and its subfolders.

    Args:
        folder_path (str): folder to scan
        signature_db_path (str): path to virus signatures file
        progress_callback (function): optional callback with signature (current, total)

    Returns:
        dict with filepath as key, and (md5_hash, infected) tuple as value.
    """
    results = {}
    signatures = load_signature_database(signature_db_path)
    if not signatures:
        print("Warning: No virus signatures loaded.")
        return results

    # Collect all files first to get total count
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
            results[filepath] = (None, False)  # Could not read file

        if progress_callback:
            progress_callback(index, total_files)

    return results
