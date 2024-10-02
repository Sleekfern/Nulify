import tkinter as tk
from tkinter import ttk
import subprocess
import webbrowser

# Main window setup
root = tk.Tk()
root.title("Nulify")
root.configure(bg="#1a1a1a")

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set window size to maximum
root.geometry(f"{screen_width}x{screen_height}")

# Maximize the window using wm_attributes
root.wm_attributes('-zoomed', True)

# Style setup for dark mode
style = ttk.Style()
style.theme_use("clam")

# Apply the dark theme styles
style.configure("TFrame", background="#1a1a1a")
style.configure("TLabel", background="#1a1a1a", foreground="#f4f4f9", font=("Roboto", 14))
style.configure("TButton", background="#00aaff", foreground="#1a1a1a", font=("Roboto", 16), relief="flat")
style.map("TButton", background=[('active', '#f4f4f9')], foreground=[('active', '#1a1a1a')])

# Variable to store the current running process
current_process = None

# Function to toggle fullscreen
def toggle_fullscreen(event=None):
    is_fullscreen = root.attributes("-fullscreen")
    root.attributes("-fullscreen", not is_fullscreen)
    if is_fullscreen:
        root.wm_attributes('-zoomed', True)

# Bind F11 key to toggle fullscreen
root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))

# Function to show the main page
def show_main_page():
    global current_process
    
    # Stop the current process if it exists
    if current_process:
        current_process.terminate()
        current_process = None

    for widget in main_frame.winfo_children():
        widget.destroy()
    
    label = ttk.Label(main_frame, text="NULIFY", font=("Roboto", 48), foreground="#00aaff", background="#1a1a1a")
    label.pack(pady=40)
    
    button_frame = ttk.Frame(main_frame, style="TFrame")
    button_frame.pack(expand=True)
    
    offline_button = ttk.Button(button_frame, text="Offline Mode", command=run_offline, width=30)
    offline_button.pack(pady=20)
    
    online_button = ttk.Button(button_frame, text="Online Mode", command=run_online, width=30)
    online_button.pack(pady=20)
    
    exit_button = ttk.Button(button_frame, text="Exit", command=close_app, width=30)
    exit_button.pack(pady=20)
    
    fullscreen_button = ttk.Button(main_frame, text="Toggle Fullscreen", command=toggle_fullscreen, width=20)
    fullscreen_button.pack(side="bottom", pady=20)
    
    welcome_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)

# Function to run offline mode
def run_offline():
    global current_process
    
    for widget in main_frame.winfo_children():
        widget.destroy()
    
    input_frame = ttk.Frame(main_frame, padding="20", style="TFrame")
    input_frame.pack(expand=True)

    error_label = ttk.Label(input_frame, text="", background="#1a1a1a", foreground="red", font=("Roboto", 12))
    error_label.grid(row=0, column=0, columnspan=2, pady=10)

    def start_offline():
        global current_process
        
        min_width = min_width_entry.get()
        max_width = max_width_entry.get()
        min_height = min_height_entry.get()
        max_height = max_height_entry.get()
        aruco_size = aruco_size_entry.get()
        
        if not all([min_width, max_width, min_height, max_height, aruco_size]):
            error_label.config(text="Please fill in all fields.")
            return
        
        command = [
            "python3", "/home/armkh/Documents/code/Nulify/nulify/usr/share/nulify/offline.py",
            str(float(min_width)), str(float(max_width)),
            str(float(min_height)), str(float(max_height)),
            str(float(aruco_size))
        ]

        current_process = subprocess.Popen(command)

    labels = ["Min Width (cm):", "Max Width (cm):", "Min Height (cm):", "Max Height (cm):", "ArUco Size (cm):"]
    entries = []

    for i, label_text in enumerate(labels, start=1):
        ttk.Label(input_frame, text=label_text).grid(row=i, column=0, pady=10, padx=10, sticky="e")
        entry = ttk.Entry(input_frame, font=("Roboto", 12), width=30)
        entry.grid(row=i, column=1, pady=10, padx=10)
        entries.append(entry)

    min_width_entry, max_width_entry, min_height_entry, max_height_entry, aruco_size_entry = entries

    start_button = ttk.Button(input_frame, text="Start Offline Mode", command=start_offline, width=30)
    start_button.grid(row=len(labels)+1, column=0, columnspan=2, pady=20)

    back_button = ttk.Button(input_frame, text="Back to Main Menu", command=show_main_page, width=30)
    back_button.grid(row=len(labels)+2, column=0, columnspan=2, pady=10)

def run_online():
    global current_process
    
    for widget in main_frame.winfo_children():
        widget.destroy()

    current_process = subprocess.Popen(["python3", "/home/armkh/Documents/code/Nulify/nulify/usr/share/nulify/server.py"])

    def open_link():
        subprocess.Popen(["x-www-browser", "http://127.0.0.1:5000/"], start_new_session=True)

    online_frame = ttk.Frame(main_frame, padding="20", style="TFrame")
    online_frame.pack(expand=True)

    ttk.Label(online_frame, text="Online Mode", font=("Roboto", 36), foreground="#00aaff").pack(pady=40)
    
    ttk.Label(online_frame, text="Server is running at:", font=("Roboto", 18)).pack(pady=20)
    
    link_label = ttk.Label(online_frame, text="http://127.0.0.1:5000/", foreground="#00aaff", font=("Roboto", 18))
    link_label.pack(pady=20)
    
    open_button = ttk.Button(online_frame, text="Open in Browser", command=open_link, width=30)
    open_button.pack(pady=30)

    back_button = ttk.Button(online_frame, text="Back to Main Menu", command=show_main_page, width=30)
    back_button.pack(pady=20)

def close_app():
    global current_process
    if current_process:
        current_process.terminate()
    root.quit()

# Create welcome frame (Welcome Page)
welcome_frame = ttk.Frame(root, padding="40", style="TFrame")
welcome_frame.pack(fill="both", expand=True)

welcome_label = ttk.Label(welcome_frame, text="Welcome to NULIFY", font=("Roboto", 48), foreground="#00aaff")
welcome_label.pack(pady=40)

project_description = ttk.Label(welcome_frame, text="This application helps measure object sizes using both online and offline modes.", wraplength=800, font=("Roboto", 18))
project_description.pack(pady=30)

get_started_button = ttk.Button(welcome_frame, text="Get Started", command=show_main_page, width=30)
get_started_button.pack(pady=40)

fullscreen_button = ttk.Button(welcome_frame, text="Toggle Fullscreen", command=toggle_fullscreen, width=20)
fullscreen_button.pack(side="bottom", pady=20)

# Create main frame (Main Page - Offline/Online mode selection)
main_frame = ttk.Frame(root, padding="40", style="TFrame")

# Start the Tkinter main loop
root.mainloop()