import os
import ssdeep

def compute_fuzzy_hash(filepath):
    try:
        return ssdeep.hash_from_file(filepath)
    except Exception as e:
        print(f"Error hashing '{filepath}': {e}")
        return None

def scan_zip_files(folder_path, output_file='fuzzy_signatures.txt'):
    results = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.zip'):
                zip_path = os.path.join(root, file)
                fuzzy_hash = compute_fuzzy_hash(zip_path)
                if fuzzy_hash:
                    relative_path = os.path.relpath(zip_path, folder_path)
                    results.append(f"{fuzzy_hash} {relative_path}")
                    print(f"✔️ Hashed: {relative_path}")

    if results:
        with open(output_file, 'w') as f:
            for entry in results:
                f.write(entry + '\n')
        print(f"\n✅ Fuzzy signature database saved to '{output_file}'")
    else:
        print("⚠️ No zip files found or none could be hashed.")

if __name__ == "__main__":
    base_folder = "malware-samples"
    scan_zip_files(base_folder)
