from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties
from odf.text import H, P, Span

def writeToDoc(path, fileName, outputLabels)
    textdoc = OpenDocumentText()
    p = P(text = "")
    for label in outputLabels:
        p.addText(label)
    textdoc.text.addElement(p)
    textdoc.save(path + fileName + ".odt")