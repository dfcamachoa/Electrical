import os
from pyautocad import Autocad
from typing import List, Optional, Dict
import logging
import csv

class AutoCADBlockExtractor:
    def __init__(self, base_directory: str, dwg_directory: str):
        """
        Initialize the AutoCAD Block Extractor.
        
        Args:
            base_directory (str): Base directory for operations
            dwg_directory (str): Directory containing DWG files
        """
        self.base_directory = base_directory
        self.dwg_directory = dwg_directory
        self.cad_directory = os.path.join(base_directory, "cad")
        self.csv_directory = os.path.join(base_directory, "csv")
        self.lisp_file_path = os.path.join(self.cad_directory, "listblocks.lsp")
        self.temp_output_path = os.path.join(self.cad_directory, "temp_output.txt")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Ensure directories exist
        os.makedirs(self.csv_directory, exist_ok=True)

    def validate_paths(self) -> bool:
        """
        Validate that all required paths exist.
        
        Returns:
            bool: True if all paths are valid, False otherwise
        """
        if not os.path.exists(self.dwg_directory):
            self.logger.error(f"DWG directory not found: {self.dwg_directory}")
            return False
        
        if not os.path.isfile(self.lisp_file_path):
            self.logger.error(f"LISP file not found: {self.lisp_file_path}")
            return False
            
        return True

    def process_dwg_file(self, acad: Autocad, file_path: str) -> Optional[List[Dict[str, str]]]:
        """
        Process a single DWG file and extract block information.
        
        Args:
            acad: AutoCAD application instance
            file_path: Path to the DWG file
            
        Returns:
            Optional[List[Dict[str, str]]]: List of dictionaries containing filename, layer, and block info
        """
        try:
            # Normalize paths and escape properly for LISP
            normalized_dwg_path = file_path.replace("\\", "/")
            normalized_lisp_path = self.lisp_file_path.replace("\\", "/")
            filename = os.path.basename(file_path)
            
            # Execute AutoCAD commands
            commands = [
                f'(vla-Open (vla-get-Documents (vlax-get-acad-object)) "{normalized_dwg_path}")',
                f'(load "{normalized_lisp_path}")',
                'ListBlocks'
            ]
            
            for cmd in commands:
                self.logger.debug(f"Executing command: {cmd}")
                acad.doc.SendCommand(f'{cmd}\n')
                
            # Read and process temporary output
            if os.path.isfile(self.temp_output_path):
                block_data = []
                with open(self.temp_output_path, 'r') as temp_file:
                    for line in temp_file:
                        parts = line.strip().split(';')
                        if len(parts) >= 3:
                            block_info = {
                                'filename': filename,
                                'layer': parts[1].strip(),
                                'block': parts[2].strip()
                            }
                            block_data.append(block_info)
                return block_data
            else:
                self.logger.warning(f"No output generated for {file_path}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {str(e)}")
            return None
        finally:
            try:
                acad.doc.SendCommand(
                    '(vla-Close (vla-get-ActiveDocument (vlax-get-acad-object)))\n'
                )
            except Exception as e:
                self.logger.error(f"Error closing document: {str(e)}")

    def write_csv(self, data: List[Dict[str, str]], output_file: str) -> bool:
        """
        Write the extracted data to a CSV file.
        """
        try:
            with open(output_file, 'w', newline='') as csvfile:
                fieldnames = ['filename', 'layer', 'block']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
            return True
        except Exception as e:
            self.logger.error(f"Error writing CSV file: {str(e)}")
            return False

    def run_extraction(self, output_file: str) -> bool:
        """
        Run block extraction on all DWG files in the directory.
        """
        if not self.validate_paths():
            return False

        try:
            acad = Autocad(create_if_not_exists=True)
        except Exception as e:
            self.logger.error(f"Failed to initialize AutoCAD: {str(e)}")
            return False

        all_block_data = []
        dwg_files = [f for f in os.listdir(self.dwg_directory) if f.endswith(".dwg")]
        
        if not dwg_files:
            self.logger.warning(f"No DWG files found in directory: {self.dwg_directory}")
            return False

        for filename in dwg_files:
            full_path = os.path.join(self.dwg_directory, filename)
            self.logger.info(f"Processing {filename}")
            
            result = self.process_dwg_file(acad, full_path)
            if result:
                all_block_data.extend(result)

        if all_block_data:
            success = self.write_csv(all_block_data, output_file)
            if success:
                self.logger.info(f"Results written to {output_file}")
                return True
        
        return False