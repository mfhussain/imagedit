import streamlit as st
import cv2
import numpy as np
import zipfile
import os
from PIL import Image
import io

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

# Function to process uploaded file
def process_uploaded_file(uploaded_file):
    # OpenCV memory optimization for large files
    file_bytes = np.frombuffer(uploaded_file.read(), dtype=np.uint8)
    original_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    return original_image

# Function to download edited image
def download_edited_image(cropped, image_info):
    # Convert numpy array to PIL image
    pil_image = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))

    # Save PIL image to byte buffer
    byte_buffer = io.BytesIO()
    pil_image.save(byte_buffer, format='PNG')
    byte_buffer.seek(0)

    # Write image information to a text file
    info_file_content = image_info.encode()

    return byte_buffer, info_file_content

# Main function
def main():
    st.title("Image Editor")

    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="uploaded_file")

    image_info = st.text_input("Image Information", "")

    if uploaded_file is not None:
        original_image = process_uploaded_file(uploaded_file)
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
            byte_buffer, info_file_content = download_edited_image(cropped, image_info)
            st.download_button(
                label="Click here to download",
                data=byte_buffer,
                file_name="edited_image.zip",
                mime="application/zip",
                key="download_button"
            )

if __name__ == "__main__":
    main()
