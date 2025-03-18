# File: mto_processor.py

import os
import csv
import pandas as pd
from cad.block_extractor import AutoCADBlockExtractor
import extract.extract_assemblies as extractor

class MtoProcessor:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.dwg_dir = os.path.join(base_dir, "dwg")
        self.csv_dir = os.path.join(base_dir, "csv")
        self.blocks_output = os.path.join(self.csv_dir, "blocks_output.csv")
        self.assemblies_output = os.path.join(self.csv_dir, "assemblies_by_file.csv")
        self.materials_reference = os.path.join(self.csv_dir, "material_by_assembly.csv")
        self.summed_materials = os.path.join(self.csv_dir, "summed_materials.csv")
        
        # Ensure directories exist
        os.makedirs(self.csv_dir, exist_ok=True)

    def execute_extract(self):
        """Execute the extract module for electrical lighting assemblies"""
        try:
            extractor.extract_info()
            return True, "Extract completed successfully"
        except Exception as e:
            return False, f"Extract failed: {str(e)}"

    def execute_cad(self):
        """Execute CAD block extraction"""
        try:
            extractor = AutoCADBlockExtractor(self.base_dir, self.dwg_dir)
            success = extractor.run_extraction(self.blocks_output)
            
            if success:
                return True, f"Block extraction completed. Output saved to: {self.blocks_output}"
            else:
                return False, "Block extraction failed - check logs for details"
        except Exception as e:
            return False, f"CAD execution failed: {str(e)}"

    def filter_blocks(self):
        """Filter blocks to get assemblies from E-LIGHTING layer"""
        try:
            with open(self.blocks_output, mode='r', newline='') as infile, \
                 open(self.assemblies_output, mode='w', newline='') as outfile:
                
                reader = csv.DictReader(infile)
                fieldnames = [name if name != 'block' else 'ASSEMBLY' for name in reader.fieldnames]
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for row in reader:
                    if row['layer'] == 'E-LIGHTING':
                        row['ASSEMBLY'] = row.pop('block')
                        writer.writerow(row)
                        
            return True, f"Filtered data saved to {self.assemblies_output}"
        except FileNotFoundError:
            return False, f"File {self.blocks_output} not found"
        except Exception as e:
            return False, f"Filter operation failed: {str(e)}"

    def group_materials(self):
        """Group materials by file using reference data with proper quantity handling"""
        try:
            # Read the input files
            assemblies_df = pd.read_csv(self.assemblies_output)
            materials_df = pd.read_csv(self.materials_reference)
            
            # Ensure QUANTITY is numeric in materials_df
            materials_df['QUANTITY'] = pd.to_numeric(materials_df['QUANTITY'], errors='coerce')
            
            # Merge assemblies with materials
            merged_df = pd.merge(
                assemblies_df,
                materials_df,
                on='ASSEMBLY',
                how='left'
            )
            
            # Count occurrences of each assembly in each file
            assembly_counts = merged_df.groupby(['filename', 'ASSEMBLY']).size().reset_index(name='COUNT')
            
            # Merge the counts back
            merged_df = pd.merge(
                merged_df,
                assembly_counts,
                on=['filename', 'ASSEMBLY'],
                how='left'
            )
            
            # Calculate final quantity (material quantity * assembly count)
            merged_df['FINAL_QUANTITY'] = merged_df['QUANTITY'] * merged_df['COUNT']
            
            # Group by filename and material code, sum the quantities
            summed_materials = merged_df.groupby(
                ['filename', 'TPENG ITEM CODE']
            )['FINAL_QUANTITY'].sum().reset_index()
            
            # Rename FINAL_QUANTITY back to QUANTITY
            summed_materials = summed_materials.rename(columns={'FINAL_QUANTITY': 'QUANTITY'})
            
            # Sort by filename and material code
            summed_materials = summed_materials.sort_values(['filename', 'TPENG ITEM CODE'])
            
            # Convert quantities to integers if they're whole numbers
            summed_materials['QUANTITY'] = summed_materials['QUANTITY'].apply(
                lambda x: int(x) if x == int(x) else x
            )
            
            # Save to output file
            summed_materials.to_csv(self.summed_materials, index=False)
            
            return True, f"Successfully created summed materials file: {self.summed_materials}"
        except Exception as e:
            return False, f"Materials grouping failed: {str(e)}"

    def execute_mto(self):
        """Execute complete MTO process"""
        try:
            # Filter blocks
            success, message = self.filter_blocks()
            if not success:
                return False, message
                
            # Group materials
            success, message = self.group_materials()
            if not success:
                return False, message
                
            return True, "MTO process completed successfully"
        except Exception as e:
            return False, f"MTO execution failed: {str(e)}"