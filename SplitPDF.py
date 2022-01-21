from PyPDF2 import PdfFileWriter, PdfFileReader
import os

# type the name of the file to split
filename = "Master_Thesis_Draft_2_Autofocus4review.pdf"

# type the pages to extract, comma separated
pages = (15,16,17,18,19)

# do you want to stitch the pages together?
stitch = True


inputpdf = PdfFileReader(open(os.path.join(os.getcwd(), filename), "rb"))
output = PdfFileWriter()
for i in range(inputpdf.numPages):
    if type(pages) is tuple:
        if i+1 in pages:
            if stitch:
                output.addPage(inputpdf.getPage(i))
            else:
                output = PdfFileWriter()
                output.addPage(inputpdf.getPage(i))
                with open((filename[0:len(filename)-4] + "_page%s.pdf" % (i+1)), "wb") as outputStream:
                    output.write(outputStream)
        else:
            pass
    elif type(pages) is int:
        if i+1 == pages:
            output = PdfFileWriter()
            output.addPage(inputpdf.getPage(i))
            with open((filename[0:len(filename)-4] + "_page%s.pdf" % (i+1)), "wb") as outputStream:
                output.write(outputStream)
        else:
            pass

if stitch:
    with open((filename[0:len(filename)-4] + "_split&stitched.pdf"), "wb") as outputStream:
        output.write(outputStream)
else:
    pass