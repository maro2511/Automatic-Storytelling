from ImageNetManager import *
import shutil
import errno
import time
import graphlab as gl


##########################################
#           Configuration                #
##########################################
wordnetIdList = ['n09918554','n02336641','n13083586','n09381242','n07697537']
#n09918554 = child
#n02336641 = mouse
#n13083586 = plant
#n09381242 = rock / mountain
#n07697537 = hotdog

numOfCategoriesList = [2,3,4,5]
numOfImagesPerCategoryList = [100,200,500,1000]
numOfIterationList = [1,2,5]
##########################################

def copyDir(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            print('Directory not copied. Error: %s' % e)

def downloadImages():
	manager = ImageNetManager()
	PREV_WORKING_DIR = ''
	for index,numOfCategories in enumerate(numOfCategoriesList):
		requestedIds = wordnetIdList[:numOfCategories]
		for numOfImagesPerCategory in numOfImagesPerCategoryList:
			print '###\nDownloading images for scenario: numOfCategories = %d, numOfImagesPerCategory = %d\n###\n' % (numOfCategories,numOfImagesPerCategory)
			WORKING_DIR = os.getcwd() + '/IMAGES_%d_%d' % (numOfCategories,numOfImagesPerCategory)
			if not os.path.exists(os.path.normpath(WORKING_DIR)):
				os.makedirs(os.path.normpath(WORKING_DIR))        
			for id in requestedIds:
				if not os.path.exists(os.path.normpath(WORKING_DIR +'/'+ str(id))):
					urlList = manager.getImagesUrlByWordNetId(id)
					manager.downloadImagesForId(id,urlList,WORKING_DIR,limit = numOfImagesPerCategory)			
			if (index < len(numOfCategoriesList)) :
				NEXT_WORKING_DIR = list(WORKING_DIR)
				NEXT_WORKING_DIR[len(os.getcwd())+8] = str(numOfCategoriesList[index+1])
				NEXT_WORKING_DIR = "".join(NEXT_WORKING_DIR)
				print 'curent:' + WORKING_DIR + '\n'
				print 'next:' + NEXT_WORKING_DIR + '\n'
				if not os.path.exists(os.path.normpath(NEXT_WORKING_DIR)):
					copyDir(WORKING_DIR,NEXT_WORKING_DIR)
			

def downloadTestImages(numberOfTestImages):
    #test images are download from the end of the url list
    manager = ImageNetManager()
    for numOfCategories in numOfCategoriesList:
		requestedIds = wordnetIdList[:numOfCategories]
		for numOfImagesPerCategory in numOfImagesPerCategoryList:
			WORKING_DIR = os.getcwd() + '/TEST_IMAGES_%d_%d' % (numOfCategories,numOfImagesPerCategory)
			for id in requestedIds:
				urlList = manager.getImagesUrlByWordNetId(id)
				manager.downloadImagesForId(id,urlList[::-1],WORKING_DIR,limit = numberOfTestImages)

def createClassificator(numOfCategories,numOfImagesPerCategory,numOfIteration):
	WORKING_DIR = os.getcwd() + '/IMAGES_%d_%d' % (numOfCategories,numOfImagesPerCategory)
	print WORKING_DIR
	train_sf = gl.image_analysis.load_images(WORKING_DIR, random_order=True)
	train_sf['wnid'] = train_sf['path'].apply(lambda x: x.split('/')[-2])
	train_sf['image'] = gl.image_analysis.resize(train_sf['image'], 256, 256)
	
	unique_labels = train_sf['wnid'].unique().sort()                                             
	class_map = {}                                                                  
	for i in range(len(unique_labels)):                                                        
		class_map[unique_labels[i]] = i                                                        
	train_sf['label'] = train_sf['wnid'].apply(lambda x: class_map[x])
	
	print train_sf
	
	mean_image = train_sf['image'].mean()
	
	model = gl.neuralnet_classifier.create(train_sf[['image', 'label']],                      
                                   target='label',
                                   mean_image=mean_image,                          
                                   max_iterations=numOfIteration,                              
                                   batch_size=int(numOfImagesPerCategory/10))
	
	return model

def	testClassificator(model,numOfCategories):
	WORKING_DIR = os.getcwd() + '/TEST_IMAGES_%d' % (numOfCategories)
	
	validation_data = gl.image_analysis.load_images(WORKING_DIR, random_order=True)
	validation_data['wnid'] = validation_data['path'].apply(lambda x: x.split('/')[-2])
	validation_data['image'] = gl.image_analysis.resize(validation_data['image'], 256, 256)
	
	unique_labels = validation_data['wnid'].unique().sort()                                              
	class_map = {}                                                                  
	for i in range(len(unique_labels)):                                                        
		class_map[unique_labels[i]] = i                                                        
	validation_data['label'] = validation_data['wnid'].apply(lambda x: class_map[x])
	
	print model.evaluate(validation_data)

def testEnviroment():
	result = list()
	for numOfCategories in numOfCategoriesList:
		for numOfImagesPerCategory in numOfImagesPerCategoryList:
			for numOfIteration in numOfIterationList:
				print '#' * 10
				print '# numOfCategories, = %d, numOfImagesPerCategory = %d, numOfIteration = %d' % (numOfCategories,numOfImagesPerCategory,numOfIteration)
				print '#' * 10
				start_time = int(time.time())
				model = createClassificator(numOfCategories,numOfImagesPerCategory,numOfIteration)
				after_classificator_time = int(time.time() - start_time)
				testClassificator(model,numOfCategories)
				after_test = int(time.time() - start_time)
				result.append((numOfCategories,numOfImagesPerCategory,numOfIteration,start_time,after_classificator_time,after_test))
				print '\n' * 10
	return result
	

def printTimeResults(results):
	print '#' * 10
	print '# RESULTS!	'
	print '#' * 10
	for item in results:
		print 'numOfCategories = %d ,numOfImagesPerCategory = %d ,numOfIteration = %d ,start_time = %d ,after_classificator_time = %d ,after_test = %d' % item
		print '#'
	print '###'
	
if __name__ == '__main__':      
    downloadImages()
    downloadTestImages(100)
	results = testEnviroment()
	printTimeResults(results)