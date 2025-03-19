# File: design_allowance_manager.py

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox

class DesignAllowanceManager:
    def __init__(self, parent, base_dir, on_close_callback=None):
        """Initialize the Design Allowance Manager window"""
        self.parent = parent
        self.base_dir = base_dir
        self.on_close_callback = on_close_callback
        self.config_file = os.path.join(base_dir, "config", "design_allowance.json")
        print(f"Design Allowance Manager initialized with config file: {self.config_file}")
        
        # Default allowance percentage
        self.allowance_pct = 10
        print(f"Default allowance: {self.allowance_pct}%")
        
        # Load saved value if exists
        self.load_config()
        print(f"After loading config: allowance_pct = {self.allowance_pct}%")
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Design Growth Allowance Manager")
        self.window.geometry("400x225")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Explanatory text
        ttk.Label(frame, text="Set the Design Growth Allowance percentage to apply to all materials.", 
                wraplength=360).pack(pady=(0, 15))
        
        # Entry field with label and % sign
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Allowance Percentage:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.pct_var = tk.StringVar(value=str(self.allowance_pct))
        vcmd = (self.window.register(self.validate_numeric), '%P')
        self.pct_entry = ttk.Entry(input_frame, textvariable=self.pct_var, width=8, validate='key', validatecommand=vcmd)
        self.pct_entry.pack(side=tk.LEFT)
        
        # Debug label to show current entry value
        self.debug_var = tk.StringVar(value=f"Current value: {self.pct_var.get()}")
        self.debug_label = ttk.Label(input_frame, textvariable=self.debug_var)
        self.debug_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Update the debug label whenever the entry changes
        self.pct_var.trace_add("write", self.update_debug_label)
        
        ttk.Label(input_frame, text="%").pack(side=tk.LEFT, padx=(2, 0))
        
        # Info text
        ttk.Label(frame, text="This percentage will be applied to the total quantity of each material\n"
                            "to calculate additional quantity for design changes.",
                 justify=tk.LEFT).pack(pady=(10, 20))
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Apply", command=self.save_config).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        
    def update_debug_label(self, *args):
        """Update the debug label with current entry value"""
        current_val = self.pct_entry.get()
        self.debug_var.set(f"Current value: {current_val}")
    
    def load_config(self):
        """Load design allowance percentage from config file"""
        print(f"Attempting to load config from: {self.config_file}")
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        if os.path.exists(self.config_file):
            print(f"Config file exists")
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    old_pct = self.allowance_pct
                    self.allowance_pct = config.get('allowance_pct', 10)
                    print(f"Loaded design allowance: {old_pct}% -> {self.allowance_pct}%")
            except Exception as e:
                print(f"Error loading design allowance config: {str(e)}")
        else:
            print(f"Config file does not exist yet, will use default: {self.allowance_pct}%")
    
    def save_config(self):
        """Save design allowance percentage to config file"""
        try:
            # Get value directly from the entry widget instead of the StringVar
            input_val = self.pct_entry.get()
            print(f"Raw input value from entry widget: '{input_val}'")
            
            try:
                pct = float(input_val)
                print(f"Converted to float: {pct}")
                if pct < 0:
                    messagebox.showerror("Error", "Allowance percentage cannot be negative")
                    return
            except ValueError as ve:
                print(f"Value error: {ve}")
                messagebox.showerror("Error", "Please enter a valid number")
                return
            
            # Save the value
            self.allowance_pct = pct
            print(f"Set self.allowance_pct to {self.allowance_pct}")
            
            # Create config directory if it doesn't exist
            config_dir = os.path.dirname(self.config_file)
            print(f"Config directory: {config_dir}")
            os.makedirs(config_dir, exist_ok=True)
            
            # Write to config file
            print(f"Writing to config file: {self.config_file}")
            data = {'allowance_pct': self.allowance_pct}
            with open(self.config_file, 'w') as f:
                json.dump(data, f)
            
            # Verify the file was written
            if os.path.exists(self.config_file):
                print(f"Config file created/updated successfully")
                # Double-check the content
                with open(self.config_file, 'r') as f:
                    saved_data = json.load(f)
                    print(f"Saved data: {saved_data}")
            else:
                print(f"Warning: Config file not found after save attempt")
            
            messagebox.showinfo("Success", f"Design allowance set to {pct}%")
            self.window.destroy()
            
            # Call callback if provided
            if self.on_close_callback:
                print("Calling on_close_callback")
                self.on_close_callback()
            else:
                print("No on_close_callback provided")
                
        except Exception as e:
            print(f"Exception in save_config: {str(e)}")
            messagebox.showerror("Error", f"Failed to save design allowance: {str(e)}")
    
    def validate_numeric(self, value):
        """Validate that entry only accepts numbers and decimal point"""
        if value == "":
            return True
            
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def on_close(self):
        """Handle window close event"""
        self.window.destroy()
        if self.on_close_callback:
            self.on_close_callback()


def get_design_allowance(base_dir):
    """Utility function to get the current design allowance percentage"""
    config_file = os.path.join(base_dir, "config", "design_allowance.json")
    print(f"Getting design allowance from: {config_file}")
    
    # Default value
    default_pct = 10
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                pct = config.get('allowance_pct', default_pct)
                print(f"Loaded design allowance: {pct}% from config file")
                return pct
        except Exception as e:
            print(f"Error reading design allowance: {str(e)}")
            print(f"Using default: {default_pct}%")
    else:
        print(f"Config file not found. Using default: {default_pct}%")
            
    return default_pct