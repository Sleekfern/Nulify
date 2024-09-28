import tkinter as tk
import subprocess
import os

# Function to handle the Offline Mode input gathering
def run_offline():
    # Create a new window for input
    input_window = tk.Toplevel(root)
    input_window.title("Offline Mode - Input Required")
    
    def start_offline():
        min_width = float(min_width_entry.get())
        max_width = float(max_width_entry.get())
        min_height = float(min_height_entry.get())
        max_height = float(max_height_entry.get())
        aruco_size = float(aruco_size_entry.get())

        # Pass the inputs to the offline script by creating a command
        command = [
            "python3", "nulify_final_app/offline.py",
            str(min_width), str(max_width),
            str(min_height), str(max_height),
            str(aruco_size)
        ]

        # Run the realtime measurement script with subprocess
        subprocess.Popen(command)
        input_window.destroy()  # Close the input window after launching the script
    
    # Labels and Entries for the inputs
    tk.Label(input_window, text="Enter the minimum width for detection (cm):").pack(pady=5)
    min_width_entry = tk.Entry(input_window)
    min_width_entry.pack(pady=5)

    tk.Label(input_window, text="Enter the maximum width for detection (cm):").pack(pady=5)
    max_width_entry = tk.Entry(input_window)
    max_width_entry.pack(pady=5)

    tk.Label(input_window, text="Enter the minimum height for detection (cm):").pack(pady=5)
    min_height_entry = tk.Entry(input_window)
    min_height_entry.pack(pady=5)

    tk.Label(input_window, text="Enter the maximum height for detection (cm):").pack(pady=5)
    max_height_entry = tk.Entry(input_window)
    max_height_entry.pack(pady=5)

    tk.Label(input_window, text="Enter the ArUco marker size (cm):").pack(pady=5)
    aruco_size_entry = tk.Entry(input_window)
    aruco_size_entry.pack(pady=5)

    # Start button
    start_button = tk.Button(input_window, text="Start", command=start_offline)
    start_button.pack(pady=20)

# Function to handle the Online Mode
def run_online():
    subprocess.Popen(["python3", "nulify_final_app/server.py"])

# Function to close the app
def close_app():
    root.quit()

# Main window setup
root = tk.Tk()
root.title("Object Measurement App")

# Title label
label = tk.Label(root, text="Choose Mode", font=("Arial", 20))
label.pack(pady=20)

# Offline mode button
offline_button = tk.Button(root, text="Offline Mode", font=("Arial", 15), command=run_offline, width=20)
offline_button.pack(pady=10)

# Online mode button
online_button = tk.Button(root, text="Online Mode", font=("Arial", 15), command=run_online, width=20)
online_button.pack(pady=10)

# Exit button
exit_button = tk.Button(root, text="Exit", font=("Arial", 15), command=close_app, width=20)
exit_button.pack(pady=20)

# Start the GUI loop
root.geometry("300x300")
root.mainloop()
