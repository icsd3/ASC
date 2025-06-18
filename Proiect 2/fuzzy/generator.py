import os
import ssdeep

malware_dir = os.path.expanduser("~/malware-samples")
output_db_path = "fuzzy_signatures.txt"

with open(output_db_path, "w") as out:
    for filename in os.listdir(malware_dir):
        filepath = os.path.join(malware_dir, filename)
        if os.path.isfile(filepath):
            try:
                fuzzy_hash = ssdeep.hash_from_file(filepath)
                out.write(f"{fuzzy_hash} {filename}\n")
                print(f"Hashed: {filename}")
            except Exception as e:
                print(f"Failed: {filename} ({e})")
