from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os
import pandas as pd
from utils.processor import dataframes_to_xml 
from utils.processor import excel_to_xml 



# BEGIN OF global variables #############################################################################

app = FastAPI()

# Set up the template directory for HTML responses
templates = Jinja2Templates(directory="templates")

# Directory for uploaded files and generated XML files
UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# sheets in the visualization excel file - input framework 
# sheets_to_print = ["Nagłówek", "Podmiot", "Kontrahent", "ZOiS", "Dziennik", "ZapisKonto", "Crl", "RPD"] 
# sheets_to_print = ["test1", "tes2", "test3"]

# Serve static files (like CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# END OF global variables ###############################################################################










# BEGIN OF routes ######################################################################################

# Home route with drag-and-drop form
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Render the main HTML page with the drag-and-drop form for file uploads.

    Parameters:
        request (Request): The incoming HTTP request.

    Returns:
        HTMLResponse: The rendered HTML page.
    """
    return templates.TemplateResponse("index.html", {"request": request})

# File upload and processing route
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Handle the file upload, process the Excel file, and generate XML output.

    Parameters:
        file (UploadFile): The uploaded Excel file.

    Returns:
        JSONResponse: A JSON object containing:
            - processed_data: A dictionary with the string representation of each sheet.
            - xml_data: The XML representation of the processed sheets.
            - xml_filename: The name of the generated XML file.
    """
    # Ensure the uploaded file is an Excel file
    if not file.filename.endswith('.xlsx'):
        return JSONResponse(status_code=400, content={"error": "Unsupported file format"})

    # Save the uploaded file temporarily
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())

    # Process the Excel file and return its contents for the specified sheets
    processed_data, processed_data_dfs = process_excel(filepath, sheets_to_print)

    # Convert processed DataFrames to XML format
    xml_output = dataframes_to_xml(processed_data_dfs)

    # Save the XML output to a file
    xml_filename = f"{file.filename.replace('.xlsx', '.xml')}"
    xml_file_path = os.path.join(UPLOAD_FOLDER, xml_filename)
    with open(xml_file_path, "w") as xml_file:
        xml_file.write(xml_output)

    return {"processed_data": processed_data, "xml_data": xml_output, "xml_filename": xml_filename}

# Route to download the generated XML file
@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download the generated XML file.

    Parameters:
        filename (str): The name of the XML file to be downloaded.

    Returns:
        FileResponse: The XML file if it exists, or raises a 404 error if not found.
    """
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Use FileResponse to send the file with a content disposition to prompt download
    return FileResponse(file_path, media_type='application/xml', filename=filename)

# END OF routes ########################################################################################










# BEGIN OF functions ###################################################################################

# Function to process multiple sheets from an Excel file
def process_excel(filepath, sheets):
    """
    Process specified sheets from the given Excel file.

    Parameters:
        filepath (str): The path to the Excel file.
        sheets (list): A list of sheet names to process.

    Returns:
        tuple: A tuple containing:
            - processed_data (dict): A dictionary with the string representation of each sheet.
            - processed_data_dfs (list): A list of DataFrames corresponding to the processed sheets.
    """
    processed_data_xml = {} # this is for display on website it should show xml code
    # processed_data_dfs = [] # this is for generating xml should be passed to further processing
    
    # Load the Excel file
    excel_file = pd.ExcelFile(filepath)
    processed_data_xml = excel_to_xml(excel_file)


    # Iterate over the list of sheets to print
    # for sheet in sheets:
    #     if sheet in excel_file.sheet_names:  # Check if the sheet exists
    #         df = pd.read_excel(filepath, sheet_name=sheet)
    #         processed_data_xml[sheet] = df.to_string(index=False)  # Convert DataFrame to string
    #         processed_data_dfs.append(df)  # Append the DataFrame to the list
    #     else:
    #         processed_data_xml[sheet] = f"Sheet '{sheet}' not found."  # Handle missing sheets

    return processed_data_xml, processed_data_dfs  # Return processed data and DataFrames

# END OF functions ###################################################################################










# BEGIN OF entry point ##############################################################################

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI application on the specified host and port
    uvicorn.run(app, host="127.0.0.1", port=8000)

# END OF entry point ################################################################################