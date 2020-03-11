import time
import os

def saveFile(fileObj, filename, uploadPath):
    savePath = uploadPath + str(time.time()) + '/'
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    saveFilePath = savePath + filename
    with open(saveFilePath, 'wb') as f:
        f.write(fileObj.read())
        f.close()
    return saveFilePath
