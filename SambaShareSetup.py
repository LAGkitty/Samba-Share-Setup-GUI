import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

# Check if running as root
if os.geteuid() != 0:
    messagebox.showerror("Permission Error", "This script must be run as root!")
    exit()

def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_path)

def setup_share():
    folder = folder_entry.get()
    share_name = share_name_entry.get()
    username = username_entry.get()

    if not folder or not share_name or not username:
        messagebox.showerror("Input Error", "All fields are required")
        return

    # Add user if not exists
    try:
        subprocess.run(["sudo", "smbpasswd", "-a", username], check=True)
    except subprocess.CalledProcessError:
        messagebox.showwarning("Warning", f"User {username} might already exist or password setup canceled.")

    # Write share to smb.conf
    share_config = f"""
[{share_name}]
   path = {folder}
   browseable = yes
   read only = no
   guest ok = no
"""
    try:
        with open("/etc/samba/smb.conf", "a") as f:
            f.write(share_config)
    except PermissionError:
        messagebox.showerror("Permission Error", "Cannot write to /etc/samba/smb.conf")
        return

    # Restart Samba
    subprocess.run(["systemctl", "restart", "smbd"])
    messagebox.showinfo("Success", f"Share {share_name} setup successfully!")

# GUI
root = tk.Tk()
root.title("Samba Share Setup GUI")

tk.Label(root, text="Select Folder:").grid(row=0, column=0, sticky="e")
folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=0, column=1)
tk.Button(root, text="Browse", command=browse_folder).grid(row=0, column=2)

tk.Label(root, text="Share Name:").grid(row=1, column=0, sticky="e")
share_name_entry = tk.Entry(root)
share_name_entry.grid(row=1, column=1)

tk.Label(root, text="Username:").grid(row=2, column=0, sticky="e")
username_entry = tk.Entry(root)
username_entry.grid(row=2, column=1)

tk.Button(root, text="Setup Share", command=setup_share).grid(row=3, column=1, pady=10)

root.mainloop()
