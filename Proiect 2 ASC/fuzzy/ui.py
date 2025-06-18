import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import main  # your updated main.py with fuzzy hashing

def get_downloads_folder():
    home = os.path.expanduser("~")
    dl = os.path.join(home, "Downloads")
    return dl if os.path.isdir(dl) else home

def get_default_signature_path():
    win_path = r"F:\ASC\Proiect 2 ASC\fuzzy_virus_signatures.txt"
    if os.name == 'nt' and os.path.isfile(win_path):
        return win_path
    return ""

def browse_folder():
    path = filedialog.askdirectory(
        title="Select folder to scan",
        initialdir=get_downloads_folder()
    )
    if path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, path)

def browse_signature_file():
    init = get_default_signature_path() or os.path.expanduser("~")
    path = filedialog.askopenfilename(
        title="Select fuzzy virus signature file",
        initialdir=os.path.dirname(init) if init else init
    )
    if path:
        signature_entry.delete(0, tk.END)
        signature_entry.insert(0, path)

def update_progress(current, total):
    progress_bar['maximum'] = total
    progress_bar['value'] = current
    progress_label.config(text=f"Scanning file {current} of {total}")
    root.update_idletasks()

def scan_thread():
    folder = folder_entry.get()
    sig    = signature_entry.get()
    if not folder or not sig:
        messagebox.showwarning("Missing input", "Please select both folder and signature file.")
        start_btn.config(state='normal')
        return
    if not os.path.isdir(folder):
        messagebox.showerror("Error", "Invalid folder path.")
        start_btn.config(state='normal')
        return
    if not os.path.isfile(sig):
        messagebox.showerror("Error", "Invalid signature file path.")
        start_btn.config(state='normal')
        return

    for item in tree.get_children():
        tree.delete(item)

    progress_bar['value'] = 0
    progress_label.config(text="Starting scan...")
    delete_btn.config(state='disabled')

    try:
        results = main.scan_folder(folder, sig, progress_callback=update_progress)
    except Exception as e:
        messagebox.showerror("Error", f"Scanning failed:\n{e}")
        start_btn.config(state='normal')
        return

    infected = {f:info for f, info in results.items() if info[1]}  # infected files only

    def finish():
        progress_label.config(text="Scan complete")
        progress_bar['value'] = 0
        if infected:
            for fp, (fuzzy_hash, infected, score, malware_id) in infected.items():
                display_name = malware_id if malware_id else "(Unknown Malware)"
                tree.insert("", "end", values=(fp, fuzzy_hash, score, display_name))
            delete_btn.config(state='normal')
            messagebox.showinfo("Done", f"Infected files found: {len(infected)}")
        else:
            messagebox.showinfo("Done", "✅ No infected files found.")
        start_btn.config(state='normal')

    root.after(0, finish)

def start_scan():
    start_btn.config(state='disabled')
    threading.Thread(target=scan_thread, daemon=True).start()

def delete_selected_file():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("No selection", "Select files to delete.")
        return
    if not messagebox.askyesno("Confirm", "Delete selected file(s)?"):
        return
    errs = []
    for item in sel:
        fp = tree.item(item, "values")[0]
        try:
            os.remove(fp)
            tree.delete(item)
        except Exception as e:
            errs.append(f"{fp}: {e}")
    if errs:
        messagebox.showerror("Errors", "\n".join(errs))
    else:
        messagebox.showinfo("Deleted", "Selected file(s) deleted.")

# --- GUI setup ---
root = tk.Tk()
root.title("Fuzzy Virus Scanner - Folder Scan")
root.geometry("1000x700")

tk.Label(root, text="Folder to scan:").pack(anchor="w", padx=10, pady=(10,0))
folder_entry = tk.Entry(root, width=95)
folder_entry.pack(padx=10, pady=2)

tk.Label(root, text="Fuzzy signature file (ssdeep hashes):").pack(anchor="w", padx=10, pady=(10,0))
signature_entry = tk.Entry(root, width=95)
signature_entry.pack(padx=10, pady=2)

tk.Button(root, text="Browse Folder...",    command=browse_folder).pack(padx=10, pady=(0,5))
tk.Button(root, text="Browse Signature...", command=browse_signature_file).pack(padx=10, pady=(0,15))

start_btn = tk.Button(root, text="Scan Folder", command=start_scan, bg="green", fg="white", height=2)
start_btn.pack(pady=10)

cols = ("File Path", "Fuzzy Hash", "Similarity", "Malware ID")
tree = ttk.Treeview(root, columns=cols, show="headings", selectmode="extended")
for c in cols:
    tree.heading(c, text=c)
    width = 400 if c=="File Path" else 150
    tree.column(c, anchor="w", width=width)
tree.pack(fill="both", expand=True, padx=10, pady=10)

delete_btn = tk.Button(root, text="Delete Selected File(s)", command=delete_selected_file,
                       bg="red", fg="white", state='disabled')
delete_btn.pack(pady=(0,15))

progress_bar = ttk.Progressbar(root, mode='determinate')
progress_bar.pack(fill='x', padx=10, pady=(0,5))

progress_label = tk.Label(root, text="")
progress_label.pack(padx=10, pady=(0,10))

# set defaults
folder_entry.insert(0, get_downloads_folder())
default_sig = get_default_signature_path()
if default_sig:
    signature_entry.insert(0, default_sig)

root.mainloop()
