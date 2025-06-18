import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import main  # your main.py file

def get_downloads_folder():
    home = os.path.expanduser("~")
    downloads = os.path.join(home, "Downloads")
    return downloads if os.path.isdir(downloads) else home

def browse_folder():
    initial_dir = get_downloads_folder()
    foldername = filedialog.askdirectory(title="Select folder to scan", initialdir=initial_dir)
    if foldername:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, foldername)

def browse_signature_file():
    # Default Windows path for signatures, empty otherwise
    default_sig_path = r"F:\ASC\Proiect 2 ASC\md5_virus_signatures.txt"
    initial_dir = os.path.dirname(default_sig_path) if os.path.isfile(default_sig_path) else os.path.expanduser("~")
    filename = filedialog.askopenfilename(title="Select virus signature file", initialdir=initial_dir)
    if filename:
        signature_entry.delete(0, tk.END)
        signature_entry.insert(0, filename)

def update_progress(current, total):
    progress_bar['maximum'] = total
    progress_bar['value'] = current
    progress_label.config(text=f"Scanning file {current} of {total}")
    root.update_idletasks()

def scan_thread():
    folder_path = folder_entry.get()
    sig_path = signature_entry.get()

    if not folder_path or not sig_path:
        messagebox.showwarning("Missing input", "Please select both folder and signature file.")
        start_btn.config(state='normal')
        return

    if not os.path.isdir(folder_path):
        messagebox.showerror("Error", "Invalid folder path.")
        start_btn.config(state='normal')
        return

    if not os.path.isfile(sig_path):
        messagebox.showerror("Error", "Invalid signature file path.")
        start_btn.config(state='normal')
        return

    # Clear previous results
    for item in infected_tree.get_children():
        infected_tree.delete(item)

    # Reset progress UI
    progress_bar['value'] = 0
    progress_label.config(text="Starting scan...")
    delete_btn.config(state='disabled')

    try:
        # Call scan_folder with the progress callback
        results = main.scan_folder(folder_path, sig_path, progress_callback=update_progress)
    except Exception as e:
        messagebox.showerror("Error", f"Scanning failed:\n{e}")
        start_btn.config(state='normal')
        return

    infected_files = {f: md5 for f, (md5, infected) in results.items() if infected}

    def finish_scan():
        progress_label.config(text="Scan complete")
        progress_bar['value'] = 0
        if infected_files:
            for filepath, md5_hash in infected_files.items():
                infected_tree.insert("", "end", values=(filepath, md5_hash))
            delete_btn.config(state='normal')
            messagebox.showinfo("Scan complete", f"Infected files found: {len(infected_files)}")
        else:
            messagebox.showinfo("Scan complete", "✅ No infected files found in the scanned folder.")
            delete_btn.config(state='disabled')
        start_btn.config(state='normal')

    root.after(0, finish_scan)

def start_scan():
    start_btn.config(state='disabled')
    threading.Thread(target=scan_thread, daemon=True).start()

def delete_selected_file():
    selected = infected_tree.selection()
    if not selected:
        messagebox.showwarning("No selection", "Please select a file to delete.")
        return

    confirm = messagebox.askyesno("Confirm delete", "Are you sure you want to delete the selected file(s)?")
    if not confirm:
        return

    errors = []
    for item in selected:
        filepath = infected_tree.item(item, "values")[0]
        try:
            os.remove(filepath)
            infected_tree.delete(item)
        except Exception as e:
            errors.append(f"{filepath}: {e}")

    if errors:
        messagebox.showerror("Error deleting files", "\n".join(errors))
    else:
        messagebox.showinfo("Success", "Selected files deleted successfully.")

root = tk.Tk()
root.title("MD5 Virus Scanner - Folder Scan")
root.geometry("900x650")
root.resizable(True, True)

tk.Label(root, text="Folder to scan:").pack(anchor="w", padx=10, pady=(10, 0))
folder_entry = tk.Entry(root, width=90)
folder_entry.pack(padx=10, pady=2)

tk.Label(root, text="Signature file (MD5):").pack(anchor="w", padx=10, pady=(10, 0))
signature_entry = tk.Entry(root, width=90)
signature_entry.pack(padx=10, pady=2)

tk.Button(root, text="Browse Folder...", command=browse_folder).pack(padx=10, pady=(0, 10))
tk.Button(root, text="Browse Signature File...", command=browse_signature_file).pack(padx=10, pady=(0, 15))

start_btn = tk.Button(root, text="Scan Folder", command=start_scan, bg="green", fg="white", height=2)
start_btn.pack(pady=10)

columns = ("File Path", "MD5 Hash")
infected_tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="extended")
for col in columns:
    infected_tree.heading(col, text=col)
    infected_tree.column(col, anchor="w", width=400 if col == "File Path" else 300)
infected_tree.pack(fill="both", expand=True, padx=10, pady=10)

delete_btn = tk.Button(root, text="Delete Selected File(s)", command=delete_selected_file, bg="red", fg="white")
delete_btn.pack(pady=10)

progress_bar = ttk.Progressbar(root, mode='determinate')
progress_bar.pack(fill='x', padx=10, pady=(0, 5))

progress_label = tk.Label(root, text="")
progress_label.pack(padx=10, pady=(0, 10))

# Set default paths
folder_entry.insert(0, get_downloads_folder())
default_sig_path = r"F:\ASC\Proiect 2 ASC\md5_virus_signatures.txt"
if os.name == 'nt' and os.path.isfile(default_sig_path):
    signature_entry.insert(0, default_sig_path)

root.mainloop()
