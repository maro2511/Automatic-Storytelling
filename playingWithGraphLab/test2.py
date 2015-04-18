from ImageNetManager import *
            
aa = ImageNetManager()
requestedIdList = ['n02336641']
for id in requestedIdList:
    urlList = aa.getImagesUrlByWordNetId(id)
    aa.downloadImagesForId(id,urlList,5000)



