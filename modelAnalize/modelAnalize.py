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

imageSize = 128
numOfTestImages = 100
topk = 2

numOfCategoriesList = [30]
numOfImagesPerCategoryList = [1000]
numOfIterationList = [1,5]
##########################################

class statistics(object):
	logName = str()
	stats = dict()
	confusion_matrix = dict()
	validation_data_len = int()
	

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
				else:
					print 'No need to download images.'
			if (index+1 < len(numOfCategoriesList)) :
				NEXT_WORKING_DIR = WORKING_DIR.split('_')
				NEXT_WORKING_DIR[-2] = str(numOfCategoriesList[index+1])
				NEXT_WORKING_DIR = '_'.join(map(str, NEXT_WORKING_DIR))
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

def	testClassificator(model,numOfCategories,statistic_data):
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
	
	eval_data = model.evaluate(validation_data,metric=['accuracy', 'confusion_matrix'])
	statistic_data.stats['accuracy'] = round(eval_data['accuracy'],2) 
	statistic_data.confusion_matrix = eval_data['confusion_matrix']
	
	return validation_data,class_to_text_map

def testEnviroment(statistic_data):
	for numOfCategories in numOfCategoriesList:
		for numOfImagesPerCategory in numOfImagesPerCategoryList:
			for numOfIteration in numOfIterationList:
				print '#' * 10
				print '# numOfCategories, = %d, numOfImagesPerCategory = %d, numOfIteration = %d' % (numOfCategories,numOfImagesPerCategory,numOfIteration)
				print '#' * 10
				statistic_data.stats['numOfCategories'] = numOfCategories
				statistic_data.stats['numOfImagesPerCategory'] = numOfImagesPerCategory
				statistic_data.stats['numOfIteration'] = numOfIteration
				statistic_data.stats['start_time'] = int(time.time())
				model = createClassificator(numOfCategories,numOfImagesPerCategory,numOfIteration)
				statistic_data.stats['after_classificator_time'] = int(time.time() - statistic_data.stats['start_time'])
				(validation_data,class_to_text_map) = testClassificator(model,numOfCategories,statistic_data)
				statistic_data.stats['after_testClassificator'] = int(time.time() - statistic_data.stats['start_time'])
				modelStatistics(model,validation_data,numOfCategories,numOfImagesPerCategory,numOfIteration,class_to_text_map,statistic_data)
				statistic_data.stats['after_statistic_info'] = int(time.time() - statistic_data.stats['start_time'])
				logFilesIndex()
				logFileStatistics(statistic_data)
				print '\n' * 10
	return (model,validation_data)

def logFilesIndex():
	logList = list()
	for root, dirs, files in os.walk(os.getcwd() + '/AnalizeLogs/'):
		for name in files:
			logList += [{'path':os.path.join(root, name), 'name':(os.path.join(root, name)).split('/')[-1]}]
	
	with open(os.path.normpath('logIndex.txt'),'w+') as logHandle:
		logHandle.write(json.dumps(logList) + '\n')
		
def logFileStatistics(statistic_data):
	if not os.path.exists(os.path.normpath('Statistics')):
		os.makedirs(os.path.normpath('Statistics'))
	
	#fix accuracy values to percent
	for i in range(5):
		statistic_data.stats['acc' + str(i+1)] = round((statistic_data.stats['acc' + str(i+1)] / float(statistic_data.validation_data_len)),2)
	
	with open(os.path.normpath('Statistics/' + statistic_data.logName),'w+') as logHandle:
		logHandle.write('{"data": [\n')
		logHandle.write(json.dumps(statistic_data.stats) + '\n')
		logHandle.write(']}\n')

def predict_image_url(model,path):
	image_sf = gl.SFrame({'image': [gl.Image(path)]})
	image_sf['image'] = gl.image_analysis.resize(image_sf['image'], imageSize, imageSize)
	top_labels = model.predict_topk(image_sf, k=min(topk,5))
	return top_labels
	
	
	
def modelStatistics(model,validation_data,numOfCategories,numOfImagesPerCategory,numOfIteration,class_to_text_map,statistic_data):
	if not os.path.exists(os.path.normpath('AnalizeLogs')):
		os.makedirs(os.path.normpath('AnalizeLogs'))
	if not os.path.exists(os.path.normpath('confusionLogs')):
		os.makedirs(os.path.normpath('confusionLogs'))
	
	manager = ImageNetManager()
	localtime = time.localtime(time.time())
	
	#Set log name "YEAR_MONTH_DAY_HOUR_MINUTE_#CATEGORIES_#IMAGES_#ITERATIONS.log"
	statistic_data.logName = '%d_%d_%d_%d_%d_cat%d_img%d_iter%d.log' % (localtime[0],localtime[1],localtime[2],localtime[3],localtime[4],numOfCategories,numOfImagesPerCategory,numOfIteration)
	
	#Init 2D array for confusion_matrix_raw
	confusion_matrix_raw = [[0 for j in range(numOfCategories)] for i in range(numOfCategories)]

	with open(os.path.normpath('AnalizeLogs/' + statistic_data.logName),'w+') as logHandle:
		logHandle.write('{"data": [\n')
		flag = 0
		flag2 = 0
		
		#init params for accuracy
		statistic_data.validation_data_len = len(validation_data['path'])
		for i in range(5):
			statistic_data.stats['acc' + str(i+1)] = 0
		
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
					statistic_data.stats['acc' + str(row+1)] = 1
					continue
				
				total_so_far += top_labels[row]['score']
				class_seen_so_far.append(top_labels[row]['class'])
				wnid_so_far += [class_to_text_map[str(top_labels[row]['class'])]]
				
				data['Top' + str(row+1)] = round(total_so_far,2)
				data['wnid' + str(row+1)] = str(wnid_so_far)
				if main_row['label'] in class_seen_so_far:
					data['Right' + str(row+1)] = 'YES'
					statistic_data.stats['acc' + str(row+1)] += 1
				else:
					data['Right' + str(row+1)] = 'NO'
			path = main_row['path'].split('/')
			data['Image'] = ('<img src="' + '/' + path[4] + '/' + path[5] + '/' + path[6] + '"height="56" width="56"> ') 
			confusion_matrix_raw[main_row['label']][top_labels[0]['class']] += 1
			
			if flag == 1: 
				logHandle.write(',')
			logHandle.write(json.dumps(data) + '\n')
			flag = 1
		logHandle.write(']}\n')

		#process confusion_matrix_raw data		
		
		with open(os.path.normpath('confusionLogs/' + statistic_data.logName),'w+') as logHandle2:
			logHandle2.write('{"data": [\n')
			for i in range(numOfCategories):
				confusion_matrix = {}
				confusion_matrix['-'] = class_to_text_map[str(i)]
				for j in range(numOfCategories):
					confusion_matrix[class_to_text_map[str(j)]] = confusion_matrix_raw[i][j]
				if flag2 == 1: 
					logHandle2.write(',')
				logHandle2.write(json.dumps(confusion_matrix) + '\n')
				flag2 = 1
			logHandle2.write(']}\n')
		
	return
	
	
if __name__ == '__main__':      
	statistic_data = statistics()
	downloadImages()
	downloadTestImages(numOfTestImages)
	(model,validation_data) = testEnviroment(statistic_data)

	
	