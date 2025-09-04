import tkinter as tk
from tkinter import filedialog, Canvas, Label, Frame, Button, Scale, HORIZONTAL, messagebox
from PIL import Image, ImageTk, ImageOps, ImageTransform
import numpy as np

class ImageManipulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Manipulator with Crosshairs")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize variables
        self.original_image = None
        self.processed_image = None
        self.image_tk = None
        self.image_id = None
        self.crosshair_h_id = None
        self.crosshair_v_id = None
        self.left_composite = None
        self.right_composite = None
        
        # Transformation parameters
        self.rotation = 0
        self.scale = 1.0
        self.skew_x = 0
        self.skew_y = 0
        self.offset_x = 0
        self.offset_y = 0
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        # Top frame for controls
        control_frame = Frame(self.root, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Load image button
        load_btn = Button(control_frame, text="Load Image", command=self.load_image, 
                         bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        load_btn.pack(side=tk.LEFT, padx=5)
        
        # Show crosshairs button
        self.show_crosshairs_btn = Button(control_frame, text="Show Crosshairs", 
                                         command=self.toggle_crosshairs,
                                         bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        self.show_crosshairs_btn.pack(side=tk.LEFT, padx=5)
        
        # Save images button
        save_btn = Button(control_frame, text="Save Combined Images", 
                         command=self.save_combined_images,
                         bg="#FF9800", fg="white", font=("Arial", 10, "bold"))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Top canvas frame
        top_frame = Frame(self.root, bg="#f0f0f0")
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Top canvas for main image
        self.canvas = Canvas(top_frame, bg="white", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events for dragging
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Transformation controls frame
        transform_frame = Frame(self.root, bg="#f0f0f0")
        transform_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Rotation control
        Label(transform_frame, text="Rotation:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=2)
        self.rotation_slider = Scale(transform_frame, from_=0, to=360, orient=HORIZONTAL, 
                                    command=self.update_rotation, length=200)
        self.rotation_slider.grid(row=0, column=1, padx=5, pady=2)
        
        # Scale control
        Label(transform_frame, text="Scale:", bg="#f0f0f0").grid(row=0, column=2, padx=5, pady=2)
        self.scale_slider = Scale(transform_frame, from_=0.1, to=3.0, resolution=0.1, 
                                 orient=HORIZONTAL, command=self.update_scale, length=200)
        self.scale_slider.set(1.0)
        self.scale_slider.grid(row=0, column=3, padx=5, pady=2)
        
        # Skew X control
        Label(transform_frame, text="Skew X:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=2)
        self.skew_x_slider = Scale(transform_frame, from_=-45, to=45, orient=HORIZONTAL, 
                                  command=self.update_skew_x, length=200)
        self.skew_x_slider.grid(row=1, column=1, padx=5, pady=2)
        
        # Skew Y control
        Label(transform_frame, text="Skew Y:", bg="#f0f0f0").grid(row=1, column=2, padx=5, pady=2)
        self.skew_y_slider = Scale(transform_frame, from_=-45, to=45, orient=HORIZONTAL, 
                                  command=self.update_skew_y, length=200)
        self.skew_y_slider.grid(row=1, column=3, padx=5, pady=2)
        
        # Bottom frame for output images
        bottom_frame = Frame(self.root, bg="#f0f0f0")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left output frame
        left_frame = Frame(bottom_frame, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        Label(left_frame, text="Left Half & Mirror", bg="#f0f0f0", font=("Arial", 10, "bold")).pack()
        self.left_canvas = Canvas(left_frame, bg="white", highlightthickness=1, highlightbackground="#cccccc")
        self.left_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right output frame
        right_frame = Frame(bottom_frame, bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        Label(right_frame, text="Mirror & Right Half", bg="#f0f0f0", font=("Arial", 10, "bold")).pack()
        self.right_canvas = Canvas(right_frame, bg="white", highlightthickness=1, highlightbackground="#cccccc")
        self.right_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Initialize crosshairs
        self.show_crosshairs = False
        
    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        if file_path:
            self.original_image = Image.open(file_path)
            self.processed_image = self.original_image.copy()
            self.display_image()
            self.update_output_images()
    
    def display_image(self):
        if not self.processed_image:
            return
            
        # Resize image to fit canvas while maintaining aspect ratio
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.root.after(100, self.display_image)
            return
            
        img_width, img_height = self.processed_image.size
        
        # Calculate scaling to fit canvas
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        scale = min(scale_x, scale_y) * 0.9  # 90% of canvas size
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Resize image
        display_image = self.processed_image.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage
        self.image_tk = ImageTk.PhotoImage(display_image)
        
        # Clear canvas and display image
        self.canvas.delete("all")
        self.image_id = self.canvas.create_image(
            canvas_width/2 + self.offset_x, 
            canvas_height/2 + self.offset_y,
            image=self.image_tk,
            anchor=tk.CENTER
        )
        
        # Draw crosshairs if enabled
        if self.show_crosshairs:
            self.draw_crosshairs()
    
    def draw_crosshairs(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Draw horizontal crosshair
        self.crosshair_h_id = self.canvas.create_line(
            0, canvas_height/2, canvas_width, canvas_height/2,
            fill="black", width=1, dash=(4, 4)
        )
        
        # Draw vertical crosshair
        self.crosshair_v_id = self.canvas.create_line(
            canvas_width/2, 0, canvas_width/2, canvas_height,
            fill="black", width=1, dash=(4, 4)
        )
        
        # Bring crosshairs to front
        self.canvas.tag_raise(self.crosshair_h_id)
        self.canvas.tag_raise(self.crosshair_v_id)
    
    def toggle_crosshairs(self):
        self.show_crosshairs = not self.show_crosshairs
        
        if self.show_crosshairs:
            self.draw_crosshairs()
            self.show_crosshairs_btn.config(text="Hide Crosshairs")
        else:
            if self.crosshair_h_id:
                self.canvas.delete(self.crosshair_h_id)
            if self.crosshair_v_id:
                self.canvas.delete(self.crosshair_v_id)
            self.show_crosshairs_btn.config(text="Show Crosshairs")
    
    def update_rotation(self, value):
        self.rotation = int(value)
        self.apply_transformations()
    
    def update_scale(self, value):
        self.scale = float(value)
        self.apply_transformations()
    
    def update_skew_x(self, value):
        self.skew_x = int(value)
        self.apply_transformations()
    
    def update_skew_y(self, value):
        self.skew_y = int(value)
        self.apply_transformations()
    
    def apply_transformations(self):
        if not self.original_image:
            return
            
        # Start with original image
        img = self.original_image.copy()
        
        # Apply rotation
        if self.rotation != 0:
            img = img.rotate(self.rotation, expand=True)
        
        # Apply scaling
        if self.scale != 1.0:
            new_width = int(img.width * self.scale)
            new_height = int(img.height * self.scale)
            img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Apply skewing
        if self.skew_x != 0 or self.skew_y != 0:
            # Convert skew angles to radians
            skew_x_rad = np.radians(self.skew_x)
            skew_y_rad = np.radians(self.skew_y)
            
            # Create transformation matrix
            transform_matrix = (
                1, np.tan(skew_x_rad), 0,
                np.tan(skew_y_rad), 1, 0,
                0, 0, 1
            )
            
            # Apply perspective transformation
            img = img.transform(
                img.size,
                Image.PERSPECTIVE,
                transform_matrix,
                Image.BICUBIC
            )
        
        self.processed_image = img
        self.display_image()
        self.update_output_images()
    
    def update_output_images(self):
        if not self.processed_image:
            return
            
        img_width, img_height = self.processed_image.size
        
        # Split image into left and right halves
        left_half = self.processed_image.crop((0, 0, img_width//2, img_height))
        right_half = self.processed_image.crop((img_width//2, 0, img_width, img_height))
        
        # Create mirrored versions
        left_mirror = ImageOps.mirror(left_half)
        right_mirror = ImageOps.mirror(right_half)
        
        # Create composite images
        self.left_composite = self.create_composite(left_half, left_mirror)
        # Right composite shows mirror first, then original
        self.right_composite = self.create_composite(right_mirror, right_half)
        
        # Display in canvases
        self.display_in_canvas(self.left_canvas, self.left_composite)
        self.display_in_canvas(self.right_canvas, self.right_composite)
    
    def create_composite(self, left_image, right_image):
        # Create a new image with both images side by side
        width = left_image.width + right_image.width
        height = max(left_image.height, right_image.height)
        
        composite = Image.new('RGB', (width, height))
        composite.paste(left_image, (0, 0))
        composite.paste(right_image, (left_image.width, 0))
        
        return composite
    
    def display_in_canvas(self, canvas, image):
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.root.after(100, lambda: self.display_in_canvas(canvas, image))
            return
            
        img_width, img_height = image.size
        
        # Calculate scaling to fit canvas
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        scale = min(scale_x, scale_y) * 0.9  # 90% of canvas size
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Resize image
        display_image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage
        image_tk = ImageTk.PhotoImage(display_image)
        
        # Clear canvas and display image
        canvas.delete("all")
        canvas.create_image(
            canvas_width/2, canvas_height/2,
            image=image_tk,
            anchor=tk.CENTER
        )
        
        # Keep a reference to prevent garbage collection
        canvas.image_tk = image_tk
    
    def save_combined_images(self):
        if not self.left_composite or not self.right_composite:
            messagebox.showwarning("Warning", "No images to save. Please load an image first.")
            return
            
        # Create a new image that combines left and right composites
        combined_width = self.left_composite.width + self.right_composite.width
        combined_height = max(self.left_composite.height, self.right_composite.height)
        
        combined_image = Image.new('RGB', (combined_width, combined_height))
        combined_image.paste(self.left_composite, (0, 0))
        combined_image.paste(self.right_composite, (self.left_composite.width, 0))
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
            title="Save Combined Image"
        )
        
        if file_path:
            try:
                combined_image.save(file_path)
                messagebox.showinfo("Success", f"Image saved successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")
    
    def on_canvas_click(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def on_canvas_drag(self, event):
        if not self.image_id:
            return
            
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        self.canvas.move(self.image_id, dx, dy)
        
        # Update offset for future transformations
        self.offset_x += dx
        self.offset_y += dy
        
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        # Redraw crosshairs if enabled
        if self.show_crosshairs:
            if self.crosshair_h_id:
                self.canvas.delete(self.crosshair_h_id)
            if self.crosshair_v_id:
                self.canvas.delete(self.crosshair_v_id)
            self.draw_crosshairs()
    
    def on_canvas_release(self, event):
        self.update_output_images()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageManipulatorApp(root)
    root.mainloop()