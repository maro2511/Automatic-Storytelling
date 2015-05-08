from ImageNetManager import *
import shutil
import errno
import graphlab as gl

##########################################
#           Configuration                #
##########################################
wordnetIdList = ['n09918554','n02336641','n13083586','n09381242','n07697537',"n00446980","n02687992","n00449295","n00440747","n02946921","n09217230","n02110341","n02087122","n12985857","n07727868","n04079244","n10129825","n06359193","n06267145","n04217882","n02958343","n02883344","n03346455","n03147509","n04555897","n02818832","n07575726","n09247410","n02942699","n07679356","n07929519"]

#n09918554 = child
#n02336641 = mouse
#n13083586 = plant
#n09381242 = rock / mountain
#n07697537 = hotdog
#n00446980 - archery
#n02687992 - airfield
#n00449295 - racing
#n00440747 - skiing
#n02946921 - can
#n09217230 - beach
#n02110341 - dalmatian
#n02087122 - dog (hunting)
#n12985857 - coral fungus
#n07727868 - green bean
#n04079244 - building, edifice
#n10129825 - girl
#n06359193 - website
#n06267145 - newspaper
#n04217882 - signboard
#n02958343 - car
#n02883344 - box
#n03346455 - fire,fireplace
#n03147509 - cup
#n04555897 - watch
#n02818832 - bed
#n07575726 - dinner
#n09247410 - cloud
#n02942699 - camera
#n07679356 - bread
#n07929519 - coffee

##########################################

manager = ImageNetManager()
result = []
for wnid in wordnetIdList:
	urlList = manager.getImagesUrlByWordNetId(wnid)
	result.append('wnid: %s, num of images: %s, description: %s' % (wnid,len(urlList),manager.getNamebyWordNetId(wnid)))

print '\n\n****************************\n'	
for line in result:
	print line

