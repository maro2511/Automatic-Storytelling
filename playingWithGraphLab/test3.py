from ImageNetManager import *
            
aa = ImageNetManager()
requestedIdList = ['n09918554']
for id in requestedIdList:
    urlList = aa.getImagesUrlByWordNetId(id)
    aa.downloadImagesForId(id,urlList,5000)



