from fastapi import FastAPI
from os import listdir
from os.path import isfile, join
from fastapi.responses import JSONResponse
import numpy as np
from PIL import Image
from fastapi.staticfiles import StaticFiles
from pydicom import dcmread
from typing import List, Dict, Any
from fastapi.responses import HTMLResponse
from datetime import datetime
import os
from pydantic import BaseModel

app = FastAPI()
app.mount("/images", StaticFiles(directory="images"), name="images")

class PatientMetadata(BaseModel):
    PatientID: str
    Age: Any
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

def dicom_to_img(mypath):
    # Create a directory to store the images if it doesn't exista

    for filename in listdir(mypath):
            # Read the DICOM file
            ds = dcmread(mypath+filename)

            # Extract the pixel data
            pixel_data = ds.pixel_array

            # Check if the pixel data is signed
            if ds.PixelRepresentation == 1:
                # Convert signed pixel data to unsigned
                pixel_data = pixel_data + np.min(pixel_data)
                pixel_data = pixel_data.astype(np.uint16)

            # Check if the pixel data is using a non-standard photometric interpretation
            if ds.PhotometricInterpretation != "RGB":
                # Convert to grayscale
                pixel_data = pixel_data * int(ds.RescaleSlope) + int(ds.RescaleIntercept)
                pixel_data = pixel_data.astype(np.uint16)

            # Create a PIL Image object
            image = Image.fromarray(pixel_data)

            # Save the image as PNG format
            image.save(f"images/{ds.PatientID}.png")

dicom_to_img("dicom/")

# question 1- 

def get_dcm_files(mypath):
    dcm_files = []
    for dcm_filename in [f for f in listdir(mypath) if isfile(join(mypath, f))]:
        dcm_files.append(dcmread(f"{mypath}/{dcm_filename}"))
    return dcm_files

def format_date(date_str):
    if date_str:
        return datetime.strptime(date_str, '%Y%m%d').strftime('%B %d, %Y')
    return None

def generate_html_grid(dcm_files):
    grid_html = "<html><body><h1>DICOM Image Overview</h1><div style='display: grid; grid-template-columns: repeat(3, 300px); grid-gap: 20px;'>"
    for dcm_file in dcm_files:
        patient_id = dcm_file.get("PatientID")
        date_str = format_date(dcm_file.get("StudyDate"))
        
        if patient_id or date_str:
            grid_html += f"<div><img src='/images/{patient_id}.png' width='300'/><p>Patient ID: {patient_id}</p><p>Date: {date_str}</p></div>"
    grid_html += "</div></body></html>"
    return grid_html



@app.get("/", response_class=HTMLResponse)
def overview_html():
    dcm_files = get_dcm_files("dicom/")
    return generate_html_grid(dcm_files)

@app.get("/patient/{patient_id}", response_class=HTMLResponse)
def patient_images_html(patient_id: str):
    dcm_files = get_dcm_files("dicom/")
    
    filtered_metadata = [dcm_obj for dcm_obj in  dcm_files if dcm_obj.get("PatientID") == patient_id]
    if not filtered_metadata:
        raise HTTPException(status_code=404, detail="Patient not found")
    return generate_html_grid(filtered_metadata)


# question 2- 

@app.get("/api", response_model=list[dict])
def get_all_metadata():
    dcm_files = get_dcm_files("dicom/")
    
    metadata = []
    for file in dcm_files:
        metadata.append(file.to_json())
    
    return JSONResponse(content=metadata)


@app.get("/api/patient/{patient_id}", response_class=JSONResponse)
def get_patient_metadata(patient_id: str):
    dcm_files = get_dcm_files("dicom/")

    filtered_metadata = [dcm_obj for dcm_obj in dcm_files if dcm_obj.get("PatientID") == patient_id]
    metadata_list = []
    for dcm_obj in filtered_metadata:
        metadata = PatientMetadata(
            PatientID=dcm_obj.get("PatientID"),
            Age=dcm_obj.get("Age"),
            StudyDate = format_date(dcm_obj.get("StudyDate"))
        )
        metadata_list.append(metadata)
    return metadata
    
    


 

# b) If you had to make it interoperable, how would you go about it? Which tools and which FHIR resources would you use? (10 points)
# To make the /api route interoperable and comply with the FHIR standard, we can use FHIR resources python library and the appropriate FHIR server or FHIR client tools.

from fhir.resources.imagingstudy import ImagingStudy
from fhir.resources.reference import Reference
from fhir.resources.meta import Meta


@app.get("/apifhir", response_model=list[ImagingStudy])
def get_all_metadata():
    dcm_files = get_dcm_files("dicom/")

    metadata = []
    for file in dcm_files:
        imaging_study = ImagingStudy(
            status="preliminary",  # Provide a valid status value
            id=file.SOPInstanceUID,
            patient=Reference(reference=f"Patient/{file.PatientID}"),
            started=format_date(file.StudyDate),
            meta=Meta(versionId=str(file.InstanceNumber))
        )
        metadata.append(imaging_study)

    return metadata


# question 3 - 

# a) Which cues can you find in both image names and metadata to help solve this problem? (5 points)


# Patient ID: The most crucial cue to match the image names with metadata is the Patient ID. Each DICOM image should have a Patient ID, which should also be a part of the image name.

# Study Date: The Study Date in the DICOM metadata could be compared with the date mentioned in the image names to identify potential mismatches.


def check_image_name_mismatches(dcm_files, image_folder):
    mismatches = []
    for file in dcm_files:
        patient_id = file.get("PatientID")
        if not patient_id:
            continue

        image_name = f"{patient_id}.png"
        image_path = join(image_folder, image_name)
        if not isfile(image_path):
            mismatches.append((file.SOPInstanceUID, patient_id, image_name))

    return mismatches

def fix_image_names(mismatches, image_folder):
    for uid, patient_id, image_name in mismatches:
        old_path = join(image_folder, image_name)
        new_name = f"{patient_id}.png"
        new_path = join(image_folder, new_name)
        os.rename(old_path, new_path)

#'dicom/' folder with DICOM files and 'images/' folder for the images.
dcm_files = get_dcm_files("dicom/")
image_folder = "images/"
mismatches = check_image_name_mismatches(dcm_files, image_folder)
if mismatches:
    fix_image_names(mismatches, image_folder)
