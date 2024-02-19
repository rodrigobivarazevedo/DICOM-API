
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
            print(mypath+filename)

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
            image.save(f"images2/{ds.PatientID}.png")



#dicom_to_img_dir("dicoms/")



def dicom_to_png(dicom_file):
    # Read the DICOM file
    ds = dcmread(dicom_file)
    print('Modality:', ds.Modality)
    print('Patient ID:', ds.PatientID)
    print("Patient Age:", ds.PatientAge)
    print("Patient Sex:", ds.PatientSex)
    print("Study Date:", ds.StudyDate)
    print(ds.BitsAllocated)
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
    #image.save(f"images/{ds.PatientID}.png")
    image.save(f"images/1.png")
    
 

# Example usage:
#dicom_file = "dicoms/N2D_0003.dcm"  # Path to your DICOM file
dicom_file = "dicom/ID_0010_AGE_0060_CONTRAST_1_CT (1).dcm"
dicom_to_png(dicom_file)

    


def process_dicom(dicom_file):
    # Read the DICOM file
    ds = dcmread(dicom_file)
    
    # Extract relevant attributes
    samples_per_pixel = ds.SamplesPerPixel
    photometric_interp = ds.PhotometricInterpretation
    rows = ds.Rows
    columns = ds.Columns
    pixel_spacing = ds.PixelSpacing
    bits_allocated = ds.BitsAllocated
    bits_stored = ds.BitsStored
    high_bit = ds.HighBit
    pixel_representation = ds.PixelRepresentation
    rescale_slope = float(ds.RescaleSlope)
    rescale_intercept = float(ds.RescaleIntercept)
    
    # Determine the processing based on extracted attributes
    if samples_per_pixel == 1 and photometric_interp == "MONOCHROME2":
        # Grayscale image processing
        if bits_allocated == 16 and bits_stored == 16 and pixel_representation == 0:
            # Processing for 16-bit unsigned grayscale image
            pixel_data = ds.pixel_array.astype(np.uint16)
            pixel_data = pixel_data * rescale_slope + rescale_intercept
            # Further processing specific to 16-bit unsigned grayscale images
            # Example: Apply a filter to enhance edges
            # Add your code here
            from skimage.filters import sobel
            enhanced_image = sobel(pixel_data)
            # Example: Save the enhanced image
            enhanced_image_path = "enhanced_image.png"
            Image.fromarray(enhanced_image).save(enhanced_image_path)
            print(f"Enhanced image saved: {enhanced_image_path}")

        elif bits_allocated == 16 and bits_stored == 16 and pixel_representation == 1:
            # Processing for 16-bit signed grayscale image
            pixel_data = ds.pixel_array.astype(np.int16)
            pixel_data = pixel_data * rescale_slope + rescale_intercept
            # Further processing specific to 16-bit signed grayscale images
            # Example: Apply thresholding to highlight certain features
            threshold_value = 1000
            binary_image = (pixel_data > threshold_value).astype(np.uint8) * 255
            # Example: Save the binary image
            binary_image_path = "binary_image.png"
            Image.fromarray(binary_image).save(binary_image_path)
            print(f"Binary image saved: {binary_image_path}")
        else:
            # Unsupported bit depth or pixel representation
            print("Unsupported bit depth or pixel representation for grayscale image.")
    else:
        # Unsupported image type
        print("Unsupported image type.")

# Example usage:
dicom_file = "dicoms/N2D_0003.dcm"  # Path to your DICOM file

#process_dicom(dicom_file)