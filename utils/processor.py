import pandas as pd
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from xml.dom import minidom



# BEGIN OF global variables #############################################################################

# sheets in the visualization excel file - input framework 
sheets_to_print = ["Nagłówek", "Podmiot", "Kontrahent", "ZOiS", "Dziennik", "ZapisKonto", "Crl", "RPD"] 

# END OF global variables ###############################################################################







# BEGIN OF utility functions ####################################################################

def sanitize_tag(tag):
    """Sanitize a string to be a valid XML tag name."""
    tag = str(tag)
    tag = tag.replace('-', '_')  # Replace hyphens with underscores
    tag = tag.replace(' ', '_')  # Replace spaces with underscores
    if tag[0].isdigit():  # Tag names can't start with a number
        tag = '_' + tag
    return tag


# END OF utility functions ####################################################################







def excel_to_xml(excel_file):
    




def extract_dfs_from_excel():






def dataframes_to_xml(dataframes, root_element_name="Data", sheet_element_name="test"):
    """
    Converts a list of dataframes into an XML string.
    
    :param dataframes: List of pandas dataframes (each representing a sheet)
    :param root_element_name: Name for the root XML element
    :param sheet_element_name: Name for the sheet XML elements
    :return: XML string
    """
    # Create the root XML element
    root = ET.Element(root_element_name)

    # Iterate through the dataframes, each corresponding to a sheet
    for idx, df in enumerate(dataframes):
        sheet_element = ET.SubElement(root, sheet_element_name, name=f"Sheet{idx + 1}")

        # Iterate through the rows of the dataframe
        for _, row in df.iterrows():
            row_element = ET.SubElement(sheet_element, "Row")

            # Iterate through each column in the row
            for col_name, value in row.items():
                # Ensure column names are valid XML tags
                sanitized_col_name = sanitize_tag(col_name)
                col_element = ET.SubElement(row_element, sanitized_col_name)

                # Set the text value of the column, handling NaN as empty string
                col_element.text = escape(str(value)) if pd.notnull(value) else ''

    # Convert the constructed tree to a string
    xml_str = ET.tostring(root, encoding='utf-8', method='xml').decode('utf-8')

    for df in dataframes:
        print(df)
    

    try:
        # Pretty-print the XML
        pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ")
    except Exception as e:
        print("Error parsing XML:", e)
        # print("XML String:", xml_str)
        raise

    # Print XML for debugging
    # print("Generated XML:", pretty_xml_str)

    return pretty_xml_str
