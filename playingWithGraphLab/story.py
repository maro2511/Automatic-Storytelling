import graphlab as gl

WORKING_DIR = '/home/ubuntu/Automatic-Storytelling'
IMAGES_DIR = WORKING_DIR + '/Images'

train_sf = gl.image_analysis.load_images(IMAGES_DIR, random_order=True)
train_sf['wnid'] = train_sf['path'].apply(lambda x: x.split('/')[-2])
train_sf['image'] = gl.image_analysis.resize(train_sf['image'], 256, 256)
train_sf.save(WORKING_DIR + '/sframe/train_shuffle')
train_sf = gl.SFrame(WORKING_DIR + '/sframe/train_shuffle')
train_sf.head()

train, validation_data = train_sf.random_split(0.8)

###### Make a mapping from string to integer labels

# In[ ]:

unique_labels = train['wnid'].unique().sort()                                              
class_map = {}                                                                  
for i in range(len(unique_labels)):                                                        
    class_map[unique_labels[i]] = i                                                        
train['label'] = train['wnid'].apply(lambda x: class_map[x])

# Save the mapping so that we can use it later when building customized classifier
import pickle
pickle.dump(class_map, file(WORKING_DIR + '/wnid_to_label.pkl', 'w'))

mean_image = train['image'].mean()
gl.SArray([mean_image]).save(WORKING_DIR + '/sframe/mean_image')
mean_image = gl.SArray(WORKING_DIR + '/sframe/mean_image')[0]

net = gl.deeplearning.get_builtin_neuralnet('imagenet')
net.layers[22].num_hidden_units=3              # number of wordnetid
net

m = gl.neuralnet_classifier.create(train[['image', 'label']],                      
                                   target='label',
                                   network=net,                                    
                                   mean_image=mean_image,                          
                                   metric=['accuracy','recall@1'],                 
                                   max_iterations=35,                              
                                   model_checkpoint_path=WORKING_DIR + '/result/model_checkpoint',
                                   model_checkpoint_interval=5,                    
                                   batch_size=150)

#recall@ need to be small than num of wordnet ids								   
wnid_to_text_sf = gl.SFrame.read_csv('http://image-net.org/archive/words.txt', delimiter='\t', header=False)
wnid_to_text_sf

wnid_to_text = dict((int(row['X1'][1:]), row['X2']) for row in wnid_to_text_sf)
wnid_to_label = pickle.load(file('wnid_to_label.pkl'))
label_to_text = dict((label, wnid_to_text[wnid]) for (wnid, label) in wnid_to_label.iteritems())
label_to_text

model = gl.load_model(WORKING_DIR + '/result/model_checkpoint')

model.evaluate(validation_data)

