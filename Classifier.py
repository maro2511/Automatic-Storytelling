from ImageDatabase import *
import shutil
import errno
import time
import graphlab as gl
import json
import time

class statistics(object):
    logName = str()
    stats = dict()
    confusion_matrix = dict()

class Classifier():
    def __init__(self,_imageDB):
        self.statistic_data = statistics()
        self.imageDB = _imageDB
        self.class_to_text_map = dict()

    def create(self,numOfCategories,numOfImagesPerCategory,numOfIteration,imageSize):
        print '#' * 10
        print '# ~~ CREATE CLASSIFIER ~~'
        print '# numOfCategories, = %d, numOfImagesPerCategory = %d, numOfIteration = %d' % (numOfCategories,numOfImagesPerCategory,numOfIteration)
        print '#' * 10

        # Save statistics information
        self.statistic_data.stats['numOfCategories'] = numOfCategories
        self.statistic_data.stats['numOfImagesPerCategory'] = numOfImagesPerCategory
        self.statistic_data.stats['numOfIteration'] = numOfIteration
        self.statistic_data.stats['start_time'] = int(time.time())

        #Set log name "YEAR_MONTH_DAY_HOUR_MINUTE_#CATEGORIES_#IMAGES_#ITERATIONS.log"
        localtime = time.localtime(time.time())
        self.logName = '%d_%d_%d_%d_%d_cat%d_img%d_iter%d.log' % (localtime[0],localtime[1],localtime[2],localtime[3],localtime[4],numOfCategories,numOfImagesPerCategory,numOfIteration)

        #Load images
        WORKING_DIR = os.getcwd() + '/IMAGES_%d_%d' % (numOfCategories,numOfImagesPerCategory)
        train_sf = gl.image_analysis.load_images(WORKING_DIR, random_order=True)

        # The path looks like '.../n1440764/n01440764_10026.JPEG'
        # The lambda function extracts the wordnet_id 'n01440764' from the path
        train_sf['wnid'] = train_sf['path'].apply(lambda x: x.split('/')[-2])

        #resize images
        train_sf['image'] = gl.image_analysis.resize(train_sf['image'], imageSize, imageSize)

        # Make a mapping from string to integer labels
        unique_labels = train_sf['wnid'].unique().sort()
        class_map = {}
        class_to_text_map = {}
        for i in range(len(unique_labels)):
            class_map[unique_labels[i]] = i
            self.class_to_text_map[str(i)] = self.imageDB.getNamebyWordNetId(unique_labels[i])
        train_sf['label'] = train_sf['wnid'].apply(lambda x: class_map[x])

        # Split the set (90% for train, 10% for validation and statistics)
        train_set, validation = train_sf.random_split(0.9)
        self.validation_set = validation

        print train_set

        mean_image = train_set['image'].mean()

        self.model = gl.neuralnet_classifier.create(train_sf[['image', 'label']],
                                                  target='label',
                                                  mean_image=mean_image,
                                                  max_iterations=numOfIteration,
                                                  batch_size=int(numOfImagesPerCategory/10))
        return

    def testModel(self):
        eval_data = self.model.evaluate(self.validation_set,metric=['accuracy', 'confusion_matrix'])
        self.statistic_data.stats['accuracy'] = round(eval_data['accuracy'],2)
        self.statistic_data.confusion_matrix = eval_data['confusion_matrix']

    #TODO: remove input parameters (replace with self)
    def statistics(self,numOfCategories,topk,imageSize):
        if not os.path.exists(os.path.normpath('AnalizeLogs')):
            os.makedirs(os.path.normpath('AnalizeLogs'))
        if not os.path.exists(os.path.normpath('confusionLogs')):
            os.makedirs(os.path.normpath('confusionLogs'))

        #Init 2D array for confusion_matrix_raw
        confusion_matrix_raw = [[0 for j in range(numOfCategories)] for i in range(numOfCategories)]
        self.statistic_data.validation_data_len = len(self.validation_set['path'])

        with open(os.path.normpath('AnalizeLogs/' + self.logName),'w+') as logHandle:
            logHandle.write('{"data": [\n')
            flag = 0
            flag2 = 0

            #init params for accuracy
            for i in range(5):
                self.statistic_data.stats['acc' + str(i+1)] = 0

            for main_row in self.validation_set:
                top_labels = self.predict_image_url(main_row['path'],imageSize,topk)

                data = dict()
                class_seen_so_far = list()
                total_so_far = 0
                wnid_so_far = []
                for row in range(5):
                    if row >= min(topk,5):
                        data['Top' + str(row+1)] = 1
                        data['Right' + str(row+1)] = '-'
                        data['wnid' + str(row+1)] = '-'
                        self.statistic_data.stats['acc' + str(row+1)] = 1
                        continue

                    total_so_far += top_labels[row]['score']
                    class_seen_so_far.append(top_labels[row]['class'])
                    wnid_so_far += [self.class_to_text_map[str(top_labels[row]['class'])]]

                    data['Top' + str(row+1)] = round(total_so_far,2)
                    data['wnid' + str(row+1)] = str(wnid_so_far)
                    if main_row['label'] in class_seen_so_far:
                        data['Right' + str(row+1)] = 'YES'
                        self.statistic_data.stats['acc' + str(row+1)] += 1
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

            with open(os.path.normpath('confusionLogs/' + self.logName),'w+') as logHandle2:
                logHandle2.write('{"data": [\n')
                for i in range(numOfCategories):
                    confusion_matrix = dict()
                    confusion_matrix['-'] = self.class_to_text_map[str(i)]
                    for j in range(numOfCategories):
                        confusion_matrix[self.class_to_text_map[str(j)]] = confusion_matrix_raw[i][j]
                    if flag2 == 1:
                        logHandle2.write(',')
                    logHandle2.write(json.dumps(confusion_matrix) + '\n')
                    flag2 = 1
                logHandle2.write(']}\n')

        self.statistic_data.stats['after_statistic_info'] = int(time.time() - self.statistic_data.stats['start_time'])
        return

    def predict_image_url(self,path,imageSize,topk):
        image_sf = gl.SFrame({'image': [gl.Image(path)]})
        image_sf['image'] = gl.image_analysis.resize(image_sf['image'], imageSize, imageSize)
        top_labels = self.model.predict_topk(image_sf, k=min(topk,5))
        return top_labels

    def createLogFileIndex(self):
        logList = list()
        for root, dirs, files in os.walk(os.getcwd() + '/AnalizeLogs/'):
            for name in files:
                logList += [{'path':os.path.join(root, name), 'name':(os.path.join(root, name)).split('/')[-1]}]

            with open(os.path.normpath('logIndex.txt'),'w+') as logHandle:
                logHandle.write(json.dumps(logList) + '\n')

    #TODO: #fix accuracy values to percent
    def dumpStatisticsToLogFile(self):
        if not os.path.exists(os.path.normpath('Statistics')):
            os.makedirs(os.path.normpath('Statistics'))

            for i in range(5):
                self.statistic_data.stats['acc' + str(i+1)] = round((self.statistic_data.stats['acc' + str(i+1)] / float(self.statistic_data.validation_data_len)),2)

            with open(os.path.normpath('Statistics/' + self.logName),'w+') as logHandle:
                logHandle.write('{"data": [\n')
                logHandle.write(json.dumps(self.statistic_data.stats) + '\n')
                logHandle.write(']}\n')
