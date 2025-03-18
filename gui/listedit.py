import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from typing import List, Optional

class CSVEditor:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Electrical Lighting Material Catalog")
        
        # Data management
        self.data: List[List[str]] = []
        self.current_page: int = 0
        self.rows_per_page: int = 20
        self.total_pages: int = 0
        self.entries: List[List[ttk.Entry]] = []
        self.current_file: Optional[str] = None
        self.headers: List[str] = []
        self.unsaved_changes: bool = False
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self._create_menu()
        self._create_toolbar()
        self._create_status_bar()
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-n>', lambda e: self.new_file())
        
    def _create_menu(self):
        """Create menu bar with File and Edit options"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Row", command=self.add_row)
        edit_menu.add_command(label="Delete Row", command=self.delete_row)
        
    def _create_toolbar(self):
        """Create toolbar with navigation and page controls"""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Navigation buttons
        self.prev_button = ttk.Button(toolbar, text="◄ Previous", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = ttk.Button(toolbar, text="Next ►", command=self.next_page)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        # Page display
        self.page_label = ttk.Label(toolbar, text="")
        self.page_label.pack(side=tk.LEFT, padx=20)
        
        # Page size control
        ttk.Label(toolbar, text="Rows per page:").pack(side=tk.LEFT, padx=5)
        self.page_size_var = tk.StringVar(value=str(self.rows_per_page))
        page_size_combo = ttk.Combobox(toolbar, textvariable=self.page_size_var, 
                                      values=['10', '20', '50', '100'], width=5)
        page_size_combo.pack(side=tk.LEFT)
        page_size_combo.bind('<<ComboboxSelected>>', self._on_page_size_change)
        
    def _create_status_bar(self):
        """Create status bar for displaying information"""
        self.status_bar = ttk.Label(self.main_frame, text="Ready", anchor=tk.W)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
    def load_csv(self, file_path: str) -> None:
        """Load CSV file and display its contents"""
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                self.headers = next(reader)  # Read headers
                self.data = list(reader)
            
            self.current_file = file_path
            self.update_total_pages()
            self.show_page(0)
            self.status_bar.config(text=f"Loaded: {os.path.basename(file_path)}")
            self.unsaved_changes = False
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file:\n{str(e)}")
            
    def save_csv(self, file_path: str) -> None:
        """Save current data to CSV file"""
        try:
            self.update_data_from_entries()
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self.headers)
                writer.writerows(self.data)
            
            self.current_file = file_path
            self.status_bar.config(text=f"Saved: {os.path.basename(file_path)}")
            self.unsaved_changes = False
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV file:\n{str(e)}")
            
    def show_page(self, page: int) -> None:
        """Display the specified page of data"""
        if not 0 <= page < self.total_pages:
            return
            
        self.current_page = page
        self.clear_entries()
        
        # Create header row
        for j, header in enumerate(self.headers):
            label = ttk.Label(self.main_frame, text=header, font=('TkDefaultFont', 9, 'bold'))
            label.grid(row=1, column=j, padx=2, pady=2)
            
        # Create data rows
        start_idx = page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(self.data))
        
        self.entries = []
        for i, row in enumerate(self.data[start_idx:end_idx]):
            row_entries = []
            for j, value in enumerate(row):
                entry = ttk.Entry(self.main_frame)
                entry.grid(row=i + 2, column=j, padx=2, pady=2)
                entry.insert(0, value)
                entry.bind('<KeyRelease>', lambda e: self._mark_unsaved())
                row_entries.append(entry)
            self.entries.append(row_entries)
            
        self.update_navigation()
        
    def clear_entries(self) -> None:
        """Clear all entry widgets from the grid"""
        for widget in self.main_frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.grid_forget()
                
    def update_navigation(self) -> None:
        """Update navigation buttons and page display"""
        self.prev_button.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_page < self.total_pages - 1 else tk.DISABLED)
        self.page_label.config(text=f"Page {self.current_page + 1} of {self.total_pages}")
        
    def update_total_pages(self) -> None:
        """Update total number of pages based on data size and rows per page"""
        self.total_pages = (len(self.data) + self.rows_per_page - 1) // self.rows_per_page
        
    def update_data_from_entries(self) -> None:
        """Update data list with current entry values"""
        start_idx = self.current_page * self.rows_per_page
        for i, row in enumerate(self.entries):
            for j, entry in enumerate(row):
                self.data[start_idx + i][j] = entry.get()
                
    def _mark_unsaved(self) -> None:
        """Mark that there are unsaved changes"""
        if not self.unsaved_changes:
            self.unsaved_changes = True
            self.status_bar.config(text="Unsaved changes")
            
    def _on_page_size_change(self, event) -> None:
        """Handle change in rows per page"""
        try:
            new_size = int(self.page_size_var.get())
            self.rows_per_page = new_size
            self.update_total_pages()
            self.show_page(0)
        except ValueError:
            pass
            
    # File operations
    def new_file(self) -> None:
        """Create new empty CSV file"""
        if self.unsaved_changes and messagebox.askyesno("Unsaved Changes", 
            "There are unsaved changes. Do you want to save them first?"):
            self.save_file()
            
        self.data = []
        self.headers = ["Column 1"]  # Default header
        self.current_file = None
        self.unsaved_changes = False
        self.show_page(0)
        self.status_bar.config(text="New file created")
        
    def open_file(self) -> None:
        """Open file dialog to load CSV file"""
        if self.unsaved_changes and messagebox.askyesno("Unsaved Changes", 
            "There are unsaved changes. Do you want to save them first?"):
            self.save_file()
            
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            self.load_csv(file_path)
            
    def save_file(self) -> None:
        """Save current file"""
        if self.current_file:
            self.save_csv(self.current_file)
        else:
            self.save_file_as()
            
    def save_file_as(self) -> None:
        """Open file dialog to save CSV file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            self.save_csv(file_path)
            
    def quit_app(self) -> None:
        """Handle application quit"""
        if self.unsaved_changes:
            if messagebox.askyesno("Unsaved Changes", 
                "There are unsaved changes. Do you want to save them first?"):
                self.save_file()
        self.root.quit()
        
    # Edit operations
    def add_row(self) -> None:
        """Add new empty row to data"""
        self.data.append([''] * len(self.headers))
        self.update_total_pages()
        self.show_page(self.total_pages - 1)
        self._mark_unsaved()
        
    def delete_row(self) -> None:
        """Delete currently selected row"""
        # Implementation for row deletion could be added here
        pass
        
    def prev_page(self) -> None:
        """Show previous page"""
        if self.current_page > 0:
            self.update_data_from_entries()
            self.show_page(self.current_page - 1)
            
    def next_page(self) -> None:
        """Show next page"""
        if self.current_page < self.total_pages - 1:
            self.update_data_from_entries()
            self.show_page(self.current_page + 1)

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVEditor(root)
    root.mainloop()