import PyPDF2
import fitz #PyMuPDF
import cv2
import os

# === PDF FUNCTIONS ===
def merge_pdfs(pdf_files, output_file):
    
    merger = PyPDF2.PdfMerger()
    for filename in pdf_files:
        with  open(filename, 'rb') as f:
           merger.append(f)
    merger.write(output_file)
    merger.close()    
    
    print(f" Merged PDF saved as '{output_file}'")

def get_size_readable(file_path):
    size = os.path.getsize(file_path)
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    else:
        return f"{size / (1024 * 1024):.2f} MB"    

def compress_pdf(input_file, output_file, compress_percent):
    pdf = fitz.open(input_file)
    scale = compress_percent / 100
    new_pdf = fitz.open()

    for page in pdf:
        images = page.get_images(full=True)

        if not images:
            # No images – keep the page structure as is
            new_pdf.insert_pdf(pdf, from_page=page.number, to_page=page.number)
            continue

        # Image-based page: compress as image
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)

        # Create a new page and insert the compressed image
        rect = page.rect
        new_rect = fitz.Rect(0, 0, rect.width * scale, rect.height * scale)
        new_page = new_pdf.new_page(width=new_rect.width, height=new_rect.height)
        new_page.insert_image(new_rect, pixmap=pix)

    # Save with aggressive cleanup and compression
    new_pdf.save(output_file, garbage=4, deflate=True, clean=True)
    new_pdf.close()
    pdf.close()

    
    print(f"Compressed PDF saved as '{output_file}'")
    



def resize_pdf(input_path, output_path, scale):
    # Open the original PDF
    pdf = fitz.open(input_path)
    new_pdf = fitz.open()

    # Loop through each page and resize
    for page in pdf:
        
        
        # Get the current page size
        rect = page.rect


        # Calculate the new width and new height based on the scale percentage
        # Create a new rectangle starting from (0, 0) with the new width and height
        # Defines where and how large the image will be placed on the new page
        new_rect = fitz.Rect(0, 0, rect.width * (scale/100), rect.height * (scale/100))

        # Create a new PDF page with new size
        mat = fitz.Matrix(scale/100, scale/100)  # scale the content
        pix = page.get_pixmap(matrix=mat)

        # creates new pages and insert it
        new_page = new_pdf.new_page(width=new_rect.width, height=new_rect.height)
        new_page.insert_image(new_rect, pixmap=pix)

    # Save with compression
    new_pdf.save(output_path, garbage=4, deflate=True)
    new_pdf.close()
    pdf.close()

# === IMAGE FUNCTIONS ===
def resize_image(source, destination, scale_percent):
    image = cv2.imread(source, cv2.IMREAD_UNCHANGED)
    new_width = int(image.shape[1] * scale_percent / 100)
    new_height = int(image.shape[0] * scale_percent / 100)
    output = cv2.resize(image, (new_width, new_height))
    cv2.imwrite(destination, output)
    print(f" Resized image saved as '{destination}'")


def compress_image(source, destination, quality):
    # Force .jpg extension if not provided
    if not destination.lower().endswith((".jpg", ".jpeg")):
        destination = os.path.splitext(destination)[0] + ".jpg"
    
    image = cv2.imread(source)
    success = cv2.imwrite(destination, image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    
    if success:
        print(f" Compressed image saved as '{destination}' (quality = {quality})")
    else:
        print(" Failed to save image. Check the filename or path.")



print("\nWhat would you like to do?")
print("1. Merge PDFs")
print("2. Compress PDF (no resizing)")
print("3. Resize PDF")
print("4. Resize Image")
print("5. Compress Image")


choice = input("Enter 1, 2, 3, 4, or 5: ")

if choice == "1":
    print("👉 This will combine multiple PDF files into a single one.")
    pdf_list = input("Enter PDF filenames separated by commas: ").split(",")
    pdf_list = [file.strip() for file in pdf_list if file.strip()]
    output_file = input("Enter the name of the merged output PDF: ")
    merge_pdfs(pdf_list, output_file)

elif choice == "2":
    print("👉 This will compress your PDF. 100% = keep original size (lossless), lower % = smaller file with slight quality loss.")
    input_path = input("Enter the path of the input PDF: ")
    output_path = input("Enter the output filename: ")
    while True:
        try:
            compress_percent = int(input("Enter compression level (100 = no resize, 90 = light, 50 = strong): "))
            if 10 <= compress_percent <= 100:
                break
            else:
                print("Please enter a value between 10 and 100.")
        except ValueError:
            print("Please enter a valid number.")

    compress_pdf(input_path, output_path, compress_percent)

elif choice == "3":
    print("👉 This will resize the pages. For example, 30 means each page will be 30% of the original size.")
    input_path = input("Enter the path of the input PDF: ")
    output_path = input("Enter the output filename: ")
    
    while True:
        try:
            scale_percent = int(input("Enter scale percent (like... 20 for 20% or 50 for 50% ): "))
            if 1 <= scale_percent <= 100:
                break
            else:
                print("Please enter a value between 1 and 100.")
        except ValueError:
            print("Invalid input! Please enter a number.")
    
    resize_pdf(input_path, output_path, scale_percent)

elif choice == "4":
    print("👉 This will resize an image to a smaller version based on your input.")
    source = input("Enter the source image filename (e.g., image.jpg): ")
    destination = input("Enter the destination filename: ")
    scale_percent = int(input("Enter scale percent (e.g., 30 = 30% of original size): "))
    resize_image(source, destination, scale_percent)

elif choice == "5":
    print("👉 This will compress the image by the given percentage quality (e.g., 80 means 80% of original quality).")
    source = input("Enter the source image filename  ")
    destination = input("Enter the destination filename: ")
    while True:
        try:
            quality = int(input("Enter compression quality (1 = max compression, 100 = best quality): "))
            if 1 <= quality <= 100:
                break
            else:
                print("Please enter a value between 1 and 100.")
        except ValueError:
            print("Please enter a valid number.")
    compress_image(source, destination, quality)    

else:
    print("Invalid choice. Please enter 1, 2, 3 ,4 or 5.")

