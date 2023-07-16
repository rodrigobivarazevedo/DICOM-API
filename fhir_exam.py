    """ 1 - Sure, I can help you create a web service using FastAPI 
    to display the overview of DICOM metadata and provide filtering based on patient ID. 
    Let's break it down into three parts as requested:
    """
    
# a) Create a Webservice to display all DICOM metadata as JSON:

from fastapi import FastAPI, HTTPException
from pydicom import dcmread
from os import listdir
from os.path import isfile, join
from datetime import datetime
from fastapi.responses import HTMLResponse


app = FastAPI()


def get_dcm_metadata(mypath):
    dcm_metadata = []
    for dcm_filename in [f for f in listdir(mypath) if isfile(join(mypath, f))]:
        dcm_metadata.append(dcmread(f"{mypath}/{dcm_filename}"))

    return dcm_metadata

@app.get("/json", response_model=list[dict])
def get_all_metadata():
    metadata = get_dcm_metadata("dicom")
    return metadata

get_dcm_metadata('dicom')
# or 

#from fastapi.responses import JSONResponse

#@app.get("/json")
#def get_all_metadata():
  #  metadata = get_dcm_metadata("dicom")
   # return JSONResponse(content=metadata)

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







    """2 - Not all of the radiologists are nerds. Can you provide an overview of all data also as actual HTML with images?

    """
    
# a) Create a route that outputs HTML and lists a grid of DICOM images, incl. annotations of Patient ID and Date (in human readable format) (15 Points)

def generate_html_grid(metadata):
    grid_html = "<html><body><h1>DICOM Image Overview</h1><div style='display: grid; grid-template-columns: repeat(3, 300px); grid-gap: 20px;'>"
    for dcm_file in metadata:
        date_str = datetime.strptime(dcm_file.StudyDate, "%Y%m%d").strftime("%B %d, %Y")
        grid_html += f"<div><img src='/images/{dcm_file.PatientID}.png' width='300'/><p>Patient ID: {dcm_file.PatientID}</p><p>Date: {date_str}</p></div>"
    grid_html += "</div></body></html>"
    return grid_html

@app.get("/", response_class=HTMLResponse)
def overview_html():
    metadata = get_dcm_metadata("dicom")
    return generate_html_grid(metadata)


# b) Create a filterable route that outputs HTML and shows all patient images:

@app.get("/patient/{patient_id}", response_class=HTMLResponse)
def patient_images_html(patient_id: str):
    metadata = get_dcm_metadata("dicom")
    filtered_metadata = [dcm_file for dcm_file in metadata if dcm_file.PatientID == patient_id]
    if not filtered_metadata:
        raise HTTPException(status_code=404, detail="Patient not found")
    return generate_html_grid(filtered_metadata)








    """3. After looking at all the images. The radiologist see something is wrong. 
    But they cannot say what. Somehow the image names and the metadata does not match - given their experience.
    """
    
    
# a) Cues to help solve the problem:

# Patient ID: The most crucial cue to match the image names with metadata is the Patient ID. Each DICOM image should have a Patient ID, which should also be a part of the image name.

# Study Date: The Study Date in the DICOM metadata could be compared with the date mentioned in the image names to identify potential mismatches.

# Modality: The Modality field in DICOM metadata can provide additional information to verify if the image is of the correct type (e.g., CT, MRI, X-ray).

# Study Description: The Study Description in DICOM metadata might give further context to help verify the image.

# Series Description: The Series Description in DICOM metadata could also aid in matching images with their metadata.   
    
    
    
    

    
# b) Image names that do not match their metadata:    
    
 # To find image names that do not match their metadata, we need to compare the Patient ID, Study Date, and other relevant fields in the image names with their corresponding fields in the DICOM metadata.   
    



   
from pydicom import dcmread
from os import listdir, rename
from os.path import isfile, join
from datetime import datetime

def find_mismatched_images(mypath):
    mismatched_images = []

    for image_filename in [f for f in listdir(mypath) if isfile(join(mypath, f))]:
        # Parse the Patient ID and Study Date from the image filename
        patient_id_from_name, study_date_from_name = parse_patient_id_and_study_date(image_filename)

        # Read the DICOM file to extract metadata
        dcm_file = dcmread(f"{mypath}/{image_filename}")
        patient_id_from_metadata = dcm_file.PatientID
        study_date_from_metadata = datetime.strptime(dcm_file.StudyDate, "%Y%m%d")

        # Compare Patient ID and Study Date from filename and metadata
        if (patient_id_from_name != patient_id_from_metadata) or (study_date_from_name != study_date_from_metadata):
            mismatched_images.append(image_filename)

    return mismatched_images

def parse_patient_id_and_study_date(image_filename):
    # Assuming the filename format is "PATIENTID_YYYYMMDD.png"
    filename_without_extension = image_filename.split(".")[0]
    parts = filename_without_extension.split("_")
    patient_id = parts[0]
    study_date = datetime.strptime(parts[1], "%Y%m%d").strftime("%Y%m%d")
    return patient_id, study_date




# c) Fixing the image names:

 # Once we have identified the mismatched images, we can proceed to rename them according to the correct Patient ID and Study Date obtained from the DICOM metadata. We should be cautious while renaming the images, and it's essential to take appropriate backup measures before making changes to the original images.   
    

def fix_image_names(mypath):
    mismatched_images = find_mismatched_images(mypath)

    for image_filename in mismatched_images:
        dcm_file = dcmread(f"{mypath}/{image_filename}")
        patient_id = dcm_file.PatientID
        study_date = datetime.strptime(dcm_file.StudyDate, "%Y%m%d").strftime("%Y%m%d")

        new_image_name = f"{patient_id}_{study_date}.png"
        new_image_path = f"{mypath}/{new_image_name}"

        try:
            # Rename the image file
            rename(f"{mypath}/{image_filename}", new_image_path)
            print(f"Renamed: {image_filename} -> {new_image_name}")
        except Exception as e:
            print(f"Error renaming {image_filename}: {e}")

    print("Mismatched images have been fixed.")

mypath = "dicom"
print("Mismatched images:")
mismatched_images = find_mismatched_images(mypath)
print(mismatched_images)

# Uncomment the following line to fix the mismatched image names
# fix_image_names(mypath)
   
    
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)