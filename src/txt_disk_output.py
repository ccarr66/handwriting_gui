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
    h1style = Style(name="Heading 1", family="paragraph")
    h=H(outlinelevel=1, stylename=h1style, text=strToWrite)
    textdoc.text.addElement(h)
    textdoc.save(fullDestFP)

def writeToDocx(filePath, strToWrite):
    fullDestFP = filePath + ".docx"
    print('Writing output to...')
    print(fullDestFP)
    # Create a new docx at specified file location and write the string on it
    doc = docx.Document()
    doc.add_paragraph(strToWrite)
    doc.save(fullDestFP)