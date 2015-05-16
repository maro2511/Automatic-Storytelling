import urllib2
import pickle
import os.path
import urllib
import socket
import imghdr
import shutil
import math
import random

class ImageDatabase:
    DATABASE_DIRECTORY = str()
    idToNameDictionary = dict()
    idToNameFile = os.path.normpath('Data/words.txt')

    def __init__(self,_DATABASE_DIRECTORY):
        self.initIdToNameDictionary()
        self.DATABASE_DIRECTORY = _DATABASE_DIRECTORY
        self.image_db_paths = list()

        for root, dirs, files in os.walk(_DATABASE_DIRECTORY):
            for name in files:
                self.image_db_paths.append(root + '/' + name)
        return

    def createImageEnviroment(self,wordnetIdList,numOfCategories,numOfImagesPerCategory):
        requestedIds = wordnetIdList[:numOfCategories]

        WORKING_DIR = os.getcwd() + '/IMAGES_%d_%d' % (numOfCategories,numOfImagesPerCategory)

        if not os.path.exists(os.path.normpath(WORKING_DIR)):
            os.makedirs(os.path.normpath(WORKING_DIR))

        for id in requestedIds:
            #Create images directory
            if not os.path.exists(os.path.normpath(WORKING_DIR + '/' + id)):
                os.makedirs(os.path.normpath(WORKING_DIR + '/' + id))

            #Get images path from local database
            local_images_path = filter(lambda x: str(id + '/') in x,self.image_db_paths)
            counter = len(local_images_path)

            #Check if we already have enough images
            num_of_requested_images = math.ceil(1.1*numOfImagesPerCategory)
            if (counter < num_of_requested_images):
                # not enough images (10% are for test and statistics)
                print "Not enough images for id: %s. Searching the web for new images" % id
                print "Try 1: Download from Image-Net"
                imagenet_url_list = self.getImagesUrlByWordNetId(id)
                random.shuffle(imagenet_url_list)  # Shuffle the list in order to get images from different sub-wnids
                counter = self.downloadImagesForId(id,imagenet_url_list,self.DATABASE_DIRECTORY,num_of_requested_images,len(local_images_path))

                if counter < num_of_requested_images:
                    print "Try 2: Download from Yahoo/Bing"
                    #TODO: add implementation

                    if counter < num_of_requested_images:
                        print "WARNING: Not enough images for id: %s" % id

            # get category paths for local database
            local_image_paths = list()
            CATEGORY_DIR_ON_DB = self.DATABASE_DIRECTORY + '/' + str(id)
            for root, dirs, files in os.walk(CATEGORY_DIR_ON_DB):
                for name in files:
                    local_image_paths.append(root + '/' + name)

            # Shuffle the list in order to get images from different sub-wnids
            random.shuffle(local_images_path)

            #TODO: fix bug, destination folder could have already images on it. consider deleting folder
            #copy files from database to destination folder
            for path in local_image_paths[:int(num_of_requested_images)]:
                file_name = os.path.normpath(path.split('/')[-1])
                destination_path = WORKING_DIR + '/' + id + '/' + file_name
                if not os.path.exists(destination_path):
                    shutil.copyfile(path,destination_path)

    def initIdToNameDictionary(self):
        with open(self.idToNameFile) as fileHandle:
            for line in fileHandle:
                id = line.split('\t')[0]
                name = line.split('\t')[1][:-2]
                self.idToNameDictionary[id] = name

    def getImagesUrlByWordNetId(self, id):
        socket.setdefaulttimeout(10)
        path = os.path.normpath('Optimization/' + str(id) + '.shu')
        if not os.path.exists(os.path.normpath('Optimization')):
            os.makedirs(os.path.normpath('Optimization'))
        if not os.path.exists(os.path.normpath('URLs')):
            os.makedirs(os.path.normpath('URLs'))
        urlList = list()

        if os.path.isfile(path):
            print 'Found optimization file for id: %s' % id
            urlList = pickle.load(open(path, 'rb'))
        else:
            for id in self.getSubTreeIdsForWordNetId(id):
                try:
                    urlList += self.getUrlsForId(id)
                except:
                    continue

            print 'Saving optimization file for id: %s' % id
            pickle.dump(urlList, open(path, 'wb'))

        with open(os.path.normpath('URLs/' + str(id) + '.txt'), 'w+') as outputFileHandle:
            [outputFileHandle.write(item) for item in urlList]
        print '--> Url file for id: %s was successfully created. Found %d images' % (id, len(urlList))

        return urlList

    def getUrlsForId(self, id):
        url = 'http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=%s' % id
        return [line for line in urllib2.urlopen(url, timeout=10)]

    def getSubTreeIdsForWordNetId(self, id):
        url = 'http://www.image-net.org/api/text/wordnet.structure.hyponym?wnid=%s&full=1' % id
        fileHandle = urllib2.urlopen(url)
        return [line[1:-1] for line in fileHandle if line.startswith('-')] + [id]

    def getNamebyWordNetId(self, id):
        try:
            return self.idToNameDictionary[id]
        except:
            return 'None'

    #TODO: replace WORKING_DIR with self
    def downloadImagesForId(self, id, urlList, WORKING_DIR, limit=-1,ImagesCounter=0):
        socket.setdefaulttimeout(3)
        directory = os.path.normpath(WORKING_DIR + '/' + str(id))
        counter = ImagesCounter
        print '***\n'
        print 'downloading images to dir: ' + directory + '\n'
        print '***\n'
        urlListLen = len(urlList)

        if not os.path.exists(directory):
            os.makedirs(directory)

        deleteList = list()
        for index, url in enumerate(urlList):
            if counter == limit:
                break
            if os.path.exists(os.path.normpath(directory + '/' + url.split('/')[-1][:-2])):
                print 'Image %d of %d already in memory or there is another image with the same name - skip download' % (
                    index, urlListLen)
                continue
            try:
                print 'Downloading image %d of %d: %s' % (index, urlListLen, url.split('/')[-1][:-1])
                filePath = os.path.normpath(directory + '/' + url.split('/')[-1][:-2])
                urllib.urlretrieve(url, filePath)
                if (imghdr.what(filePath) != 'jpeg') or (not (filePath.endswith('.jpg'))):
                    print '-- Image delete (wrong format / not in server)'
                    deleteList += [url]
                    os.remove(filePath)
                else:
                    counter += 1;
            except:
                print 'Error downloading image %d' % index
                deleteList += [url]
                continue
        socket.setdefaulttimeout(20)

        path = os.path.normpath('Optimization/' + str(id) + '.shu')
        if os.path.isfile(path):
            print "removing invalid urls from optimization files"
            urlList = pickle.load(open(path, 'rb'))
            urlList = list(set(urlList) - set(deleteList))
            pickle.dump(urlList, open(path, 'wb'))

        return counter
