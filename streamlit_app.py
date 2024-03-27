import streamlit as st
import cv2
import numpy as np
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

    # Save PIL image to temporary file
    tmp_file = "edited_image.png"
    pil_image.save(tmp_file, quality=95)  # Adjust quality as needed

    # Write image information to a text file
    info_file_name = "image_info.txt"
    with open(info_file_name, 'w') as f:
        f.write(image_info)

    # Create a zip file containing the image and its information text file
    zip_file_name = "edited_image.zip"
    with zipfile.ZipFile(zip_file_name, 'w') as zipf:
        zipf.write(tmp_file, arcname="edited_image.png")
        zipf.write(info_file_name, arcname="image_info.txt")

    return zip_file_name

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
            zip_file_name = download_edited_image(cropped, image_info)
            with open(zip_file_name, 'rb') as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                href = f'<a href="data:file/zip;base64,{b64}" download="{os.path.basename(zip_file_name)}">Click here to download</a>'
                st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
