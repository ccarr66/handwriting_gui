import prg_state_ctrl as PSC
try:
    import docx

    from odf.opendocument import OpenDocumentText
    from odf.style import Style, TextProperties
    from odf.text import H, P, Span
except ModuleNotFoundError:
    print('Required libraries not found, please install odfpy and python-docx')


def writeToOdt(filePath, strToWrite):
    fullDestFP = filePath + ".odt"
    print('Writing output to...')
    print(fullDestFP)

    textdoc = OpenDocumentText()
    textdoc.text.addElement(textElem(text = strToWrite))
    textdoc.save(fullDestFP)

def writeToDocx(filePath, strToWrite):
    fullDestFP = filePath + ".docx"
    # Create a new docx at specified file location and write the string on it
    doc = docx.Document()
    doc.add_paragraph(strToWrite)
    doc.save(fullDestFP)