import PyPDF2
import os

def combine_pdfs(pdf_list, output_filename):
    # Create a PDF writer object
    pdf_writer = PyPDF2.PdfWriter()
    
    for pdf_file in pdf_list:
        # Open each PDF file
        with open(pdf_file, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            # Add each page to the writer
            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])
    
    # Write out the combined PDF
    with open(output_filename, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)

# Example usage
pdf_files = ['q1.pdf', 'q2.pdf', 'q3.pdf', 'q4.pdf', 'q5.pdf']  # List of PDF files to combine
output_file = 'QA_rag.pdf'
combine_pdfs(pdf_files, output_file)

print(f'Combined PDF saved as {output_file}')
