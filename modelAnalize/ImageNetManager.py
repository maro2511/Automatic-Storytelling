import urllib2
import pickle
import os.path
import urllib
import socket
import imghdr



class ImageNetManager:
	idToNameDictionary = dict()
	idToNameFile = os.path.normpath('Data/words.txt')
	def __init__(self):
		self.initIdToNameDictionary()
		
	def initIdToNameDictionary(self): 
		with open(self.idToNameFile) as fileHandle:
			for line in fileHandle:
				id = line.split('\t')[0]
				name = line.split('\t')[1][:-2]
				self.idToNameDictionary[id] = name
				
	def getImagesUrlByWordNetId(self,id):
		socket.setdefaulttimeout(10)
		path = os.path.normpath('Optimization/' + str(id) + '.shu')
		if not os.path.exists(os.path.normpath('Optimization')):
			os.makedirs(os.path.normpath('Optimization'))
		if not os.path.exists(os.path.normpath('URLs')):
			os.makedirs(os.path.normpath('URLs'))
		urlList = list()
		
		if os.path.isfile(path):
			print 'Found optimization file for id: %s' % id
			urlList = pickle.load(open(path,'rb'))
		else:    
			for id in self.getSubTreeIdsForWordNetId(id):
				try:
					print 'z'
					urlList += self.getUrlsForId(id)
				except:
					continue
					
			print 'Saving optimization file for id: %s' % id
			pickle.dump(urlList, open(path,'wb'))
	
		with open(os.path.normpath('URLs/' + str(id) + '.txt'),'w+') as outputFileHandle:
			[outputFileHandle.write(item) for item in urlList]
		print '--> Url file for id: %s was successfully created. Found %d images' % (id,len(urlList))
			
		return urlList
	
	def getUrlsForId(self,id):
		url = 'http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=%s' % id
		return [line for line in urllib2.urlopen(url,timeout=10)]
		
	def getSubTreeIdsForWordNetId(self,id):
		url = 'http://www.image-net.org/api/text/wordnet.structure.hyponym?wnid=%s&full=1' % id
		fileHandle = urllib2.urlopen(url)
		return [line[1:-1] for line in fileHandle if line.startswith('-')] + [id]
	
	def getNamebyWordNetId(self,id):
		try:
			return self.idToNameDictionary[id]
		except:
			return 'None'
			
	# TODO: remove url from deleteList
	def downloadImagesForId(self,id,urlList,WORKING_DIR, limit = -1, force = 'no'):
		socket.setdefaulttimeout(3)
		directory = os.path.normpath(WORKING_DIR +'/'+ str(id))
		print '***\n'
		print 'downloading images to dir: ' + directory + '\n'
		print '***\n'
		urlListNum = len(urlList)
		
		if not os.path.exists(directory):
			os.makedirs(directory)
	
		goodImagesCounter = 0
		deleteList = list()   
		for index,url in enumerate(urlList):
			if goodImagesCounter == limit:
				break
			if os.path.exists(os.path.normpath(directory + '/' + url.split('/')[-1][:-2])) and force == 'no':
				print 'Image %d of %d already in memory - skip download' % (index,urlListNum)
				goodImagesCounter += 1;
				continue
			try:
				print 'Downloading image %d of %d: %s' % (index,urlListNum,url.split('/')[-1][:-1])
				filePath = os.path.normpath(directory + '/' + url.split('/')[-1][:-2])
				urllib.urlretrieve(url,filePath)
				if imghdr.what(filePath) != 'jpeg':
					print '-- Image delete (wrong format / not in server)'
					deleteList += [url]
					os.remove(filePath)
				else:
					goodImagesCounter += 1;
			except:
				print 'Error downloading image %d' % index
				deleteList += [url]
				continue
		socket.setdefaulttimeout(20)
        
