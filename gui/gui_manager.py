# File: gui/gui_manager.py

import tkinter as tk
from tkinter import messagebox

class GuiManager:
    def __init__(self, root: tk.Tk, processor):
        self.root = root
        self.processor = processor
        self.setup_gui()

    def setup_gui(self):
        """Setup the GUI elements"""
        self.root.title("Electrical MTO Automation")
        self.root.iconbitmap('gui/ten.ico')
        self.root.minsize(350, 175)

        # Create main section
        self.subsection = tk.LabelFrame(self.root, text="Lighting MTO", padx=10, pady=10)
        self.subsection.pack(padx=10, pady=10, fill="both", expand="yes")

        # Create buttons
        self.create_buttons()

    def create_buttons(self):
        """Create and configure buttons"""
        buttons = [
            ("Extract Electrical Lighting Assemblies", self.handle_extract),
            ("Detect Assemblies in Lighting Layouts", self.handle_cad),
            ("Manage WBS", self.handle_wbs),
            ("Generate Lighting Material Take-Off", self.handle_mto),
            ("Format MTO to Excel Template", self.handle_format_mto)
        ]

        for text, command in buttons:
            btn = tk.Button(self.subsection, text=text, command=command)
            btn.pack(pady=10)

    def show_result(self, success: bool, message: str):
        """Show operation result to user"""
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def handle_extract(self):
        """Handle extract button click"""
        success, message = self.processor.execute_extract()
        self.show_result(success, message)

    def handle_cad(self):
        """Handle CAD button click"""
        success, message = self.processor.execute_cad()
        self.show_result(success, message)

    def handle_wbs(self):
        """Handle WBS button click"""
        success, message = self.processor.manage_wbs()
        self.show_result(success, message)

    def handle_mto(self):
        """Handle MTO button click"""
        success, message = self.processor.execute_mto()
        self.show_result(success, message)
    
    def handle_format_mto(self):
        """Handle format MTO button click"""
        success, message = self.processor.format_mto_template()
        self.show_result(success, message)

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()