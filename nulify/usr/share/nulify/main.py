import tkinter as tk
from tkinter import ttk
import subprocess
import webbrowser

# Main window setup
root = tk.Tk()
root.title("Nulify")
root.geometry("480x770")
root.configure(bg="#1a1a1a")  # Set the background of the main window to dark mode

# Style setup for dark mode
style = ttk.Style()
style.theme_use("clam")

# Apply the dark theme styles
style.configure("TFrame", background="#1a1a1a")
style.configure("TLabel", background="#1a1a1a", foreground="#f4f4f9", font=("Roboto", 10))
style.configure("TButton", background="#00aaff", foreground="#1a1a1a", font=("Roboto", 12), relief="flat")
style.map("TButton", background=[('active', '#f4f4f9')], foreground=[('active', '#1a1a1a')])

# List to store subprocesses
subprocesses = []

# Function to show the main page (current page)
def show_main_page():
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()
    # Recreate main page content
    label = ttk.Label(main_frame, text="NULIFY", font=("Roboto", 24), foreground="#00aaff", background="#1a1a1a")
    label.pack(pady=20)
    offline_button = ttk.Button(main_frame, text="Offline Mode", command=run_offline)
    offline_button.pack(pady=10, fill="x")
    online_button = ttk.Button(main_frame, text="Online Mode", command=run_online)
    online_button.pack(pady=10, fill="x")
    exit_button = ttk.Button(main_frame, text="Exit", command=close_app)
    exit_button.pack(pady=10, fill="x")
    # Show the main frame
    welcome_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)

# Function to run offline mode
def run_offline():
    input_frame = ttk.Frame(main_frame, padding="10")
    input_frame.pack(fill="x", pady=10)

    # Add this error label
    error_label = ttk.Label(input_frame, text="", background="#1a1a1a", foreground="red")
    error_label.pack(pady=5)

    def start_offline():
        # Get input values
        min_width = min_width_entry.get()
        max_width = max_width_entry.get()
        min_height = min_height_entry.get()
        max_height = max_height_entry.get()
        aruco_size = aruco_size_entry.get()
        
        # Check if any field is empty
        if not all([min_width, max_width, min_height, max_height, aruco_size]):
            # Show an error message if any field is empty
            error_label.config(text="Please fill in all fields.", foreground="red")
            return
        
        # Convert inputs to float and run the subprocess
        command = [
            "python3", "/home/armkh/Documents/code/Nulify/nulify/usr/share/nulify/offline.py",
            str(float(min_width)), str(float(max_width)),
            str(float(min_height)), str(float(max_height)),
            str(float(aruco_size))
        ]

        process = subprocess.Popen(command)
        subprocesses.append(process)
        input_frame.destroy()  # Remove the input frame after starting the offline mode

    # Input fields and labels
    ttk.Label(input_frame, text="Min Width (cm):").pack(pady=5)
    min_width_entry = ttk.Entry(input_frame)
    min_width_entry.pack(pady=5)

    ttk.Label(input_frame, text="Max Width (cm):").pack(pady=5)
    max_width_entry = ttk.Entry(input_frame)
    max_width_entry.pack(pady=5)

    ttk.Label(input_frame, text="Min Height (cm):").pack(pady=5)
    min_height_entry = ttk.Entry(input_frame)
    min_height_entry.pack(pady=5)

    ttk.Label(input_frame, text="Max Height (cm):").pack(pady=5)
    max_height_entry = ttk.Entry(input_frame)
    max_height_entry.pack(pady=5)

    ttk.Label(input_frame, text="ArUco Size (cm):").pack(pady=5)
    aruco_size_entry = ttk.Entry(input_frame)
    aruco_size_entry.pack(pady=5)

    start_button = ttk.Button(input_frame, text="Start Offline Mode", command=start_offline)
    start_button.pack(pady=10)




def run_online():
    # Clear the main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Start the server
    process = subprocess.Popen(["python3", "/home/armkh/Documents/code/Nulify/nulify/usr/share/nulify/server.py"])
    subprocesses.append(process)

    # Function to open the link in the terminal
    def open_link():
        subprocess.Popen(["x-www-browser", "http://127.0.0.1:5000/"], start_new_session=True)

    # Create labels and button in the main frame
    ttk.Label(main_frame, text="Online Mode", font=("Roboto", 24), foreground="#00aaff", background="#1a1a1a").pack(pady=20)
    
    ttk.Label(main_frame, text="Server is running at:", background="#1a1a1a", foreground="#f4f4f9", font=("Roboto", 12)).pack(pady=10)
    
    link_label = ttk.Label(main_frame, text="http://127.0.0.1:5000/", foreground="#00aaff", background="#1a1a1a", font=("Roboto", 12))
    link_label.pack(pady=10)
    
    open_button = ttk.Button(main_frame, text="Open in Browser", command=open_link)
    open_button.pack(pady=20)

    back_button = ttk.Button(main_frame, text="Back to Main Menu", command=show_main_page)
    back_button.pack(pady=10)

def close_app():
    for process in subprocesses:
        process.terminate()
    root.quit()

# Create welcome frame (Welcome Page)
welcome_frame = ttk.Frame(root, padding="20")
welcome_frame.pack(fill="both", expand=True)

# Welcome page content
welcome_label = ttk.Label(welcome_frame, text="Welcome to NULIFY", font=("Roboto", 24), foreground="#00aaff", background="#1a1a1a")
welcome_label.pack(pady=20)

project_description = ttk.Label(welcome_frame, text="This application helps measure object sizes using both online and offline modes.", background="#1a1a1a", foreground="#f4f4f9", font=("Roboto", 12), wraplength=400)
project_description.pack(pady=20)

project_description = ttk.Label(welcome_frame, text="Get started to begin measuring.", background="#1a1a1a", foreground="#f4f4f9", font=("Roboto", 12), wraplength=400)
project_description.pack(pady=5, anchor="center")

get_started_button = ttk.Button(welcome_frame, text="Get Started", command=show_main_page)
get_started_button.pack(pady=0)

# Create main frame (Main Page - Offline/Online mode selection)
main_frame = ttk.Frame(root, padding="20")

# Main page content
label = ttk.Label(main_frame, text="NULIFY", font=("Roboto", 24), foreground="#00aaff", background="#1a1a1a")
label.pack(pady=20)

offline_button = ttk.Button(main_frame, text="Offline Mode", command=run_offline)
offline_button.pack(pady=10, fill="x")

online_button = ttk.Button(main_frame, text="Online Mode", command=run_online)
online_button.pack(pady=10, fill="x")

exit_button = ttk.Button(main_frame, text="Exit", command=close_app)
exit_button.pack(pady=10, fill="x")

# Start the Tkinter main loop
root.mainloop()
