import os
import ssdeep

def compute_fuzzy_hash(filepath):
    try:
        return ssdeep.hash_from_file(filepath)
    except Exception as e:
        print(f"Error hashing file '{filepath}': {e}")
        return None

def load_fuzzy_signatures(filename):
    signatures = {}
    if not os.path.isfile(filename):
        print(f"Error: Signature file '{filename}' not found.")
        return signatures
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    # Assume: <ssdeep_hash> <optional malware name or id>
                    parts = line.split(None, 1)
                    sig_hash = parts[0]
                    malware_id = parts[1] if len(parts) > 1 else ''
                    signatures[sig_hash] = malware_id
        return signatures
    except Exception as e:
        print(f"Error loading fuzzy signature database: {e}")
        return {}

def is_infected(fuzzy_hash, signature_db, threshold=70):
    for sig_hash, malware_id in signature_db.items():
        score = ssdeep.compare(fuzzy_hash, sig_hash)
        if score >= threshold:
            return True, score, malware_id
    return False, 0, None

def scan_file_fuzzy(filepath, signature_db, threshold=70):
    fuzzy_hash = compute_fuzzy_hash(filepath)
    if not fuzzy_hash:
        return None, False, 0, None
    infected, score, malware_id = is_infected(fuzzy_hash, signature_db, threshold)
    return fuzzy_hash, infected, score, malware_id

def scan_folder(folder_path, signature_db_path, progress_callback=None, threshold=70):
    results = {}
    signature_db = load_fuzzy_signatures(signature_db_path)
    if not signature_db:
        print("Warning: No fuzzy virus signatures loaded.")
        return results

    all_files = []
    for root, _, files in os.walk(folder_path):
        for filename in files:
            all_files.append(os.path.join(root, filename))
    total_files = len(all_files)

    for idx, filepath in enumerate(all_files, start=1):
        fuzzy_hash, infected, score, malware_id = scan_file_fuzzy(filepath, signature_db, threshold)
        results[filepath] = (fuzzy_hash, infected, score, malware_id)
        if progress_callback:
            progress_callback(idx, total_files)

    return results
