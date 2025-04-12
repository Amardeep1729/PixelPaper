import streamlit as st
st.set_option('server.maxUploadSize', 1024)

import fitz  # PyMuPDF
import PyPDF2
import cv2
import os
import tempfile

# === Utilities ===
def get_size_readable(file_path):
    size = os.path.getsize(file_path)
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    else:
        return f"{size / (1024 * 1024):.2f} MB"

# === PDF FUNCTIONS ===
def merge_pdfs(files, output_path):
    merger = PyPDF2.PdfMerger()
    for file in files:
        merger.append(file)
    merger.write(output_path)
    merger.close()


def compress_pdf(input_path, output_path, compress_percent):
    pdf = fitz.open(input_path)
    scale = compress_percent / 100
    new_pdf = fitz.open()

    for page in pdf:
        images = page.get_images(full=True)

        if not images:
            new_pdf.insert_pdf(pdf, from_page=page.number, to_page=page.number)
            continue

        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)

        rect = page.rect
        new_rect = fitz.Rect(0, 0, rect.width * scale, rect.height * scale)
        new_page = new_pdf.new_page(width=new_rect.width, height=new_rect.height)
        new_page.insert_image(new_rect, pixmap=pix)

    new_pdf.save(output_path, garbage=4, deflate=True, clean=True)
    new_pdf.close()
    pdf.close()


def resize_pdf(input_path, output_path, scale):
    pdf = fitz.open(input_path)
    new_pdf = fitz.open()

    for page in pdf:
        rect = page.rect
        new_rect = fitz.Rect(0, 0, rect.width * (scale / 100), rect.height * (scale / 100))
        mat = fitz.Matrix(scale / 100, scale / 100)
        pix = page.get_pixmap(matrix=mat)
        new_page = new_pdf.new_page(width=new_rect.width, height=new_rect.height)
        new_page.insert_image(new_rect, pixmap=pix)

    new_pdf.save(output_path, garbage=4, deflate=True)
    new_pdf.close()
    pdf.close()


# === IMAGE FUNCTIONS ===
def resize_image(input_path, output_path, scale):
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    new_dim = (int(img.shape[1] * scale / 100), int(img.shape[0] * scale / 100))
    resized = cv2.resize(img, new_dim)
    cv2.imwrite(output_path, resized)


def compress_image(input_path, output_path, quality):
    img = cv2.imread(input_path)
    cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, quality])


# === STREAMLIT GUI ===
st.set_page_config(page_title="PDF/Image Toolkit", layout="centered")
st.title("Welcome to PixelPaper 📄✨")
st.markdown("A simple, powerful tool to compress, resize, and merge your PDFs and images.")

option = st.sidebar.selectbox("Choose an action:", [
    "Merge PDFs", "Compress PDF", "Resize PDF", "Resize Image", "Compress Image"])

with tempfile.TemporaryDirectory() as tmpdir:

    if option == "Merge PDFs":
        uploaded_files = st.file_uploader("Upload PDFs to merge", type="pdf", accept_multiple_files=True)
        if uploaded_files:
            output_filename = st.text_input("Output filename", "merged.pdf")
            if st.button("Merge"):
                paths = [os.path.join(tmpdir, f.name) for f in uploaded_files]
                for file, path in zip(uploaded_files, paths):
                    with open(path, "wb") as f:
                        f.write(file.read())
                out_path = os.path.join(tmpdir, output_filename)
                merge_pdfs(paths, out_path)
                st.success("PDFs merged successfully!")
                st.download_button("📥 Download Merged PDF", open(out_path, "rb"), file_name=output_filename)

    elif option == "Compress PDF":
        uploaded = st.file_uploader("Upload PDF", type="pdf")
        compress_percent = st.slider("Compression level", 10, 100, 70)
        if uploaded:
            input_path = os.path.join(tmpdir, uploaded.name)
            with open(input_path, "wb") as f:
                f.write(uploaded.read())
            output_path = os.path.join(tmpdir, "compressed.pdf")
            if st.button("Compress"):
                compress_pdf(input_path, output_path, compress_percent)
                st.success("Compression done!")
                st.download_button("📥 Download Compressed PDF", open(output_path, "rb"), file_name="compressed.pdf")

    elif option == "Resize PDF":
        uploaded = st.file_uploader("Upload PDF", type="pdf")
        scale = st.slider("Resize scale (%)", 10, 100, 50)
        if uploaded:
            input_path = os.path.join(tmpdir, uploaded.name)
            with open(input_path, "wb") as f:
                f.write(uploaded.read())
            output_path = os.path.join(tmpdir, "resized.pdf")
            if st.button("Resize"):
                resize_pdf(input_path, output_path, scale)
                st.success("PDF resized!")
                st.download_button("📥 Download Resized PDF", open(output_path, "rb"), file_name="resized.pdf")

    elif option == "Resize Image":
        uploaded = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        scale = st.slider("Resize scale (%)", 10, 100, 50)
        if uploaded:
            input_path = os.path.join(tmpdir, uploaded.name)
            with open(input_path, "wb") as f:
                f.write(uploaded.read())
            output_path = os.path.join(tmpdir, "resized.jpg")
            if st.button("Resize"):
                resize_image(input_path, output_path, scale)
                st.success("Image resized!")
                st.download_button("📥 Download Resized Image", open(output_path, "rb"), file_name="resized.jpg")

    elif option == "Compress Image":
        uploaded = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        quality = st.slider("JPEG Quality", 1, 100, 70)
        if uploaded:
            input_path = os.path.join(tmpdir, uploaded.name)
            with open(input_path, "wb") as f:
                f.write(uploaded.read())
            output_path = os.path.join(tmpdir, "compressed.jpg")
            if st.button("Compress"):
                compress_image(input_path, output_path, quality)
                st.success("Image compressed!")
                st.download_button("📥 Download Compressed Image", open(output_path, "rb"), file_name="compressed.jpg")


