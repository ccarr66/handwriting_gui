import prg_state_ctrl as PSC
import txt_disk_output as OUT
try:
    import PIL.Image
    import PIL.ImageTk
    from tkinter import *
    from tkinter import ttk
    from tkinter.scrolledtext import ScrolledText
except ModuleNotFoundError:
    print('Required libraries not found, please install tkinter & PIL')

#*******************************************************    main window
mainWindow = Tk()
mainWindow.title("Handwriting Parser")
mainWindow.geometry('800x600')
mainWindow.resizable(False,False)
mainWindow.columnconfigure(0, weight=1)
mainWindow.rowconfigure(0, weight=1)

#*******************************************************    init glob state

globState = PSC.PrgStateCtrl()
cachedImage = PIL.ImageTk.PhotoImage(globState.GetCachedImage())
modelName = StringVar(mainWindow, value=globState._modelName)
imageName = StringVar(mainWindow, value=globState._imgName)

saveWindow = None
saveWindowOpen = False

outputFileName = StringVar(saveWindow,value=globState.GetOutputName())
outputFilePath = StringVar(saveWindow,value=globState.GetOutputPath())
outputDocType = StringVar()

#*******************************************************    gui state control
def LoadModel():
    if not globState.SetModel(modelName.get()):
        newWindow = Toplevel(mainWindow)
        newWindow.title("Error") 
        errorLbl = Label(newWindow, text = "Text entered is not a valid model name. Must be in same directory as executable")
        errorLbl.grid(row=0, column=0, padx=15, pady=15)

def LoadImage():
    if not globState.LoadImage(imageName.get()):
        newWindow = Toplevel(mainWindow) 
        newWindow.title("Error") 
        errorLbl = Label(newWindow, text = "Text entered is not a valid image name. Must be in same directory as executable")
        errorLbl.grid(row=0, column=0, padx=15, pady=15)
    else:
        cachedImage = PIL.ImageTk.PhotoImage(globState.GetCachedImage())
        imgDisplayLbl.configure(image=cachedImage)
        imgDisplayLbl.image = cachedImage
        imgDisplayLbl.update_idletasks()

def ParseImage():
    globState.PerformOCR()

    outputText['state'] = "normal"
    outputText.delete('1.0', END)
    outputText.insert(END, globState.GetOutputText())
    outputText.update_idletasks()
    outputText['state'] = "disabled"

    cachedImage = PIL.ImageTk.PhotoImage(globState.GetNextOutputImage())
    imgDisplayLbl.configure(image=cachedImage)
    imgDisplayLbl.image = cachedImage
    imgDisplayLbl.update_idletasks()

def NextImage():
    cachedImage = PIL.ImageTk.PhotoImage(globState.GetNextOutputImage())
    imgDisplayLbl.configure(image=cachedImage)
    imgDisplayLbl.image = cachedImage
    imgDisplayLbl.update_idletasks()

def PrevImage():
    cachedImage = PIL.ImageTk.PhotoImage(globState.GetPrevOutputImage())
    imgDisplayLbl.configure(image=cachedImage)
    imgDisplayLbl.image = cachedImage
    imgDisplayLbl.update_idletasks()

def SaveFile():
    filePath = outputFilePath.get() + PSC.filepathSlash + outputFileName.get()
    if outputDocType.get() == 'docx':
        OUT.writeToDocx(filePath, globState.GetOutputText())
    if outputDocType.get() == 'odt':
        OUT.writeToOdt(filePath, globState.GetOutputText())
    if outputDocType.get() == 'txt':
        OUT.writeToTxt(filePath, globState.GetOutputText())
    saveWindow.destroy()

def SaveDialog():
    global saveWindowOpen
    global saveWindow
    global outputFileName
    global outputFilePath
    if saveWindowOpen is False:
        saveWindowOpen = True

        saveWindow = Toplevel(mainWindow) 
        saveWindow.title("Save File") 
        saveWindow.resizable(False,False)
        saveWindow.rowconfigure((0,2), weight=1)

        fileNameLbl = ttk.Label(saveWindow, text = "File name:")
        fileNameLbl.grid(row=0, column=0, padx=5, pady=5)

        filePathLbl = ttk.Label(saveWindow, text = "File path:")
        filePathLbl.grid(row=1, column=0, padx=5, pady=5)
        
        outputFileName = StringVar(saveWindow,value=globState.GetOutputName())
        fileNameEntry = ttk.Entry(saveWindow, textvariable=outputFileName, width = 50)
        fileNameEntry.grid(row=0, column=1, columnspan=3, padx=5, pady=5)

        outputFilePath = StringVar(saveWindow,value=globState.GetOutputPath())
        filePathEntry = ttk.Entry(saveWindow, textvariable=outputFilePath, width = 50)
        filePathEntry.grid(row=1, column=1, columnspan=3,  padx=5, pady=5)

        docTypeCombBx = ttk.Combobox(saveWindow, textvariable=outputDocType, values=('.docx', '.odt', '.txt'))
        docTypeCombBx.grid(row=2, column=1, padx=5, pady=5, sticky=W)
        docTypeCombBx.current(0)
        docTypeCombBx.update_idletasks()

        saveBtn = ttk.Button(saveWindow, command=SaveFile, text="Save", width=20)
        saveBtn.grid(row=2, column=3, padx=5, pady=5, sticky=E)

        saveWindow.wait_window()
        saveWindowOpen = False



#*******************************************************    WIDGET CONFIG
content = ttk.Frame(mainWindow)

lhsFrame = ttk.Frame(content)
imgDisplayLbl = ttk.Label(lhsFrame, image=cachedImage)
prevBtn = ttk.Button(lhsFrame, command=PrevImage, text="Prev")
nextBtn = ttk.Button(lhsFrame, command=NextImage, text="Next")

dividerFrame = ttk.Frame(content)
dividerImg = PIL.ImageTk.PhotoImage(PIL.Image.new('RGBA', (5, 600), (100, 100, 100, 0xff)))
dividerImgDisplayLbl = ttk.Label(dividerFrame, image=dividerImg)

rhsFrame = ttk.Frame(content)
modelLocLbl = ttk.Label(rhsFrame, text="Model name")
modelLocEntry = ttk.Entry(rhsFrame, textvariable=modelName, width = 42)
modelLocUpdateBtn = ttk.Button(rhsFrame, command=LoadModel, text="Load Model", width=20)

imgLocLbl = ttk.Label(rhsFrame, text="Image name")
imgLocEntry = ttk.Entry(rhsFrame, textvariable=imageName, width = 42)
imgLocUpdateBtn = ttk.Button(rhsFrame, command=LoadImage, text="Load Image", width=20)

outputLbl = ttk.Label(rhsFrame, text="Output Text",)
outputText = ScrolledText(rhsFrame, state="disabled", width = 42, height=7)
outputGenBtn = ttk.Button(rhsFrame, command = ParseImage, text="Generate Output", width=20)

outputSaveBtn = ttk.Button(rhsFrame, command=SaveDialog, text="Save Output", width=20)

#******************************************************     GRID CONFIG
content.grid(column=0, row=0, sticky="NS")
content.columnconfigure((1,3), weight=1)

lhsFrame.grid(column=0, row=0, sticky="NS")
lhsFrame.rowconfigure((0,2), weight=2)
imgDisplayLbl.grid(column=0, row=1, padx=5, columnspan=3)
prevBtn.grid(column=0, row=4, padx=5, pady=5, sticky=S)
nextBtn.grid(column=2, row=4, padx=5, pady=5, sticky=S)

dividerFrame.grid(column=2, row=0)
dividerImgDisplayLbl.grid(column=0, row=0, padx=5)

rhsFrame.grid(column=4, row=0, sticky="NS")
rhsFrame.rowconfigure((0,4,8,12), weight=2)
rhsFrame.columnconfigure((1), weight=1)

modelLocLbl.grid(column=0, row=1, padx=5, sticky=W)
modelLocEntry.grid(column=0, row=2, padx=5, columnspan=3, sticky="WE")
modelLocUpdateBtn.grid(column=2, row=3, padx=5, pady=5, sticky=E)

imgLocLbl.grid(column=0, row=5, padx=5, sticky=W)
imgLocEntry.grid(column=0, row=6, padx=5, columnspan=3, sticky="WE")
imgLocUpdateBtn.grid(column=2, row=7, padx=5, pady=5, sticky=E)

outputLbl.grid(column=0, row=9, padx=5, sticky=W)
outputText.grid(column=0, row=10, padx=5, columnspan=3, sticky="WE")
outputGenBtn.grid(column=2, row=11, padx=5, pady=5, sticky=E)

outputSaveBtn.grid(column=2, row=13, padx=5, pady=5, sticky=E)

mainWindow.mainloop()