import sys, os, platform
import PIL.Image
import PIL.ImageTk


debug = False

class PrgStateCtrl:
    def isWindowsOS():
        return platform.system == "Windows"

    _execPath = os.path.dirname(os.path.realpath(__file__))
    _resSubFolderPath = "\\res" if isWindowsOS() else "/res"
    _imgSubFolderPath = "\\images" if isWindowsOS() else "/images"
    _filepathSlash = '\\' if isWindowsOS() else '/'

    _modelName = "handwriting.model"
    _modelPath = _execPath + _resSubFolderPath + _filepathSlash + _modelName

    _imgName = ""
    _imgPath = _execPath + _resSubFolderPath + _imgSubFolderPath

    _saveCount = 0
    _outputFileName = "results_" + str(_saveCount)
    _outputFilePath = _execPath

    _cachedImage = PIL.Image.new('RGBA', (400, 50), (0,0,0,0))

    def __init__(self):
        if(debug):
            self._imgName = "hello_world.png"
        self.LoadImage(self._imgName)

    def GetImagePath(self):
        return self._execPath + self._resSubFolderPath + self._imgSubFolderPath + self._filepathSlash

    def GetImageFullPath(self):
        return self._execPath + self._resSubFolderPath + self._imgSubFolderPath + self._filepathSlash + self._imgName

    def GetModelFullPath(self):
        return self._modelPath

    def GetCachedImage(self):
        return self._cachedImage

    def GetScaledImage(self, imgObj, width, height):
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

    def isValidImg(self, name):
        try:
            PIL.Image.open(self.GetImagePath() + name)
            return True
        except:
            return False

    def IncrementSaveCount(self):
        _saveCount += 1

    def LoadImage(self, imageName):
        if self.isValidImg(imageName):
            self._imgName = imageName
            self._cachedImage = self.GetScaledImage(PIL.Image.open(self.GetImagePath() + self._imgName), 400, 600)
            return True
        else:
            return False