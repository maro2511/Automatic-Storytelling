from ImageNetManager import *

def test():
	requestedIdList = ['n10249270','n02336641','n09918554','n13083586']
	aa = ImageNetManager()
	for id in requestedIdList:
		urlList = aa.getImagesUrlByWordNetId(id)
		aa.downloadImagesForId(id,urlList,5000)
	
if __name__ == '__main__':      
    test()
