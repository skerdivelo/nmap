import socket
import threading
import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Store results temporarily
scan_results = []

# Function to scan a specific IP and port
def scan_ip(ip, port, endpoint):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(1)  # Timeout after 1 second if the port is closed
    result = s.connect_ex((ip, port))  # Returns 0 if port is open
    if result == 0:
        check_supervisor(ip, port, endpoint)
    s.close()

# Function to check if the endpoint exists on the server
def check_supervisor(ip, port, endpoint):
    url = f"http://{ip}:{port}{endpoint}"
    try:
        response = requests.get(url, timeout=2)  # 2-second timeout for the request
        if response.status_code == 200:
            scan_results.append(f"IP: {ip}{endpoint} è disponibile.\n")
        else:
            scan_results.append(f"IP: {ip} ha risposto, ma {endpoint} non trovato.\n")
    except requests.RequestException:
        pass  # Ignore request errors

# Function to scan multiple IPs on a given range of ports
def scan_range(start_ip, end_ip, port, endpoint):
    start_parts = list(map(int, start_ip.split('.')))
    end_parts = list(map(int, end_ip.split('.')))

    # Loop through the range of IP addresses
    for i in range(start_parts[3], end_parts[3] + 1):
        ip = f"{start_parts[0]}.{start_parts[1]}.{start_parts[2]}.{i}"
        thread = threading.Thread(target=scan_ip, args=(ip, port, endpoint))
        thread.start()

# Function to start the scan when the button is pressed
def start_scan():
    global scan_results  # Reference the global results list
    scan_results = []  # Clear previous results

    start_ip = start_ip_entry.get()
    end_ip = end_ip_entry.get()
    endpoint = endpoint_entry.get()
    port = int(port_entry.get())

    if not start_ip or not end_ip or not port:
        messagebox.showerror("Errore di Input", "Per favore, compila tutti i campi")
        return

    # Clear the output box
    output_textbox.delete(1.0, tk.END)

    # Start scanning the given IP range
    scan_range(start_ip, end_ip, port, endpoint)

    # Wait for threads to finish before sorting and displaying results
    output_textbox.after(100, display_results)

# Function to display the sorted results in the output textbox
def display_results():
    # Sort results: "è disponibile" first
    sorted_results = sorted(scan_results, key=lambda x: "è disponibile" in x, reverse=True)
    for result in sorted_results:
        output_textbox.insert(tk.END, result)
    
# Create the GUI window
root = tk.Tk()
root.title("Scanner Porte IP")

# Set a background color and style
root.configure(bg="#2E2E2E")
root.option_add("*Font", "Helvetica 12")
root.option_add("*foreground", "white")

# Configure grid weight for responsiveness
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# GUI elements
# Default starting IP range
start_ip_label = tk.Label(root, text="IP Iniziale:", bg="#2E2E2E", fg="#A8DADC")
start_ip_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
start_ip_entry = tk.Entry(root, bg="#3A3A3A", fg="#F1FAEE", insertbackground='white')
start_ip_entry.insert(0, "192.168.111.0")  # Set default value for starting IP
start_ip_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

end_ip_label = tk.Label(root, text="IP Finale:", bg="#2E2E2E", fg="#A8DADC")
end_ip_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
end_ip_entry = tk.Entry(root, bg="#3A3A3A", fg="#F1FAEE", insertbackground='white')
end_ip_entry.insert(0, "192.168.111.254")  # Set default value for ending IP
end_ip_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")


endpoint_label = tk.Label(root, text="Endpoint (predefinito: /Hi4Supervisor):", bg="#2E2E2E", fg="#A8DADC")
endpoint_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
endpoint_entry = tk.Entry(root, bg="#3A3A3A", fg="#F1FAEE", insertbackground='white')
endpoint_entry.insert(0, "/Hi4Supervisor")  # Set default value
endpoint_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

port_label = tk.Label(root, text="Porta:", bg="#2E2E2E", fg="#A8DADC")
port_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
port_entry = tk.Entry(root, bg="#3A3A3A", fg="#F1FAEE", insertbackground='white')
port_entry.insert(0, "8080")  # Default to port 8080
port_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

# Button to start the scan
start_button = tk.Button(root, text="Inizia Scansione", command=start_scan, bg="#A8DADC", fg="#2E2E2E", activebackground="#F1FAEE")
start_button.grid(row=4, column=0, columnspan=2, pady=10)

# Output Textbox with Scrollbar
output_textbox = scrolledtext.ScrolledText(root, height=15, width=60, wrap=tk.WORD, bg="#3A3A3A", fg="#F1FAEE")
output_textbox.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

# Start the GUI main loop
root.mainloop()
