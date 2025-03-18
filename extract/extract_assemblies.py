from extract.utils import pdfextractor as pdfextractor
from extract.utils import utils as utils

def extract_info():
    # Global list to store all assemblies
    assemblies = []
    material_catalog = []
    material_by_assembly = []

    pdf_file_path = "./pdf/ELECTRICAL_LIGHT_INSTALL_DETAILS.pdf"
    csv_dir = "./csv"
    utils.clean_csv_folder(csv_dir)
    tables_by_page, material_by_assembly, material_catalog, assemblies = pdfextractor.extract_tables_from_pdf(pdf_file_path)
    utils.save_csv(material_by_assembly, material_catalog, assemblies, csv_dir)
    return
