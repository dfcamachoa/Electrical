# File: main.py

import os
import tkinter as tk
from mto_processor import MtoProcessor
from gui.gui_manager import GuiManager

def main():
    # Create the main window
    root = tk.Tk()
    
    # Initialize the MTO processor
    base_dir = os.path.dirname(os.path.abspath(__file__))
    processor = MtoProcessor(base_dir)
    
    # Initialize and run GUI
    gui = GuiManager(root, processor)
    gui.run()

if __name__ == "__main__":
    main()