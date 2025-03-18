import os
import shutil
import csv
import logging

def ordercodes(list): 
    try:
        # Remove duplicates based on 'TPENG ITEM CODE' and 'BILL OF MATERIAL'
        seen = set()
        unique_codes = []
        for item in list:
            identifier = (item['TPENG ITEM CODE'], item['BILL OF MATERIAL'])
            if identifier not in seen:
                seen.add(identifier)
                unique_codes.append(item)
        
        # Sort the list by 'TPENG ITEM CODE'
        unique_codes.sort(key=lambda x: x['TPENG ITEM CODE'])
        return unique_codes 
    except Exception as e:
        logging.error(f"Failed to order list: {e}")

def clean_csv_folder(csv_folder_path):
    try:
        if os.path.exists(csv_folder_path):
            shutil.rmtree(csv_folder_path)
        os.makedirs(csv_folder_path)
        logging.info(f"Cleaned and recreated the folder: {csv_folder_path}")
    except Exception as e:
        logging.error(f"Failed clear csv directory {csv_folder_path}: {e}")

def save_csv(material_by_assembly, material_catalog, assemblies, csv_dir):
    if material_by_assembly:
        all_assembly_code_csv_file = f"{csv_dir}/material_by_assembly.csv"
        try:
            # Get the keys from the first dictionary as the header
            header = material_by_assembly[0].keys()

            # Write the list of dictionaries to a CSV file
            with open(all_assembly_code_csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=header)
                writer.writeheader()
                writer.writerows(material_by_assembly)

            logging.info(f"Data has been successfully saved to {all_assembly_code_csv_file}.")
        except Exception as e:
            logging.error(f"Failed to save Data to {all_assembly_code_csv_file}: {e}")

    if material_catalog:
        all_codes_csv_file = f"{csv_dir}/material_catalog.csv"
        try:
            # Remove duplicates based on 'TPENG ITEM CODE' and 'BILL OF MATERIAL'
            unique_codes = ordercodes(material_catalog)

            # Get the keys from the first dictionary as the header
            header = unique_codes[0].keys()

            # Write the list of dictionaries to a CSV file
            with open(all_codes_csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=header)
                writer.writeheader()
                writer.writerows(unique_codes)

            logging.info(f"Data has been successfully saved to {all_codes_csv_file}.")
        except Exception as e:
            logging.error(f"Failed to save Data to {all_codes_csv_file}: {e}")

    if assemblies:
        all_assemblies_csv_file = f"{csv_dir}/assemblies.csv"
        try:
            # Convert the list of assembly names to a list of dictionaries
            all_assemblies_dicts = [{'ASSEMBLY': assembly} for assembly in assemblies]
            # Get the keys from the first dictionary as the header
            header = all_assemblies_dicts[0].keys()

            # Write the list of dictionaries to a CSV file
            with open(all_assemblies_csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=header)
                writer.writeheader()
                writer.writerows(all_assemblies_dicts)

            logging.info(f"Data has been successfully saved to {all_assemblies_csv_file}.")
        except Exception as e:
            logging.error(f"Failed to save Data to {all_assemblies_csv_file}: {e}")