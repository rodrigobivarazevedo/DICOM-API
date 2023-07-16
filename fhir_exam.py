    """Sure, I can help you create a web service using FastAPI 
    to display the overview of DICOM metadata and provide filtering based on patient ID. 
    Let's break it down into three parts as requested:
    """
    
# a) Create a Webservice to display all DICOM metadata as JSON:

from fastapi import FastAPI, HTTPException
from pydicom import dcmread
from os import listdir
from os.path import isfile, join

app = FastAPI()

def get_dcm_metadata(mypath):
    dcm_metadata = []
    for dcm_filename in [f for f in listdir(mypath) if isfile(join(mypath, f))]:
        dcm_file = dcmread(f"{mypath}/{dcm_filename}")
        dcm_metadata.append(dcm_file)

    return dcm_metadata

@app.get("/json", response_model=list[dict])
def get_all_metadata():
    metadata = get_dcm_metadata("dicom")
    return metadata



# b) Create a route (/json) and add a link to the actual image on disk to the metadata:


@app.get("/json", response_model=list[dict])
def get_all_metadata_with_image_links():
    metadata = get_dcm_metadata("dicom")
    for dcm_file in metadata:
        dcm_file["image_link"] = f"/images/{dcm_file.PatientID}.png"
    return metadata



# c) Create a route (/json/patient/<patient_id>) that filters images based on a patient's id:


@app.get("/json/patient/{patient_id}", response_model=list[dict])
def get_patient_metadata(patient_id: str):
    metadata = get_dcm_metadata("dicom")
    filtered_metadata = [dcm_file for dcm_file in metadata if dcm_file.PatientID == patient_id]
    if not filtered_metadata:
        raise HTTPException(status_code=404, detail="Patient not found")
    for dcm_file in filtered_metadata:
        dcm_file["image_link"] = f"/images/{dcm_file.PatientID}.png"
    return filtered_metadata



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
