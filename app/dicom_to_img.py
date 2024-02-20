
from os import listdir
import numpy as np
from PIL import Image
from pydicom import dcmread
import os
import matplotlib.pyplot as plt


def dicom_to_img_dir(mypath):
    
    for filename in listdir(mypath):
            # Read the DICOM file
            
            ds = dcmread(mypath+filename)
         
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
