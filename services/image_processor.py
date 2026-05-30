# services/image_processor.py
import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
import io

def image_processor():
    """App 3: Image Processor - upload, adjust brightness, grayscale, etc."""
    st.markdown("<h2 style='text-align: center;'>🖼️ Image Processor</h2>", unsafe_allow_html=True)
    uploaded_img = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    
    if uploaded_img is not None:
        try:
            original = Image.open(uploaded_img)
            st.image(original, caption="Original Image", use_container_width=True)
            
            operation = st.selectbox("Choose operation", ["Grayscale", "Brightness Adjustment", "Horizontal Flip", "Rotate 90°"])
            
            processed = original.copy()
            if operation == "Grayscale":
                processed = ImageOps.grayscale(original)
                st.image(processed, caption="Grayscale", use_container_width=True)
            elif operation == "Brightness Adjustment":
                factor = st.slider("Brightness factor", 0.2, 3.0, 1.0, step=0.1)
                enhancer = ImageEnhance.Brightness(original)
                processed = enhancer.enhance(factor)
                st.image(processed, caption=f"Brightness x{factor}", use_container_width=True)
            elif operation == "Horizontal Flip":
                processed = ImageOps.mirror(original)
                st.image(processed, caption="Flipped Horizontally", use_container_width=True)
            elif operation == "Rotate 90°":
                processed = original.rotate(90, expand=True)
                st.image(processed, caption="Rotated 90°", use_container_width=True)
            
            buf = io.BytesIO()
            processed.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button("Download Processed Image", data=byte_im, file_name="processed.png", mime="image/png")
        except Exception as e:
            st.error(f"Error processing image: {e}")
    else:
        st.info("Upload an image (JPG or PNG) to start editing.")
    
    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state["current_app"] = "home"
        st.rerun()