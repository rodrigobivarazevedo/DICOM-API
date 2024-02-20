
from os import listdir
import numpy as np
from PIL import Image
from pydicom import dcmread
import os
import matplotlib.pyplot as plt


def dicom_to_img_dir(mypath):
    
    # Remove all files from the images directory
    for file in os.listdir("images/"):
        os.remove(os.path.join("images", file))

    for filename in listdir(mypath):
            # Read the DICOM file
            
            ds = dcmread(mypath+filename)
            print(ds)
         
            # Extract the pixel data
            pixel_data = ds.pixel_array
            # Check if the pixel data is signed
            if ds.PixelRepresentation == 1:
                # Convert signed pixel data to unsigned
                pixel_data = pixel_data + abs(np.min(pixel_data))
                pixel_data = pixel_data.astype(np.uint8)
                

            # Check if the pixel data is using a non-standard photometric interpretation
            if ds.PhotometricInterpretation != "RGB":
                # Convert to grayscale
                pixel_data = pixel_data * int(ds.RescaleSlope) + int(ds.RescaleIntercept)
                pixel_data = pixel_data.astype(np.uint8)
                
            # Create a PIL Image object
            image = Image.fromarray(pixel_data)
            
            # Save the image as PNG format
            image.save(f"images/{ds.PatientID}.png")
            

dicom_to_img_dir("dicom/")

def dicom_to_png(dicom_file):
    # Read the DICOM file
    ds = dcmread(dicom_file)
    print('Modality:', ds.Modality)
    print('Patient ID:', ds.PatientID)
    print("Patient Age:", ds.PatientAge)
    print("Patient Sex:", ds.PatientSex)
    print("Study Date:", ds.StudyDate)
    print(ds.BitsAllocated)
    print(ds)
    # Define a dictionary to map BitsAllocated values to data types
    
    
    # Extract the pixel data
    pixel_data = ds.pixel_array
    # Check if the pixel data is signed
    if ds.PixelRepresentation == 1:
        # Convert signed pixel data to unsigned
        pixel_data = pixel_data + abs(np.min(pixel_data))
        pixel_data = pixel_data.astype(np.uint8)
        

    # Check if the pixel data is using a non-standard photometric interpretation
    if ds.PhotometricInterpretation != "RGB":
        # Convert to grayscale
        pixel_data = pixel_data * int(ds.RescaleSlope) + int(ds.RescaleIntercept)
        pixel_data = pixel_data.astype(np.uint8)
        
    # Create a PIL Image object
    image = Image.fromarray(pixel_data)

    # Save the image as PNG format
    image.save(f"images/{ds.PatientID}.png")

    
 


