from ImageDatabase import *
#from Classifier import *

if __name__ == '__main__':
    ##########################################
    #           Configuration                #
    ##########################################
    wordnetIdList = ['n09918554', 'n02336641', 'n09381242', 'n07697537', "n00446980", "n02687992",
                     "n00449295", "n00440747", "n02946921", "n09217230", "n02110341", "n02087122", "n12985857",
                     "n07727868", "n04079244", "n10129825", "n06359193", "n06267145", "n04217882", "n02958343",
                     "n02883344", "n03346455", "n03147509", "n04555897", "n02818832", "n07575726", "n09247410",
                     "n02942699", "n07679356", "n07929519"]

    imageSize = 64
    numOfTestImages = 100
    topk = 3

    numOfCategoriesList = [3]
    numOfImagesPerCategoryList = [50]
    numOfIterationList = [1]

    DATABASE_DIRECTORY = os.getcwd() + '/IMAGE_DATABASE'
    ##########################################

    imageDB = ImageDatabase(DATABASE_DIRECTORY)
    #classifier = Classifier(imageDB)
    imageDB.createImageEnviroment(wordnetIdList,3,10)

    #for numOfCategories in numOfCategoriesList:
        #for numOfImagesPerCategory in numOfImagesPerCategoryList:
            #imageDB.createImageEnviroment(wordnetIdList,numOfCategories,numOfImagesPerCategory)
            #for numOfIteration in numOfIterationList:
                #classifier.create(numOfCategories,numOfImagesPerCategory,numOfIteration,imageSize)
                #classifier.testModel()
                #classifier.statistics(numOfCategories,topk,imageSize)
                #classifier.createLogFileIndex()
                #classifier.dumpStatisticsToLogFile()
