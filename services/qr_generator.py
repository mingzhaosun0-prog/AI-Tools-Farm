# services/qr_generator.py
import streamlit as st
import qrcode
from io import BytesIO

def qr_generator():
    """QR Code Generator — create scannable QR codes from any text or URL."""
    st.markdown("<h2 style='text-align: center;'>📱 QR Code Generator</h2>", unsafe_allow_html=True)
    st.markdown("Turn any text or URL into a scannable QR code in seconds.")

    input_text = st.text_area(
        "Enter text or URL",
        placeholder="https://example.com or any text…",
        height=80,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        fg_color = st.color_picker("Foreground colour", "#1e3c72")
    with col2:
        bg_color = st.color_picker("Background colour", "#ffffff")

    size = st.slider("QR code size", 100, 500, 250, step=50)

    if input_text:
        try:
            qr = qrcode.QRCode(box_size=10, border=2)
            qr.add_data(input_text)
            qr.make(fit=True)
            img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert("RGB")

            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)

            st.image(buf, caption="Your QR Code", width=size)

            st.download_button(
                "⬇️ Download QR Code (PNG)",
                data=buf.getvalue(),
                file_name="qrcode.png",
                mime="image/png",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error generating QR code: {e}")
    else:
        st.info("Enter text or a URL above to generate a QR code.")

    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state["current_app"] = "home"
        st.rerun()
