"""
ss_steganography.py - Main application for SS Steganography

A graphical user interface for advanced steganography operations, allowing
users to hide and retrieve messages in images using strong encryption.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading
import time

from steganography import AdvancedSteganography

class SteganographyApp:
    """Main application class for the SS Steganography GUI."""

    def __init__(self, root):
        """Initialize the application window and components."""
        self.root = root
        self.root.title("SS Steganography")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Center the window on screen
        self._center_window()

        # Set application icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except tk.TclError:
            pass  # Icon not found, skip

        # Initialize the steganography engine
        self.stego = AdvancedSteganography()

        # Variables
        self.image_path = tk.StringVar()
        self.message = tk.StringVar()
        self.password = tk.StringVar()
        self.status = tk.StringVar(value="Ready")
        self.operation = tk.StringVar(value="encode")
        self.use_password = tk.BooleanVar(value=False)

        # Set up dark theme
        self._setup_dark_theme()

        # Create the UI
        self._create_ui()        # Thread for background operations
        self.working_thread = None

    def _center_window(self):
        """Center the application window on the screen."""
        # Wait for the window to be drawn before calculating positions
        self.root.update_idletasks()

        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Get window width and height
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # Calculate position coordinates
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Set window position
        self.root.geometry(f"+{x}+{y}")

    def _setup_dark_theme(self):
        """Configure dark theme colors and styles."""
        # Define colors
        self.colors = {
            "bg_dark": "#2E2E2E",
            "bg_medium": "#3E3E3E",
            "bg_light": "#4E4E4E",
            "fg_main": "#E0E0E0",
            "fg_accent": "#FFFFFF",
            "accent": "#007BFF",
            "error": "#FF5252",
            "success": "#4CAF50",
            "warning": "#FFC107"
        }

        # Configure ttk styles
        style = ttk.Style()

        # Main window background
        self.root.configure(background=self.colors["bg_dark"])        # Configure ttk styles for dark theme
        style.configure("TFrame", background=self.colors["bg_dark"])
        style.configure("TLabel", background=self.colors["bg_dark"], foreground=self.colors["fg_main"])
        style.configure("TCheckbutton", background=self.colors["bg_dark"], foreground=self.colors["fg_main"])
        style.configure("TRadiobutton", background=self.colors["bg_dark"], foreground=self.colors["fg_main"])
        style.configure("TEntry", fieldbackground=self.colors["bg_medium"], foreground=self.colors["fg_main"])

        # Custom button style with better contrast
        style.configure("TButton",
                        background=self.colors["accent"],  # Use accent color for better visibility
                        foreground=self.colors["bg_dark"])  # White text on accent background

        # Map different button states
        style.map("TButton",
                 foreground=[('pressed', self.colors["fg_accent"]),
                             ('active', self.colors["fg_accent"])],
                 background=[('pressed', '!disabled', self.colors["bg_light"]),
                             ('active', self.colors["accent"])])

        # Special styles
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), background=self.colors["bg_dark"],
                       foreground=self.colors["fg_accent"])
        style.configure("Status.TLabel", background=self.colors["bg_medium"], foreground=self.colors["fg_main"])

        # Labelframe styles
        style.configure("TLabelframe", background=self.colors["bg_dark"])
        style.configure("TLabelframe.Label", background=self.colors["bg_dark"], foreground=self.colors["accent"])

        # Progressbar
        style.configure("TProgressbar", background=self.colors["accent"])

    def _create_ui(self):
        """Create the user interface components."""
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header = ttk.Label(frame, text="SS Steganography", style="Header.TLabel")
        header.grid(row=0, column=0, columnspan=3, pady=10)

        # Operation selection
        op_frame = ttk.LabelFrame(frame, text="Operation", padding=10)
        op_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        encode_radio = ttk.Radiobutton(op_frame, text="Hide Message (Encode)",
                                      variable=self.operation, value="encode")
        decode_radio = ttk.Radiobutton(op_frame, text="Extract Message (Decode)",
                                      variable=self.operation, value="decode")
        encode_radio.grid(row=0, column=0, padx=5, sticky="w")
        decode_radio.grid(row=0, column=1, padx=5, sticky="w")

        # Image selection
        img_frame = ttk.LabelFrame(frame, text="Image Selection", padding=10)
        img_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        ttk.Label(img_frame, text="Image:").grid(row=0, column=0, sticky="w")
        entry_img = ttk.Entry(img_frame, textvariable=self.image_path, width=50)
        entry_img.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.btn_browse = ttk.Button(img_frame, text="Browse...", command=self._browse_image)
        self.btn_browse.grid(row=0, column=2, padx=5, pady=5)

        # Image preview
        self.preview_frame = ttk.LabelFrame(frame, text="Image Preview", padding=10)
        self.preview_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        frame.rowconfigure(3, weight=1)

        self.image_label = ttk.Label(self.preview_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # Message input
        msg_frame = ttk.LabelFrame(frame, text="Message", padding=10)
        msg_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        # Configure text widget colors for dark theme
        self.message_text = tk.Text(msg_frame, height=5, width=50, wrap=tk.WORD,
                               bg=self.colors["bg_medium"], fg=self.colors["fg_main"],
                               insertbackground=self.colors["fg_main"])
        self.message_text.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        msg_frame.columnconfigure(0, weight=1)

        # Password
        pw_frame = ttk.LabelFrame(frame, text="Security", padding=10)
        pw_frame.grid(row=5, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.use_pw_check = ttk.Checkbutton(pw_frame, text="Use Password (Optional)",
                                           variable=self.use_password,
                                           command=self._toggle_password)
        self.use_pw_check.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        ttk.Label(pw_frame, text="Password:").grid(row=1, column=0, sticky="w", padx=5)
        self.entry_pw = ttk.Entry(pw_frame, textvariable=self.password, show="*", width=30)
        self.entry_pw.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.entry_pw.configure(state="disabled")

        # Action buttons
        btn_frame = ttk.Frame(frame, padding=10)
        btn_frame.grid(row=6, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.btn_action = ttk.Button(btn_frame, text="Encode Message", command=self._process_action)
        self.btn_action.pack(side=tk.RIGHT, padx=5)

        self.btn_clear = ttk.Button(btn_frame, text="Clear", command=self._clear_form)
        self.btn_clear.pack(side=tk.RIGHT, padx=5)

        # Status bar
        status_frame = ttk.Frame(frame, relief=tk.SUNKEN, padding=(2, 2))
        status_frame.grid(row=7, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        self.progress = ttk.Progressbar(status_frame, mode='indeterminate', length=100)
        self.progress.pack(side=tk.LEFT, padx=5)

        ttk.Label(status_frame, textvariable=self.status, style="Status.TLabel").pack(side=tk.LEFT, padx=5)

        # Bind operation change to update UI
        self.operation.trace_add("write", self._update_ui_for_operation)

        # Make columns expandable
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

    def _toggle_password(self):
        """Enable or disable password field based on checkbox."""
        if self.use_password.get():
            self.entry_pw.configure(state="normal")
        else:
            self.password.set("")
            self.entry_pw.configure(state="disabled")

    def _browse_image(self):
        """Open file dialog to select an image."""
        file_types = [
            ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
            ("All files", "*.*")
        ]
        image_path = filedialog.askopenfilename(title="Select Image",
                                               filetypes=file_types)
        if image_path:
            self.image_path.set(image_path)
            self._display_image(image_path)

    def _display_image(self, image_path):
        """Display the selected image in the preview area."""
        try:
            # Open and resize the image for preview
            img = Image.open(image_path)
            img.thumbnail((400, 300))  # Resize for preview

            # Convert to PhotoImage and display
            photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=photo)
            self.image_label.image = photo  # Keep a reference

            # Show image info
            width, height = img.size
            format_type = img.format if img.format else "Unknown"
            self.preview_frame.configure(text=f"Image Preview: {width}x{height} {format_type}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.image_label.configure(image=None)
            self.image_label.image = None

    def _update_ui_for_operation(self, *args):
        """Update UI elements based on selected operation."""
        operation = self.operation.get()

        if operation == "encode":
            self.btn_action.configure(text="Encode Message")
            self.message_text.configure(state="normal")
        else:  # decode
            self.btn_action.configure(text="Decode Message")
            self.message_text.delete(1.0, tk.END)
            self.message_text.configure(state="normal")

    def _process_action(self):
        """Handle the main encode/decode action."""
        # Validate inputs
        image_path = self.image_path.get()
        if not image_path or not os.path.isfile(image_path):
            messagebox.showerror("Error", "Please select a valid image file.")
            return

        # Get password if enabled
        password = None
        if self.use_password.get():
            password = self.password.get()
            if not password:
                messagebox.showerror("Error", "Please enter a password or uncheck the 'Use Password' option.")
                return

        operation = self.operation.get()

        if operation == "encode":
            # Get message from text widget
            message = self.message_text.get(1.0, tk.END).strip()
            if not message:
                messagebox.showerror("Error", "Please enter a message to hide.")
                return

            # Start the encoding process in a separate thread
            self._start_operation(self._encode_image, image_path, message, password)

        else:  # decode
            # Start the decoding process in a separate thread
            self._start_operation(self._decode_image, image_path, password)

    def _start_operation(self, target_func, *args):
        """Start an operation in a background thread with UI updates."""
        # Disable UI during operation
        self._set_ui_state("disabled")
        self.progress.start(10)
        self.status.set("Processing...")

        # Start thread
        self.working_thread = threading.Thread(target=self._run_operation,
                                              args=(target_func, *args))
        self.working_thread.daemon = True
        self.working_thread.start()

    def _run_operation(self, target_func, *args):
        """Run an operation and update the UI when complete."""
        try:
            result = target_func(*args)

            # Schedule UI update in the main thread
            self.root.after(0, self._operation_complete, result)

        except Exception as e:
            # Schedule error display in the main thread
            self.root.after(0, self._operation_error, str(e))

    def _operation_complete(self, result):
        """Handle completion of an operation."""
        self.progress.stop()
        self._set_ui_state("normal")

        if self.operation.get() == "encode":
            messagebox.showinfo("Success", f"Message hidden successfully!\nImage saved to: {result}")
            self.status.set("Message encoded successfully")
        else:
            if result:
                # Display the decoded message
                self.message_text.delete(1.0, tk.END)
                self.message_text.insert(tk.END, result)
                self.status.set("Message decoded successfully")
            else:
                messagebox.showerror("Error", "Failed to decode message. Invalid password or no message found.")
                self.status.set("Decoding failed")

    def _operation_error(self, error_msg):
        """Handle errors during an operation."""
        self.progress.stop()
        self._set_ui_state("normal")
        messagebox.showerror("Error", f"Operation failed: {error_msg}")
        self.status.set("Operation failed")

    def _encode_image(self, image_path, message, password):
        """Perform the encode operation."""
        # Get the directory and filename for the output
        directory = os.path.dirname(image_path)
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)

        # Create output path
        output_path = os.path.join(directory, f"{name}_stego.png")

        # Encode the message
        result = self.stego.encode(image_path, message, password, output_path)

        # Simulate some processing time for small images
        time.sleep(0.5)

        return result

    def _decode_image(self, image_path, password):
        """Perform the decode operation."""
        # Decode the message
        result = self.stego.decode(image_path, password)

        # Simulate some processing time for small images
        time.sleep(0.5)

        return result

    def _set_ui_state(self, state):
        """Enable or disable UI elements during processing."""
        widgets = [
            self.btn_action,
            self.btn_clear,
            self.message_text,
            self.btn_browse,
            self.use_pw_check
        ]

        for widget in widgets:
            widget.configure(state=state)

        # Only enable password field if use_password is checked
        if state == "normal" and self.use_password.get():
            self.entry_pw.configure(state="normal")
        else:
            self.entry_pw.configure(state="disabled")

    def _clear_form(self):
        """Reset the form to its initial state."""
        self.image_path.set("")
        self.message_text.delete(1.0, tk.END)
        self.password.set("")
        self.use_password.set(False)
        self.entry_pw.configure(state="disabled")
        self.image_label.configure(image=None)
        self.image_label.image = None
        self.preview_frame.configure(text="Image Preview")
        self.status.set("Ready")


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
