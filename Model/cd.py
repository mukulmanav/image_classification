#Data cleaning module( video 3 from playlist)

 #%%
import numpy as np
import cv2
import matplotlib
import matplotlib.pyplot as plt

# %%
img=cv2.imread("../Datasets/maria_sharapova/s1.jpg")
img.shape

# %%
plt.imshow(img)
# %% removing color from pic(converting pic into black and white)
gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
gray.shape
plt.imshow(gray ,cmap='gray')
# %% detecting face by using xml file in opencv folder . this process is haarcascading
face_cascade=cv2.CascadeClassifier('opencv/haarcascades/haarcascade_frontalface_default.xml')
face=face_cascade.detectMultiScale(img,1.3,5)
face
# %% passing the witdth and height of face in variables
(x,y,w,h)=face[0]
x,y,w,h
# %%
face_img=cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
plt.imshow(face_img)
# %% detecting eyes by using eyes cascade
eyes_cascade=cv2.CascadeClassifier('opencv/haarcascades/haarcascade_eye.xml')
cv2.destroyAllWindows()
for (x,y,w,h) in face:
    face_img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
    roi_gray = gray[y:y+h, x:x+w]
    roi_color = face_img[y:y+h, x:x+w]
    eyes = eyes_cascade.detectMultiScale(roi_gray)
    for (ex,ey,ew,eh) in eyes:
        cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
        

plt.figure()
plt.imshow(face_img, cmap='gray')
plt.show()
# %%
plt.imshow(roi_color, cmap='gray')
# %% reads faace and eyes and create a cropped images of Reign of interest
def get_cropped_img_if_2_eyes(img_path):
    img=cv2.imread(img_path)
    gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces=face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eyes_cascade.detectMultiScale(roi_color)
        if len(eyes) >= 2:
            return roi_color 
# %% returns original image
original_image = cv2.imread('../Datasets/maria_sharapova/s1.jpg')
plt.imshow(original_image)
# %%
cropped_image = get_cropped_img_if_2_eyes('../Datasets/maria_sharapova/s1.jpg')
plt.imshow(cropped_image)
# %%
org_image_obstructed = cv2.imread('../Datasets/maria_sharapova/s2.jpg')
plt.imshow(org_image_obstructed)
# %%
cropped_image_no_2_eyes = get_cropped_img_if_2_eyes('../Datasets/maria_sharapova/s2.jpg')
cropped_image_no_2_eyes
# %%
path_to_data = "../Datasets/"
path_to_cr_data = "../Datasets/cropped/"
# %% store all the files in datasets folder in a python list
import os
img_dirs = []
for entry in os.scandir(path_to_data):
    if entry.is_dir():
        img_dirs.append(entry.path)
# %%
img_dirs
# %% if the cropped forlder exists it eill remove it and create it if not exists it wil create it
import shutil
if os.path.exists(path_to_cr_data):
     shutil.rmtree(path_to_cr_data)
os.mkdir(path_to_cr_data)
# %%
cropped_image_dirs = []
celebrity_file_names_dict = {}

for img_dir in img_dirs:   #img dirs is a list contains all the files in Datasets
    count = 1
    celebrity_name = img_dir.split('/')[-1]    #takes the path of file and split it  and takes the name of player
    print(celebrity_name)
    
    celebrity_file_names_dict[celebrity_name] = []
    
    for entry in os.scandir(img_dir):   # iterate through all the photos 
        roi_color = get_cropped_img_if_2_eyes(entry.path)
        if roi_color is not None:   #checks if it has face and eyes
            cropped_folder = path_to_cr_data + celebrity_name 
            if not os.path.exists(cropped_folder):  # if it finds face and eyes it creates a folder with the name of player and move the cropped photo in the folder
                os.makedirs(cropped_folder)
                cropped_image_dirs.append(cropped_folder)
                print("Generating cropped images in folder: ",cropped_folder)
                
            cropped_file_name = celebrity_name + str(count) + ".png"  # naming the cropped photo
            cropped_file_path = cropped_folder + "/" + cropped_file_name 
            
            cv2.imwrite(cropped_file_path, roi_color)
            celebrity_file_names_dict[celebrity_name].append(cropped_file_path)
            count += 1    
# %% Use wavelet transform as a feature for traning our model
# In wavelet transformed image, you can see edges clearly and that can give us clues on various facial features such as eyes, nose, lips etc
import numpy as np
import pywt
import cv2    

def w2d(img, mode='haar', level=1):
    imArray = img
    #Datatype conversions
    #convert to grayscale
    imArray = cv2.cvtColor( imArray,cv2.COLOR_RGB2GRAY )
    #convert to float
    imArray =  np.float32(imArray)   
    imArray /= 255;
    # compute coefficients 
    coeffs=pywt.wavedec2(imArray, mode, level=level)

    #Process Coefficients
    coeffs_H=list(coeffs)  
    coeffs_H[0] *= 0;  

    # reconstruction
    imArray_H=pywt.waverec2(coeffs_H, mode);
    imArray_H *= 255;
    imArray_H =  np.uint8(imArray_H)

    return imArray_H

# %%
cropped_img = np.array(roi_color)
cropped_img.shape
#%%
im_har = w2d(cropped_img,'db1',5)
plt.imshow(im_har, cmap='gray')
# %%
celebrity_file_names_dict = {}
for img_dir in cropped_image_dirs:
    celebrity_name = img_dir.split('/')[-1]
    file_list = []
    for entry in os.scandir(img_dir):
        file_list.append(entry.path)
    celebrity_file_names_dict[celebrity_name] = file_list
celebrity_file_names_dict
# %%
class_dict = {}
count = 0
for celebrity_name in celebrity_file_names_dict.keys():
    class_dict[celebrity_name] = count
    count = count + 1
class_dict
# %%
X, y = [], []
for celebrity_name, training_files in celebrity_file_names_dict.items():
    for training_image in training_files:
        img = cv2.imread(training_image)
        scalled_raw_img = cv2.resize(img, (32, 32))
        img_har = w2d(img,'db1',5)
        scalled_img_har = cv2.resize(img_har, (32, 32))
        combined_img = np.vstack((scalled_raw_img.reshape(32*32*3,1),scalled_img_har.reshape(32*32,1)))
        X.append(combined_img)
        y.append(class_dict[celebrity_name])  
# %%
len(X[0])
# %%
X = np.array(X).reshape(len(X),4096).astype(float)
X.shape
# %% Data cleaning process is done. Now we are ready to train our model

from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

# %%
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

pipe = Pipeline([('scaler', StandardScaler()), ('svc', SVC(kernel = 'rbf', C = 10))])
pipe.fit(X_train, y_train)
pipe.score(X_test, y_test)
# %%
print(classification_report(y_test, pipe.predict(X_test)))
# %%
# Let's use GridSearch to try out different models with different paramets. Goal is to come up with best modle with best fine tuned parameters
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV
# %%
model_params = {
    'svm': {
        'model': svm.SVC(gamma='auto',probability=True),
        'params' : {
            'svc__C': [1,10,100,1000],
            'svc__kernel': ['rbf','linear']
        }  
    },
    'random_forest': {
        'model': RandomForestClassifier(),
        'params' : {
            'randomforestclassifier__n_estimators': [1,5,10]
        }
    },
    'logistic_regression' : {
        'model': LogisticRegression(solver='liblinear',multi_class='auto'),
        'params': {
            'logisticregression__C': [1,5,10]
        }
    }
}
# %%
scores = []
best_estimators = {}
import pandas as pd
for algo, mp in model_params.items():
    pipe = make_pipeline(StandardScaler(), mp['model'])
    clf =  GridSearchCV(pipe, mp['params'], cv=5, return_train_score=False)
    clf.fit(X_train, y_train)
    scores.append({
        'model': algo,
        'best_score': clf.best_score_,
        'best_params': clf.best_params_
    })
    best_estimators[algo] = clf.best_estimator_
    
df = pd.DataFrame(scores,columns=['model','best_score','best_params'])
df
# %%
best_estimators
# %%
best_estimators['svm'].score(X_test,y_test)
# %%
best_estimators['random_forest'].score(X_test,y_test)
# %%
best_estimators['logistic_regression'].score(X_test,y_test)
# %%
best_clf = best_estimators['svm']
# %%
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, best_clf.predict(X_test))
cm
# %%
import seaborn as sn
plt.figure(figsize = (10,7))
sn.heatmap(cm, annot=True)
plt.xlabel('Predicted')
plt.ylabel('Truth')
# %%
class_dict
# %% Save the trained model
import joblib 
# Save the model as a pickle in a file 
joblib.dump(best_clf, 'saved_model.pkl') 
# %% Save class dictionary
import json
with open("class_dictionary.json","w") as f:
    f.write(json.dumps(class_dict))

# %%
