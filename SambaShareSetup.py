import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import os
import re

SMB_CONF = "/etc/samba/smb.conf"

# Must be run as root
if os.geteuid() != 0:
    messagebox.showerror("Permission Error", "This script must be run as root!")
    exit()

def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_path)

def setup_share():
    folder = folder_entry.get().strip()
    share_name = share_name_entry.get().strip()
    username = username_entry.get().strip()

    if not folder or not share_name or not username:
        messagebox.showerror("Input Error", "All fields are required")
        return

    # Add user to Samba (will prompt for password)
    try:
        subprocess.run(["sudo", "smbpasswd", "-a", username], check=True)
    except subprocess.CalledProcessError:
        messagebox.showwarning("Warning", f"User {username} might already exist or password setup canceled.")

    share_config = f"""
[{share_name}]
   path = {folder}
   browseable = yes
   read only = no
   guest ok = no
"""

    try:
        with open(SMB_CONF, "a") as f:
            f.write(share_config)
    except PermissionError:
        messagebox.showerror("Permission Error", "Cannot write to /etc/samba/smb.conf")
        return

    subprocess.run(["systemctl", "restart", "smbd"])
    messagebox.showinfo("Success", f"Share '{share_name}' setup successfully!")
    refresh_shares()

def parse_shares():
    """Read /etc/samba/smb.conf and find all shares."""
    shares = []
    if not os.path.exists(SMB_CONF):
        return shares

    with open(SMB_CONF, "r") as f:
        content = f.read()

    matches = re.findall(r"\[([^\]]+)\]\s*path\s*=\s*(.+)", content)
    for name, path in matches:
        shares.append((name.strip(), path.strip()))
    return shares

def refresh_shares():
    """Refresh the list of existing shares."""
    for item in share_listbox.get_children():
        share_listbox.delete(item)
    shares = parse_shares()
    for name, path in shares:
        share_listbox.insert("", "end", values=(name, path))

def remove_share():
    selected = share_listbox.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a share to remove.")
        return

    share_name = share_listbox.item(selected[0], "values")[0]

    with open(SMB_CONF, "r") as f:
        lines = f.readlines()

    new_lines = []
    inside_block = False
    for line in lines:
        if line.strip().startswith(f"[{share_name}]"):
            inside_block = True
            continue
        if inside_block and line.strip().startswith("[") and not line.strip().startswith(f"[{share_name}]"):
            inside_block = False
        if not inside_block:
            new_lines.append(line)

    with open(SMB_CONF, "w") as f:
        f.writelines(new_lines)

    subprocess.run(["systemctl", "restart", "smbd"])
    messagebox.showinfo("Removed", f"Share '{share_name}' removed successfully!")
    refresh_shares()

# GUI setup
root = tk.Tk()
root.title("Samba Share Manager")
root.geometry("600x400")

# Frame for new share setup
frame_top = tk.LabelFrame(root, text="Add New Share", padx=10, pady=10)
frame_top.pack(fill="x", padx=10, pady=10)

tk.Label(frame_top, text="Folder:").grid(row=0, column=0, sticky="e")
folder_entry = tk.Entry(frame_top, width=40)
folder_entry.grid(row=0, column=1)
tk.Button(frame_top, text="Browse", command=browse_folder).grid(row=0, column=2)

tk.Label(frame_top, text="Share Name:").grid(row=1, column=0, sticky="e")
share_name_entry = tk.Entry(frame_top, width=40)
share_name_entry.grid(row=1, column=1)

tk.Label(frame_top, text="Username:").grid(row=2, column=0, sticky="e")
username_entry = tk.Entry(frame_top, width=40)
username_entry.grid(row=2, column=1)

tk.Button(frame_top, text="Create Share", command=setup_share).grid(row=3, column=1, pady=10)

# Frame for existing shares
frame_bottom = tk.LabelFrame(root, text="Existing Shares", padx=10, pady=10)
frame_bottom.pack(fill="both", expand=True, padx=10, pady=10)

import tkinter.ttk as ttk
share_listbox = ttk.Treeview(frame_bottom, columns=("Share", "Path"), show="headings")
share_listbox.heading("Share", text="Share Name")
share_listbox.heading("Path", text="Folder Path")
share_listbox.pack(fill="both", expand=True)

tk.Button(frame_bottom, text="Remove Selected Share", command=remove_share).pack(pady=5)

refresh_shares()
root.mainloop()
