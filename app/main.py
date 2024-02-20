from fastapi import FastAPI, Request
from os import listdir
from os.path import isfile, join
from fastapi.responses import JSONResponse
import numpy as np
from PIL import Image
from fastapi.staticfiles import StaticFiles
from pydicom import dcmread
from typing import  Any, List
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
from datetime import datetime
from pydantic import BaseModel
from fhir.resources.imagingstudy import ImagingStudy
from fhir.resources.reference import Reference
from fhir.resources.meta import Meta
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/images", StaticFiles(directory="images"), name="images")
templates = Jinja2Templates(directory="templates")

class PatientMetadata(BaseModel):
    PatientID: str
    Age: int
    Sex: str
    StudyDate: str

class Reference(BaseModel):
    reference: str

class Meta(BaseModel):
    versionId: str

class ImagingStudy(BaseModel):
    id: str
    patient: Reference
    started: str
    meta: Meta


# Function to get DICOM files from a directory
def get_dcm_files(mypath):
    dcm_files = []
    for dcm_filename in [f for f in listdir(mypath) if isfile(join(mypath, f))]:
        dcm_files.append(dcmread(f"{mypath}/{dcm_filename}"))
    return dcm_files

# Function to format date in the desired format
def format_date(date_str):
    if date_str:
        return datetime.strptime(date_str, '%Y%m%d').strftime('%B %d, %Y')
    return None

# Function to generate HTML grid with DICOM image metadata
def generate_html_grid(dcm_files):
    grid_html = "<html><body><h3>DICOM Image Overview</h3><div style='display: grid; grid-template-columns: repeat(3, 300px); grid-gap: 20px;'>"
    for dcm_file in dcm_files:
        patient_id = dcm_file.get("PatientID")
        date_str = format_date(dcm_file.get("StudyDate"))
        
        if patient_id or date_str:
            grid_html += f"<div><img src='/images/{patient_id}.png' width='300'/><p>Patient ID: {patient_id}</p><p>Date: {date_str}</p></div>"
    grid_html += "</div></body></html>"
    return grid_html



@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Route to display HTML overview of all DICOM images
@app.get("/overview", response_class=HTMLResponse)
def overview_html():
    dcm_files = get_dcm_files("dicom/")
    return generate_html_grid(dcm_files)

# Route to display HTML overview of DICOM images filtered by patient ID
@app.get("/patient/{patient_id}", response_class=HTMLResponse)
def patient_images_html(patient_id: str):
    dcm_files = get_dcm_files("dicom/")
    
    filtered_metadata = [dcm_obj for dcm_obj in dcm_files if dcm_obj.get("PatientID") == patient_id]
    if not filtered_metadata:
        raise HTTPException(status_code=404, detail="Patient not found")
    return generate_html_grid(filtered_metadata)

# Route to get all DICOM metadata in JSON format
@app.get("/api", response_class=JSONResponse)
def get_all_metadata():
    dcm_files = get_dcm_files("dicom/")
    
    metadata_list = []
    for dcm_obj in dcm_files:
        metadata = PatientMetadata(
            PatientID=dcm_obj.get("PatientID"),
            Age=int((dcm_obj.get("PatientAge")).rstrip('Y')),
            Sex=dcm_obj.get("PatientSex"),
            StudyDate=format_date(dcm_obj.get("StudyDate"))
        )
        metadata_list.append(metadata)
    if not metadata_list:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return metadata_list


# Route to get metadata of a patient in JSON format
@app.get("/api/patient/{patient_id}", response_class=JSONResponse)
def get_patient_metadata(patient_id: str):
    dcm_files = get_dcm_files("dicom/")

    filtered_metadata = [dcm_obj for dcm_obj in dcm_files if dcm_obj.get("PatientID") == patient_id]
    metadata_list = []
    for dcm_obj in filtered_metadata:
        metadata = PatientMetadata(
            PatientID=dcm_obj.get("PatientID"),
            Age=int((dcm_obj.get("PatientAge")).rstrip('Y')),
            Sex=dcm_obj.get("PatientSex"),
            StudyDate=format_date(dcm_obj.get("StudyDate"))
        )
        metadata_list.append(metadata)
    if not metadata_list:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return metadata_list


# Route to get DICOM metadata in FHIR format
@app.get("/apifhir", response_model=list[ImagingStudy])
def get_all_metadata():
    dcm_files = get_dcm_files("dicom/")

    metadata = []
    for file in dcm_files:
        imaging_study = ImagingStudy(
            status="preliminary",  
            id=file.SOPInstanceUID,
            patient=Reference(reference=f"Patient/{file.PatientID}"),
            started=format_date(file.StudyDate),
            meta=Meta(versionId=str(file.InstanceNumber))
        )
        metadata.append(imaging_study)

    return metadata


