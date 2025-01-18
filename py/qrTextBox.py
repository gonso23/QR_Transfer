import tkinter as tk
from tkinter import ttk, messagebox
import qrcode
from PIL import Image, ImageTk

# Define maximum capacities for error correction levels (in bytes)
MAX_CAPACITIES = {
    "Low (L)": 2953,
    "Medium (M)": 2331,
    "Quartile (Q)": 1663,
    "High (H)": 1273
}

# Function to update the info label with the remaining capacity
def update_info_label():
    text = text_entry.get("1.0", tk.END).strip()
    error_correction = error_correction_var.get()

    # Get maximum capacity based on error correction level
    max_capacity = MAX_CAPACITIES[error_correction]

    # Calculate remaining capacity
    current_bytes = len(text.encode('utf-8'))
    remaining_capacity = max_capacity - current_bytes

    # Update info label with remaining capacity
    if remaining_capacity < 0:
        info_label.config(text=f"Remaining capacity: {remaining_capacity}", fg="red")
    else:
        info_label.config(text=f"Remaining capacity: {remaining_capacity}", fg="black")

# Function to clear the text entry
def clear_text():
    text_entry.delete("1.0", tk.END)
    update_info_label()

# Function to generate QR code
def generate_qr():
    text = text_entry.get("1.0", tk.END).strip()
    error_correction = error_correction_var.get()
    qr_size = int(size_entry.get())

    # Set error correction level
    if error_correction == "Low (L)":
        error_correction_level = qrcode.constants.ERROR_CORRECT_L
    elif error_correction == "Medium (M)":
        error_correction_level = qrcode.constants.ERROR_CORRECT_M
    elif error_correction == "Quartile (Q)":
        error_correction_level = qrcode.constants.ERROR_CORRECT_Q
    else:
        error_correction_level = qrcode.constants.ERROR_CORRECT_H

    # Create QR code instance with larger box size
    qr = qrcode.QRCode(
        version=None,
        error_correction=error_correction_level,
        box_size=20,  # Increase box size to make the image larger
        border=4,
    )

    # Add data to QR code
    try:
        qr.add_data(text)
        qr.make(fit=True)
        
        # Create an image from the QR Code instance
        img = qr.make_image(fill='black', back_color='white')
        
        # Check if resize will not lead to reduction in size
        if img.size[0] < qr_size or img.size[1] < qr_size:
            img = img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)  # Resize to larger dimensions
        
        # Display the QR code in a new window
        display_qr_code(img)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to display the QR code in a new window
def display_qr_code(img):
    qr_window = tk.Toplevel(root)
    qr_window.title("Generated QR Code")
    
    img = ImageTk.PhotoImage(img)
    
    qr_label = tk.Label(qr_window, image=img)
    qr_label.image = img  # Keep a reference to avoid garbage collection
    qr_label.pack(padx=10, pady=10)

# Create main window
root = tk.Tk()
root.title("QR Code Generator")

# Create and place widgets
text_frame = tk.Frame(root)
text_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

text_entry = tk.Text(text_frame, height=10, width=80, wrap="word")
text_entry.pack(side="left", fill="both", expand=True)
text_entry.bind("<KeyRelease>", lambda event: update_info_label())

scrollbar = tk.Scrollbar(text_frame, command=text_entry.yview)
scrollbar.pack(side="right", fill="y")
text_entry.config(yscrollcommand=scrollbar.set)

tk.Label(root, text="Error Correction:").grid(row=1, column=0, padx=10, pady=10)
error_correction_var = tk.StringVar(value="Medium (M)")
error_correction_menu = ttk.Combobox(root, textvariable=error_correction_var)
error_correction_menu['values'] = ("Low (L)", "Medium (M)", "Quartile (Q)", "High (H)")
error_correction_menu.grid(row=1, column=1, padx=10, pady=10)
error_correction_menu.bind("<<ComboboxSelected>>", lambda event: update_info_label())

tk.Label(root, text="Size:").grid(row=1, column=2, padx=10, pady=10)
size_entry = tk.Entry(root)
size_entry.insert(0, "500")
size_entry.grid(row=1, column=3, padx=10, pady=10)

clear_button = tk.Button(root, text="Clear", command=clear_text)
clear_button.grid(row=2, column=0, pady=20)

generate_button = tk.Button(root, text="Generate QR", command=generate_qr)
generate_button.grid(row=2, column=1, columnspan=3, pady=20)

info_label = tk.Label(root, text="Remaining capacity: 2331")
info_label.grid(row=3, columnspan=4)

# Run the application
root.mainloop()