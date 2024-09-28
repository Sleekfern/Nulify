import tkinter as tk
import subprocess
import os

def run_offline():
    # Run the offline real-time measurement code
    subprocess.Popen(["python3", "realtime_measurement.py"])

def run_online():
    # Run the online remote monitoring server
    subprocess.Popen(["python3", "server.py"])

def close_app():
    root.quit()

# Create the main window
root = tk.Tk()
root.title("Object Measurement App")

# Create a label for the title
label = tk.Label(root, text="Choose Mode", font=("Arial", 20))
label.pack(pady=20)

# Create buttons for Offline and Online modes
offline_button = tk.Button(root, text="Offline Mode", font=("Arial", 15), command=run_offline, width=20)
offline_button.pack(pady=10)

online_button = tk.Button(root, text="Online Mode", font=("Arial", 15), command=run_online, width=20)
online_button.pack(pady=10)

# Create an exit button
exit_button = tk.Button(root, text="Exit", font=("Arial", 15), command=close_app, width=20)
exit_button.pack(pady=20)

# Start the GUI loop
root.geometry("300x300")
root.mainloop()
