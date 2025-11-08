# Samba Share Setup GUI

A simple Python GUI tool to easily set up Samba (SMB) file sharing on Linux. Select a folder, create a share name, and add a Samba user—all from a graphical interface.

## Features

* Select any folder on your system to share.
* Set a custom share name.
* Add or configure a Samba user.
* Automatically appends share configuration to `/etc/samba/smb.conf`.
* Restarts Samba service automatically.

## Requirements

* Linux system with Samba installed:

```bash
sudo apt update
sudo apt install samba smbclient
```

* Python 3 and Tkinter module:

```bash
sudo apt install python3 python3-tk
```

* Root privileges (required to modify Samba configuration).

## Usage

1. Clone or download the script to your machine.
2. Run the script with root privileges:

```bash
sudo python3 FTP.py
```

3. In the GUI:

   * Click **Browse** to select the folder you want to share.
   * Enter a **Share Name**.
   * Enter a **Username** for Samba access.
   * Click **Setup Share** to create the share.
4. You will be prompted to set a Samba password for the user.
5. The share is now active and can be accessed from other devices on your network.

## Notes

* Make sure Samba is installed and running (`sudo systemctl status smbd`).
* Only run this script as root, otherwise it cannot modify `/etc/samba/smb.conf`.
* To remove a share, manually edit `/etc/samba/smb.conf` and restart Samba:

```bash
sudo systemctl restart smbd
```

---
