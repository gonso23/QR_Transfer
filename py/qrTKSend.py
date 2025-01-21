import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import zipfile
import os
from QRTD import QSR, QRTD_type

class QRCopyRder:
    def __init__(self, root):
        self.root = root
        self.root.title("QRCopyR")
        
        # Set screen width and height
        self.screen_width = 600
        self.screen_height = 600
        
        # Initialize variables
        self.images = []
        self.current_image_index = 0
        
        self.s = QSR()
        
        # Create GUI components
        self.create_widgets()
        
    def create_widgets(self):
        # Picture area
        self.picture_area = tk.Label(self.root, bg="gray", text="opened files will be packed to zip, split and coded as QR", 
                                     font=("Helvetica", 12), fg="white", wraplength=self.screen_width, justify="center")
        self.picture_area.pack(expand=True, fill=tk.BOTH)
        
        # Buttons and text area
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()
        
        self.open_button = tk.Button(self.button_frame, text="Open File", command=self.open_file)
        self.open_button.grid(row=0, column=0)
        
        self.prev_button = tk.Button(self.button_frame, text="<", command=self.show_prev_image)
        self.prev_button.grid(row=0, column=1)
        
        self.image_info = tk.Label(self.button_frame, text="0 / 0")
        self.image_info.grid(row=0, column=2)
        
        self.next_button = tk.Button(self.button_frame, text=">", command=self.show_next_image)
        self.next_button.grid(row=0, column=3)
        
        self.clear_button = tk.Button(self.button_frame, text="Clear", command=self.clear_images)
        self.clear_button.grid(row=0, column=4)
        
    def open_file(self):
        # Clear existing images
        self.clear_images()
        
        # Open file dialog to select multiple files
        file_paths = filedialog.askopenfilenames()
        
        if file_paths:
            #todo: do not zip in case of one zip file selected
            # Create a temporary ZIP archive
            with zipfile.ZipFile('temp.zip', 'w') as temp_zip:
                for file_path in file_paths:
                    temp_zip.write(file_path, os.path.basename(file_path))
            
            # Read the ZIP archive
            with open('temp.zip', 'rb') as f:
                zip_data = f.read()
            
            os.remove('temp.zip')
            
            self.s.send(QRTD_type.ZIP_BINARY,zip_data)
            
            for img in self.s.images:    
                # Resize image to fit screen
                img = img.resize((self.screen_width, self.screen_height), Image.LANCZOS)
                self.images.append(ImageTk.PhotoImage(img))
            
            # Display the first image
            if len(self.images) > 0:
                self.current_image_index = 0
                self.update_image()
                
    def show_prev_image(self):
        if len(self.images) > 0 and self.current_image_index > 0:
            self.current_image_index -= 1
            self.update_image()
            
    def show_next_image(self):
        if len(self.images) > 0 and self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
            self.update_image()
            
    def clear_images(self):
        self.s = QSR()
        self.images = []
        self.current_image_index = 0
        self.update_image()
        
    def update_image(self):
        if len(self.images) > 0:
            self.picture_area.config(image=self.images[self.current_image_index], text="")
            self.image_info.config(text=f"{self.current_image_index + 1} / {len(self.images)}")
        else:
            self.picture_area.config(image="", text="    opened files will be packed to zip, splited to be coded as QR   ", bg="gray")
            self.image_info.config(text="0 / 0")

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCopyRder(root)
    root.mainloop()