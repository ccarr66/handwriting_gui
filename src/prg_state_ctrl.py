import sys, os, platform
import ocr_image_analyzer as OCR
try:
    import PIL.Image
    import PIL.ImageTk
except ModuleNotFoundError:
    print('Required libraries not found, please install PIL')

debug = False

#********************************************   Program state independent logic
def isWindowsOS():
    return platform.system == "Windows"
    
filepathSlash = '\\' if isWindowsOS() else '/'
    
def scaleImage(imgObj, width, height):
    imgWidth, imgHeight = imgObj.size

    smallestOutDim = min(width, height)
    largestInDim = max(imgObj.size)

    imageScale = smallestOutDim/largestInDim
    newWidth = (int)(imageScale * imgWidth)
    newHeight = (int)(imageScale * imgHeight)

    imgObj = imgObj.resize((newWidth,newHeight), PIL.Image.ANTIALIAS)

    offsetX = (int)(abs(width - newWidth)/2)
    offsetY = (int)(abs(height - newHeight)/2)
    background = PIL.Image.new('RGBA', (width, height), (255, 0, 0, 0))
    foreground = imgObj.convert('RGBA')
    background.paste(foreground, (offsetX, offsetY), foreground)
    return background
    
#********************************************   Object that contains program state
class PrgStateCtrl:

    _execPath = os.path.dirname(os.path.realpath(__file__))
    _resSubFolderPath = "\\res" if isWindowsOS() else "/res"
    _imgSubFolderPath = "\\images" if isWindowsOS() else "/images"

    _modelName = "handwriting.model"
    _modelPath = _execPath + _resSubFolderPath + filepathSlash + _modelName

    _imgName = ""
    _imgPath = _execPath + _resSubFolderPath + _imgSubFolderPath

    _saveCount = 0
    _outputFileName = "results_" + str(_saveCount)
    _outputFilePath = _execPath

    _cachedImage = PIL.Image.new('RGBA', (400, 550), (0,0,0,0))

    _outputMayBegin = False
    _outputIsValid = False
    _currentOutputImageIdx = 0
    _currentOutputImages = []
    _currentOutputText = ""

    def __init__(self):
        if(debug):
            self._imgName = "hello_world.png"
        self.LoadImage(self._imgName)

    def GetImagePath(self):
        return self._execPath + self._resSubFolderPath + self._imgSubFolderPath + filepathSlash

    def GetImageFullPath(self):
        return self._execPath + self._resSubFolderPath + self._imgSubFolderPath + filepathSlash + self._imgName

    def GetModelFullPath(self):
        return self._modelPath

    def GetCachedImage(self):
        return self._cachedImage

    def GetOutputPath(self):
        return self._outputFilePath

    def GetOutputName(self):
        return self._outputFileName

    def isValidImg(self, name):
        try:
            PIL.Image.open(self.GetImagePath() + name)
            return True
        except:
            return False

    def IncrementSaveCount(self):
        self._saveCount += 1

    def LoadImage(self, imageName):
        if self.isValidImg(imageName):
            self._imgName = imageName
            self._cachedImage = scaleImage(PIL.Image.open(self.GetImagePath() + self._imgName), 400, 550)
            self._outputMayBegin = True
            return True
        else:
            return False

    def PerformOCR(self):
        self._currentOutputImages.clear()

        if self._outputMayBegin:
            try:
                self._currentOutputImageIdx = 0
                self._currentOutputImages.append(self._cachedImage)
                text, images = OCR.analyzeImage(self.GetImageFullPath(), self.GetModelFullPath())

                self._currentOutputText = ""
                for c in text:
                    self._currentOutputText += c

                for img in images:
                    img_pil = PIL.Image.fromarray(img)
                    scaledImg = scaleImage(img_pil,400,550)
                    self._currentOutputImages.append(scaledImg)

                self._outputIsValid = True
            except:
                self._outputIsValid = False
    
    def GetOutputText(self):
        if self._outputIsValid:                
            return self._currentOutputText
        else:
            return ""

    def GetNextOutputImage(self):
        if self._outputIsValid:
            if self._currentOutputImageIdx == len(self._currentOutputImages) - 1:
                self._currentOutputImageIdx = 0
            else:
                self._currentOutputImageIdx += 1
                
            return self._currentOutputImages[self._currentOutputImageIdx]
        else:
            return self._cachedImage

    def GetPrevOutputImage(self):
        if self._outputIsValid:
            if self._currentOutputImageIdx == 0:
                self._currentOutputImageIdx = len(self._currentOutputImages) - 1
            else:
                self._currentOutputImageIdx -= 1
                
            return self._currentOutputImages[self._currentOutputImageIdx]
        else:
            return self._cachedImage
