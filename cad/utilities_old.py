import os
from pyautocad import Autocad

def run_lisp_on_all_files(directory, output_file):
    acad = Autocad(create_if_not_exists=True)
    lisp_file_path = "C:/Users/dcamachoav/Documents/Python/Electrical/cad/listblocks.lsp"

    # Check if the LISP file exists
    if not os.path.isfile(lisp_file_path):
        print(f"Error: LISP file not found at {lisp_file_path}")
        return

    # Initialize a list to store the output
    output_list = []

    for filename in os.listdir(directory):
        if filename.endswith(".dwg"):
            full_path = os.path.join(directory, filename)
            if not os.path.isfile(full_path):
                print(f"Error: DWG file not found at {full_path}")
                continue

            # Open the DWG file in BricsCAD
            acad.doc.SendCommand('(vla-Open (vla-get-Documents (vlax-get-acad-object)) "' + full_path.replace("\\", "/") + '")\n')
            acad.doc.SendCommand('(load "' + lisp_file_path.replace("\\", "/") + '")\n')
            acad.doc.SendCommand('ListBlocks\n')

            # Read the temporary output file and append its content to the list
            temp_output_file = "C:/Users/dcamachoav/Documents/Python/Electrical/cad/temp_output.txt"
            if os.path.isfile(temp_output_file):
                with open(temp_output_file, 'r') as temp_file:
                    output_list.extend(temp_file.readlines())
            else:
                print(f"Warning: Temporary output file not found at {temp_output_file}")

            # Close the DWG file
            acad.doc.SendCommand('(vla-Close (vla-get-ActiveDocument (vlax-get-acad-object)))\n')

    # Write the collected output to the final output file
    with open(output_file, 'w') as outfile:
        outfile.writelines(output_list)

def get_blocks_by_layer():
    directory = "C:/Users/dcamachoav/Documents/Python/Electrical/cad"  # Change this to your directory
    output_file = "C:/Users/dcamachoav/Documents/Python/Electrical/cad/final_output.txt"
    run_lisp_on_all_files(directory, output_file)
    return