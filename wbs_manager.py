# Create a new file: wbs_manager.py
import os
import csv
import tkinter as tk
from tkinter import ttk, messagebox

class WbsManager:
    def __init__(self, parent, base_dir, on_close_callback=None):
        """Initialize the WBS Manager window"""
        self.parent = parent
        self.base_dir = base_dir
        self.on_close_callback = on_close_callback
        self.wbs_file = os.path.join(base_dir, "csv", "wbs_mapping.csv")
        self.dwg_dir = os.path.join(base_dir, "dwg")
        self.mappings = []
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("WBS Management")
        self.window.geometry("700x500")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Frame for the treeview
        frame = ttk.Frame(self.window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with scrollbar
        self.tree = ttk.Treeview(frame, columns=("filename", "wbs_code", "wbs_description"), 
                                 show="headings")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Set column headings and widths
        self.tree.heading("filename", text="Filename")
        self.tree.heading("wbs_code", text="WBS Code")
        self.tree.heading("wbs_description", text="Description")
        self.tree.column("filename", width=300)
        self.tree.column("wbs_code", width=100)
        self.tree.column("wbs_description", width=250)
        
        # Pack the treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add buttons frame
        button_frame = ttk.Frame(self.window, padding="10")
        button_frame.pack(fill=tk.X)
        
        # Entry fields for editing
        edit_frame = ttk.LabelFrame(self.window, text="Edit WBS Information", padding="10")
        edit_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(edit_frame, text="Filename:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.filename_var = tk.StringVar()
        self.filename_entry = ttk.Entry(edit_frame, textvariable=self.filename_var, state='readonly', width=40)
        self.filename_entry.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(edit_frame, text="WBS Code:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.wbs_code_var = tk.StringVar()
        self.wbs_code_entry = ttk.Entry(edit_frame, textvariable=self.wbs_code_var, width=40)
        self.wbs_code_entry.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(edit_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.wbs_desc_var = tk.StringVar()
        self.wbs_desc_entry = ttk.Entry(edit_frame, textvariable=self.wbs_desc_var, width=40)
        self.wbs_desc_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Buttons
        btn_frame = ttk.Frame(self.window, padding="10")
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Update", command=self.update_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Apply to All Unassigned", command=self.apply_to_unassigned).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save Changes", command=self.save_data).pack(side=tk.RIGHT, padx=5)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
    
    def load_data(self):
        """Load WBS mapping data from CSV"""
        self.mappings = []
        # Ensure the file exists
        os.makedirs(os.path.dirname(self.wbs_file), exist_ok=True)
        if not os.path.exists(self.wbs_file):
            with open(self.wbs_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["filename", "wbs_code", "wbs_description"])
    
        # Read existing mappings
        try:
            with open(self.wbs_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                self.mappings = list(reader)
            print(f"Loaded {len(self.mappings)} mappings from file")
        except Exception as e:
            print(f"Error loading WBS file: {str(e)}")
            self.mappings = []
    
        # Get list of DWG files
        dwg_files = []
        if os.path.exists(self.dwg_dir):
            dwg_files = [f for f in os.listdir(self.dwg_dir) if f.endswith('.dwg')]
    
        print(f"Found {len(dwg_files)} DWG files in directory")
    
        # Add DWG files not in mappings
        existing_filenames = {m['filename'] for m in self.mappings}
        for filename in dwg_files:
            if filename not in existing_filenames:
                print(f"Adding new file to mappings: {filename}")
                self.mappings.append({
                    'filename': filename,
                    'wbs_code': '',
                    'wbs_description': ''
                })
    
        # Update treeview
        self.update_treeview()
    
    def update_treeview(self):
        """Update the treeview with current mappings"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add mappings to treeview
        for mapping in self.mappings:
            self.tree.insert('', 'end', values=(
                mapping['filename'],
                mapping['wbs_code'],
                mapping['wbs_description']
            ))
    
    def on_item_select(self, event):
        """Handle item selection in treeview"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        values = self.tree.item(item, 'values')
        
        # Update entry fields
        self.filename_var.set(values[0])
        self.wbs_code_var.set(values[1])
        self.wbs_desc_var.set(values[2])
    
    def update_selected(self):
        """Update the selected item with new WBS information"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No item selected")
            return
    
        item = selected_items[0]
        values = self.tree.item(item, 'values')
        filename = values[0]
    
        # Get new values directly from entry widgets to ensure we have the latest input
        new_wbs_code = self.wbs_code_entry.get()
        new_wbs_desc = self.wbs_desc_entry.get()

        print(f"Updating {filename} with code={new_wbs_code}, desc={new_wbs_desc}")

        # Update mapping in memory
        updated = False
        for i, mapping in enumerate(self.mappings):
            if mapping['filename'] == filename:
                print(f"Found at index {i}, old values: {mapping['wbs_code']}, {mapping['wbs_description']}")
                mapping['wbs_code'] = new_wbs_code
                mapping['wbs_description'] = new_wbs_desc
                updated = True
                print(f"Updated to: {mapping['wbs_code']}, {mapping['wbs_description']}")
                break
    
        if not updated:
            print(f"Warning: {filename} not found in mappings")
    
        # Update treeview
        self.tree.item(item, values=(
            filename,
            new_wbs_code,
            new_wbs_desc
        ))
    
        # Provide feedback
        messagebox.showinfo("Success", f"Updated WBS information for {filename}")
    
    def apply_to_unassigned(self):
        """Apply current WBS code and description to all unassigned files"""
        wbs_code = self.wbs_code_var.get()
        wbs_desc = self.wbs_desc_var.get()
        
        if not wbs_code:
            messagebox.showwarning("Warning", "WBS code cannot be empty")
            return
        
        # Update mappings in memory
        for mapping in self.mappings:
            if not mapping['wbs_code']:
                mapping['wbs_code'] = wbs_code
                mapping['wbs_description'] = wbs_desc
        
        # Update treeview
        self.update_treeview()
    
    def save_data(self):
        """Save mappings to CSV file"""
        try:
            with open(self.wbs_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["filename", "wbs_code", "wbs_description"])
                writer.writeheader()
                writer.writerows(self.mappings)
            # Print debug information
            print(f"Saved {len(self.mappings)} records to {self.wbs_file}")
            for mapping in self.mappings[:3]:  # Print first few for debugging
                print(f"  {mapping['filename']}: {mapping['wbs_code']} - {mapping['wbs_description']}")
            
            messagebox.showinfo("Success", "WBS mappings saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save WBS mappings: {str(e)}")
    
    def on_close(self):
        """Handle window close event"""
        if messagebox.askyesno("Save Changes", "Do you want to save changes before closing?"):
            self.save_data()
        
        self.window.destroy()
        if self.on_close_callback:
            self.on_close_callback()