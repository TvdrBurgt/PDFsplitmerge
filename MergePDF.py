from PyPDF2 import PdfFileMerger


pdfs = ['Transcripts_page4.pdf',
        'Transcripts_page5.pdf',
        'Transcripts_page6.pdf']

merger = PdfFileMerger()

for pdf in pdfs:
    merger.append(pdf)

merger.write("merged.pdf")
merger.close()
