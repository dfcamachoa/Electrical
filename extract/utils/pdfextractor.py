
import pdfplumber
import pandas as pd
from tqdm import tqdm
import re
import logging

# Global list to store all assemblies
assemblies = []
material_catalog = []
material_by_assembly = []

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_table_name(headers):
    assemblies_table = []
    pattern = re.compile(r'^[A-Z]\d{2}')
    table_name = None
    for header in headers:
        if header:
            matches = re.findall(r'(\w+)\nQTY', header)
            if matches:
                assemblies_table.extend(matches)
    for assembly in assemblies_table:
        match = pattern.match(assembly)
        if match:
            radix = match.group(0)
            if table_name is None:
                table_name = radix
            else:
                # Find the common prefix between the current table_name and the new radix
                common_length = min(len(table_name), len(radix))
                for i in range(common_length):
                    if table_name[i] != radix[i]:
                        table_name = table_name[:i]
                        break
                else:
                    table_name = table_name[:common_length]
    return table_name, assemblies_table if assemblies_table else ["NoAssemblies"]

def remove_empty_columns(df):
    # Remove columns that contain only empty values or have the header "Unnamed"
    df = df.dropna(axis=1, how='all')
    df = df.loc[:, df.columns != "Unnamed"]
    return df

def clean_headers(headers):
    # Clean headers to remove extra characters after "BILL OF MATERIAL"
    cleaned_headers = []
    for header in headers:
        if header:
            if "BILL OF MATERIAL" in header:
                cleaned_header = re.sub(r'BILL OF MATERIAL.*', 'BILL OF MATERIAL', header)
            elif "ITEM COD" in header:
                cleaned_header = "TPENG ITEM CODE"
            else:
                cleaned_header = header
            cleaned_headers.append(cleaned_header)
        else:
            cleaned_headers.append(header)
    return cleaned_headers

def split_column(df, column_name):
    # Define the pattern for the TPENG ITEM CODE
    pattern = re.compile(r'\b\d{2}[A-Z]{4}\d{6}\b')
    
    # Check if the pattern is present in any of the column's text
    if df[column_name].apply(lambda x: bool(pattern.search(x))).any():
        # Create new columns for BILL OF MATERIAL and TPENG ITEM CODE
        df['NEW BILL OF MATERIAL'] = df[column_name].apply(lambda x: pattern.split(x)[0].strip() if pattern.search(x) else x)
        df['NEW TPENG ITEM CODE'] = df[column_name].apply(lambda x: pattern.search(x).group(0) if pattern.search(x) else "")
        
        # Drop the original column
        df = df.drop(columns=[column_name])
        
        # Rename the new columns to the original names
        df = df.rename(columns={
            'NEW BILL OF MATERIAL': 'BILL OF MATERIAL',
            'NEW TPENG ITEM CODE': 'TPENG ITEM CODE'
        })
    
    return df

def unpivot_table(df):
    # Local Assemblies - Code
    global material_by_assembly
    global material_catalog

    # Identify all columns that contain "QTY"
    qty_columns = [col for col in df.columns if "QTY" in col]
    
    # Initialize a list to store unpivoted DataFrames
    unpivoted_dfs = []
    
    for qty_column in qty_columns:
        # Identify columns to keep
        id_vars = ['UNIT','TPENG ITEM CODE', 'BILL OF MATERIAL']
        df_unpivoted = pd.melt(df, id_vars=id_vars, value_vars=[qty_column], var_name='ASSEMBLY', value_name='QUANTITY')
        df_unpivoted['ASSEMBLY'] = df_unpivoted['ASSEMBLY'].str.replace('QTY', '').str.strip()
        df_unpivoted = df_unpivoted[df_unpivoted['QUANTITY'] != '-']
        material_by_assembly.extend(df_unpivoted[['ASSEMBLY', 'TPENG ITEM CODE', 'QUANTITY', 'UNIT']].to_dict('records'))
        material_catalog.extend(df_unpivoted[['TPENG ITEM CODE', 'BILL OF MATERIAL', 'UNIT']].to_dict('records'))
        assemblies.extend(df_unpivoted['ASSEMBLY'].unique().tolist())
        unpivoted_dfs.append(df_unpivoted)
    
    # Concatenate all unpivoted DataFrames
    df_final = pd.concat(unpivoted_dfs, ignore_index=True)
    
    return df_final

def extract_tables_from_pdf(pdf_path):
    tables_by_page = {}
    table_settings = {
        "vertical_strategy": "lines_strict",
        "explicit_vertical_lines": [1185],
        "explicit_horizontal_lines": [20, 500],
        "intersection_y_tolerance": 6,
        "snap_tolerance": 2
    }
    
    fixed_columns = {"ITEM", "UNIT", "TPENG ITEM CODE"}
    variable_column_patterns = {"QTY", "BILL OF MATERIAL"}
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for page_num, page in enumerate(tqdm(pdf.pages, total=total_pages, desc="Processing pages")):
                headers = []
                table_name = ''
                assemblies_table = []
                table = page.extract_table(table_settings)
                
                if table:
                    filtered_table = [row for row in table if any(cell and cell.strip() for cell in row)]
                    
                    if not filtered_table:
                        logging.info(f"No valid rows found on page {page_num + 1}. Skipping table.")
                        continue
                    
                    headers = filtered_table[0]
                    if all(header is None or header.strip() == "" for header in headers):
                        logging.info(f"All headers are None or empty on page {page_num + 1}. Skipping table.")
                        continue
                    
                    table_name, assemblies_table = extract_table_name(headers)
                    logging.info(f"Assemblies found {assemblies_table}")
                    
                    headers = [header.replace('\n', ' ') if header else "Unnamed" for header in headers]
                    headers = clean_headers(headers)  # Clean the headers
                    logging.info(f"Table found on page {page_num + 1}: {headers}")
                    
                    if fixed_columns.issubset(headers) and any(pattern in header for header in headers for pattern in variable_column_patterns):
                        logging.info(f"Table on page {page_num + 1} contains required columns.")
                        if page_num + 1 not in tables_by_page:
                            tables_by_page[page_num + 1] = []
                        
                        filtered_table = [row for row in filtered_table[1:] if any(cell and cell.strip() for cell in row)]
                        df = pd.DataFrame(filtered_table, columns=headers)
                        df = remove_empty_columns(df)
                        
                        # Apply the split_column function to the relevant column
                        relevant_column = next((col for col in df.columns if re.search(r'BILL OF MATERIAL.*', col)), None)
                        if relevant_column:
                            df = split_column(df, relevant_column)
                        
                        # Unpivot the table by all columns that contain "QTY"
                        df_assembly_code = unpivot_table(df)

                        tables_by_page[page_num + 1].append((df, df_assembly_code, table_name))
                    else:
                        logging.info(f"Table on page {page_num + 1} does not contain required columns.")
        
        return tables_by_page, material_by_assembly, material_catalog, assemblies
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None