import streamlit as st
import pathlib
from PIL import Image
import google.generativeai as genai

# Configure the API key directly in the script
API_KEY = 'AIzaSyDvln1q95RRWxaER0fSMlqoaWsA1UU6lvs'
genai.configure(api_key=API_KEY)

# Model configuration
MODEL_NAME = "gemini-2.0-flash-exp"
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ],
    generation_config={
        "temperature": 0.8,
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 4096,
    },
)

# Streamlit app
st.set_page_config(page_title="Modern UI to Code Tool", layout="centered")
st.title("Modern UI to Code Tool")
st.markdown("An intuitive tool to transform UI images into clean, responsive code using advanced AI.")

# Framework selection
frameworks = ["Tailwind CSS", "Bootstrap", "Materialize"]
selected_framework = st.radio("Select your preferred CSS framework:", frameworks, horizontal=True)

# Image upload
uploaded_file = st.file_uploader("Upload an image of your UI design (JPG, JPEG, PNG):", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        # Load and display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded UI Design", use_column_width=True)

        # Convert to RGB if necessary
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Save the image temporarily
        temp_image_path = pathlib.Path("temp_image.jpg")
        image.save(temp_image_path, format="JPEG")

        # Generate refined description and HTML code
        if st.button("Generate Responsive Code"):
            st.info("Processing your UI design...")

            prompt = "Generate a detailed description of this UI design, focusing on its structure, colors, and layout."
            description = model.start_chat(history=[]).send_message(prompt).text

            html_prompt = (
                f"Generate a fully responsive HTML code styled with {selected_framework}. The design should match this description: {description}. "
                "Ensure the code is optimized for both desktop and mobile views."
            )
            html_code = model.start_chat(history=[]).send_message(html_prompt).text

            # Display and save the code
            st.code(html_code, language="html")

            with open("output.html", "w") as f:
                f.write(html_code)

            st.download_button(
                label="Download HTML File", data=html_code, file_name="output.html", mime="text/html"
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")
