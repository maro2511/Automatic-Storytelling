from ImageNetManager import *
import shutil
import errno
import time
import graphlab as gl
import json
import time


##########################################
#           Configuration                #
##########################################
wordnetIdList = ['n09918554','n02336641','n13083586','n09381242','n07697537']
#n09918554 = child
#n02336641 = mouse
#n13083586 = plant
#n09381242 = rock / mountain
#n07697537 = hotdog

imageSize = 64
numOfTestImages = 100
topk = 5

numOfCategoriesList = [5]
numOfImagesPerCategoryList = [1000]
numOfIterationList = [1,3]
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
					print 'a'
					urlList = manager.getImagesUrlByWordNetId(id)
					print 'b'
					manager.downloadImagesForId(id,urlList,WORKING_DIR,limit = numOfImagesPerCategory)			
					print 'c'
				else:
					print 'No need to download images.'
			if (index+1 < len(numOfCategoriesList)) :
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
		WORKING_DIR = os.getcwd() + '/TEST_IMAGES_%d' % (numOfCategories)
		for id in requestedIds:
			if not os.path.exists(os.path.normpath(WORKING_DIR +'/'+ str(id))):
				urlList = manager.getImagesUrlByWordNetId(id)
				manager.downloadImagesForId(id,urlList[::-1],WORKING_DIR,limit = numberOfTestImages)

def createClassificator(numOfCategories,numOfImagesPerCategory,numOfIteration):
	WORKING_DIR = os.getcwd() + '/IMAGES_%d_%d' % (numOfCategories,numOfImagesPerCategory)
	print WORKING_DIR
	train_sf = gl.image_analysis.load_images(WORKING_DIR, random_order=True)
	train_sf['wnid'] = train_sf['path'].apply(lambda x: x.split('/')[-2])
	train_sf['image'] = gl.image_analysis.resize(train_sf['image'], imageSize, imageSize)
	
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
	manager = ImageNetManager()
	
	validation_data = gl.image_analysis.load_images(WORKING_DIR, random_order=True)
	validation_data['wnid'] = validation_data['path'].apply(lambda x: x.split('/')[-2])
	validation_data['image'] = gl.image_analysis.resize(validation_data['image'], imageSize, imageSize)
		
	unique_labels = validation_data['wnid'].unique().sort()                                              
	class_map = {}
	class_to_text_map = {}
	for i in range(len(unique_labels)):                                                        
		class_map[unique_labels[i]] = i
		class_to_text_map[str(i)] = manager.getNamebyWordNetId(unique_labels[i])
	validation_data['label'] = validation_data['wnid'].apply(lambda x: class_map[x])
	
	print model.evaluate(validation_data)
	return validation_data,class_to_text_map

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
				(validation_data,class_to_text_map) = testClassificator(model,numOfCategories)
				after_testClassificator = int(time.time() - start_time)
				statistic_info = modelStatistics(model,validation_data,numOfCategories,numOfImagesPerCategory,numOfIteration,class_to_text_map)
				after_statistic_info = int(time.time() - start_time)
				result.append((numOfCategories,numOfImagesPerCategory,numOfIteration,start_time,after_classificator_time,after_testClassificator,after_statistic_info))
				logFilesIndex()
				print '\n' * 10
	return (model,result,validation_data)

def logFilesIndex():
	logList = list()
	for root, dirs, files in os.walk(os.getcwd() + '/AnalizeLogs/'):
		for name in files:
			logList += [{'path':os.path.join(root, name), 'name':(os.path.join(root, name)).split('/')[-1]}]
	
	with open(os.path.normpath('logIndex.txt'),'w+') as logHandle:
		logHandle.write(json.dumps(logList) + '\n')
		

def printTimeResults(results):
	print '#' * 10
	print '# RESULTS!	'
	print '#' * 10
	for item in results:
		print 'numOfCategories = %d ,numOfImagesPerCategory = %d ,numOfIteration = %d ,start_time = %d ,after_classificator_time = %d ,after_testClassificator = %d, after_statistic_info = %d' % item
		print '#'
	print '###'

def predict_image_url(model,path):
	image_sf = gl.SFrame({'image': [gl.Image(path)]})
	image_sf['image'] = gl.image_analysis.resize(image_sf['image'], imageSize, imageSize)
	top_labels = model.predict_topk(image_sf, k=min(topk,5))
	return top_labels
	
	
	
def modelStatistics(model,validation_data,numOfCategories,numOfImagesPerCategory,numOfIteration,class_to_text_map):
	if not os.path.exists(os.path.normpath('AnalizeLogs')):
		os.makedirs(os.path.normpath('AnalizeLogs'))
	
	manager = ImageNetManager()
	localtime = time.localtime(time.time())
	logName = '%d_%d_%d_%d_%d_cat%d_img%d_iter%d.log' % (localtime[0],localtime[1],localtime[2],localtime[3],localtime[4],numOfCategories,numOfImagesPerCategory,numOfIteration)
	with open(os.path.normpath('AnalizeLogs/' + logName),'w+') as logHandle:
		logHandle.write('{"data": [\n')
		flag = 0
		for main_row in validation_data:
			top_labels = predict_image_url(model,main_row['path'])
			
			data = dict()
			class_seen_so_far = list()
			total_so_far = 0
			wnid_so_far = []
			for row in range(5):
				if row >= min(topk,5):
					data['Top' + str(row+1)] = 1
					data['Right' + str(row+1)] = '-'
					data['wnid' + str(row+1)] = '-'
					continue
					
				total_so_far += top_labels[row]['score']
				class_seen_so_far.append(top_labels[row]['class'])
				wnid_so_far += [class_to_text_map[str(top_labels[row]['class'])]]
				
				data['Top' + str(row+1)] = round(total_so_far,2)
				data['wnid' + str(row+1)] = str(wnid_so_far)
				if main_row['label'] in class_seen_so_far:
					data['Right' + str(row+1)] = 'YES'
				else:
					data['Right' + str(row+1)] = 'NO'
			path = main_row['path'].split('/')
			data['Image'] = ('<img src="' + '/' + path[4] + '/' + path[5] + '/' + path[6] + '"height="56" width="56"> ') 
			if flag == 1: 
				logHandle.write(',')
			logHandle.write(json.dumps(data) + '\n')
			flag = 1
		logHandle.write(']}\n')
	
	return
	
	
if __name__ == '__main__':      
	downloadImages()
	downloadTestImages(numOfTestImages)
	(model,result,validation_data) = testEnviroment()
	#printTimeResults(results)
	
	