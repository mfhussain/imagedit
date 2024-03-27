# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 11:13:11 2024

@author: fhussain
"""

import streamlit as st
import cv2
import numpy as np
from tempfile import NamedTemporaryFile
import base64
import zipfile
import os
from PIL import Image

# Function to resize the image
def resize_image(image, scale_percent):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_LINEAR)
    return resized_image

# Function to adjust brightness and contrast
def adjust_brightness_contrast(image, brightness, contrast):
    adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
    return adjusted

# Function to crop the image
def crop_image(image, x, y, w, h):
    cropped_image = image[y:y+h, x:x+w]
    return cropped_image

# Main function
def main():
    st.title("Image Editor")

    uploaded_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    image_info = st.text_input("Image Information", "")

    if uploaded_image is not None:
        # OpenCV memory optimization for large files
        file_bytes = np.frombuffer(uploaded_image.read(), dtype=np.uint8)
        original_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        st.image(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB), caption="Original Image", use_column_width=True)

        # Image processing options
        st.sidebar.title("Image Processing Options")

        scale_percent = st.sidebar.slider("Scale Percent", 10, 200, 100, 10)
        brightness = st.sidebar.slider("Brightness", -100, 100, 0, 1)
        contrast = st.sidebar.slider("Contrast", 0.0, 2.0, 1.0, 0.1)

        # Crop parameters
        st.sidebar.subheader("Crop")
        x = st.sidebar.slider("X", 0, original_image.shape[1], 0, 1)
        y = st.sidebar.slider("Y", 0, original_image.shape[0], 0, 1)
        w = st.sidebar.slider("Width", 0, original_image.shape[1], original_image.shape[1], 1)
        h = st.sidebar.slider("Height", 0, original_image.shape[0], original_image.shape[0], 1)

        resized = resize_image(original_image, scale_percent)
        adjusted = adjust_brightness_contrast(resized, brightness, contrast)
        cropped = crop_image(adjusted, x, y, w, h)

        st.image(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB), caption="Processed Image", use_column_width=True)

        # Download button
        if st.button("Download Edited Image"):
            # Convert numpy array to PIL image
            pil_image = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))

            # Save PIL image to temporary file
            tmp_file = NamedTemporaryFile(delete=False, suffix=".png")
            pil_image.save(tmp_file.name, quality=95)  # Adjust quality as needed

            # Write image information to a text file
            info_file = NamedTemporaryFile(delete=False, suffix=".txt")
            with open(info_file.name, 'w') as f:
                f.write(image_info)

            # Create a zip file containing the image and its information text file
            tmp_zip = NamedTemporaryFile(delete=False, suffix=".zip")
            with zipfile.ZipFile(tmp_zip.name, 'w') as zipf:
                zipf.write(tmp_file.name, arcname="edited_image.png")
                zipf.write(info_file.name, arcname="image_info.txt")

            # Provide download link for the zip file
            st.markdown(get_binary_file_downloader_html(tmp_zip.name, 'Edited Image'), unsafe_allow_html=True)

def get_binary_file_downloader_html(bin_file_path, file_label='File'):
    with open(bin_file_path, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode('utf-8')
    href = f'<a href="data:file/zip;base64,{bin_str}" download="{os.path.basename(bin_file_path)}">{file_label}</a>'
    return href

if __name__ == "__main__":
    main()
