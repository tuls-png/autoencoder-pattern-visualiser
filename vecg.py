import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from keract import get_activations, display_activations
from keras import layers, losses
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import accuracy_score, recall_score, roc_curve
from sklearn.model_selection import train_test_split
from keras.models import Model


df = pd.read_csv('lmao2.csv', header=None)
raw_data = df.values
df.head()

# Now we will separate the data and labels so that it will be easy for us
data = raw_data[:, 0:-1]
print(len(data))
labels = raw_data[:, -1]
print("data",data)
print("labels",labels)
print('Number of data: ',len(data))
print('Number of labels: ',len(labels ))
train_data, test_data, train_labels, test_labels = train_test_split(data, labels, test_size=0.19, random_state=0)
print('train_labels',train_labels)
print("testlabel",test_labels)


min = tf.reduce_min(train_data)
max = tf.reduce_max(train_data)

# Now we will use the formula (data - min)/(max - min)
train_data = (train_data - min) / (max - min)
test_data = (test_data - min) / (max - min)

# I have converted the data into float
train_data = tf.cast(train_data, dtype=tf.float32)
test_data = tf.cast(test_data, dtype=tf.float32)


# The labels are either 0 or 1, so I will convert them into boolean(true or false)
train_labels = train_labels.astype(bool)
test_labels = test_labels.astype(bool)
print("train_labels",train_labels)
print("test_labels",test_labels)
# Now let's separate the data for normal ECG from that of abnormal ones
# Normal ECG data

n_train_data = train_data[train_labels]
n_test_data = test_data[test_labels]
print(' ')
print('---------------------')
print("n_train_data:\n",n_train_data, len(n_train_data))
print(' ')
print("n_test_data:\n",n_test_data)
print(' ')
print("Normal Train Data:\n",n_train_data)
print(' ')
print("Normal Test Data:\n",n_test_data)
# Abnormal ECG data
an_train_data = train_data[~train_labels]
an_test_data = test_data[~test_labels]
print(' ')
print('---------------------')
print("an_train_data:\n",an_train_data, len(an_train_data))
print(' ')
print("an_test_data:\n",an_test_data)
print(' ')
print("Abnormal Train Data:\n",an_train_data)
print(' ')
print("Abnormal Test Data:\n",an_test_data)

# Lets plot a normal ECG
plt.plot(np.arange(187), n_train_data[7])
plt.grid()
plt.title('Normal ECG')
plt.show()

# Lets plot one from abnormal ECG
plt.plot(np.arange(187), an_train_data[0])
plt.grid()
plt.title('Abnormal ECG')
plt.show()




class detector(Model):
    def __init__(self):
        super(detector, self).__init__()
        self.encoder = tf.keras.Sequential([
            layers.Dense(32, activation='relu'),
            layers.Dense(16, activation='relu'),
            layers.Dense(8, activation='relu')
        ])
        self.decoder = tf.keras.Sequential([
            layers.Dense(16, activation='relu'),
            layers.Dense(32, activation='relu'),
            layers.Dense(187, activation='sigmoid')
        ])

    def call(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded


# Let's compile and train the model!!
autoencoder = detector()
autoencoder.compile(optimizer='adam', loss='mae')
history = autoencoder.fit(n_train_data, n_train_data, epochs=100, batch_size=512, validation_data=(test_data, test_data))
plt.plot(history.history["loss"], label="Training Loss")
plt.plot(history.history["val_loss"], label="Validation Loss")
plt.show()


# Now let's define a function in order to plot the original ECG and reconstructed ones and also show the error
def plot(data, n):
    enc_img = autoencoder.encoder(data)
    dec_img = autoencoder.decoder(enc_img)
    plt.plot(data[n], 'b')
    plt.plot(dec_img[n], 'r')
    plt.fill_between(np.arange(187), data[n], dec_img[n], color='lightcoral')
    plt.legend(labels=['Input', 'Reconstruction', 'Error'])
    plt.show()

print(' ')
print('---------------------')
print("n_test_data, 0")
plot(n_test_data, 0)

reconstructed = autoencoder.predict(n_train_data)
train_loss = tf.keras.losses.mae(reconstructed, n_train_data)

originalthresh = np.mean(train_loss) + np.std(train_loss)
print(' ')
print('---------------------')
print(f'Threshold: {originalthresh}')

reconstructed = autoencoder.predict(an_test_data)
test_loss = tf.keras.losses.mae(reconstructed, an_test_data)

plt.hist(train_loss[None,:], bins=50, label='Train', alpha=0.7, edgecolor='red')
plt.hist(test_loss[None,:], bins=50, label='Test', alpha=0.7, edgecolor='yellow')
plt.xlabel("Loss")
plt.ylabel("Number of examples")
plt.legend()
plt.show()


print("an_test_data, 0")
plot(an_test_data, 0)
print("an_test_data, 1")
plot(an_test_data, 1)
print("an_test_data, 2")
plot(an_test_data, 2)


x=[0.75, 0.78, 0.8, 0.82, 0.84, 0.86, 0.88, 0.9, 0.92, 0.94, 0.96, 0.98, 1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4,2.6, 2.8, 3]

print(' ')
print('---------------------')
print(f'Threshold List: {x}')
thresh=[]
for i in range (len(x)):
    t = np.mean(train_loss) + (np.std(train_loss))*x[i]
    print(f'For {x[i]}:')
    print("Threshold", t)
    thresh.append(t)
print(' ')
print('Number of test data: ',len(test_labels))

def predict(model, data, threshold):
  reconstructions = model(data)
  loss = tf.keras.losses.mae(reconstructions, data)
  return tf.math.less(loss, threshold)

accur=[]

def print_stat(predictions, labels):
    lol=accuracy_score(labels, predictions) * 100
    accur.append(lol)
    fp = 0
    fn = 0
    tp = 0
    tn = 0

    print(' ')
    print('---------------------')
    print("Accuracy in terms of numbers = {}".format(round(accuracy_score(labels, predictions, normalize=False))))
    print("Accuracy in terms of percentage = {}%".format(lol))

    print("Recall = {}".format(recall_score(labels, predictions)))
    if labels[i] == True and predictions[i] == False:
        fp += 1
    if labels[i] == False and predictions[i] == True:
        fn += 1
    if labels[i] == True and predictions[i] == True:
        tn += 1
    if labels[i] == False and predictions[i] == False:
        tp += 1
    print('Actual Sample: Normal, Predicted Sample: Abnormal \n False Positive: ', fp)
    print('Actual Sample: Abnormal, Predicted Sample: Normal \n False Negative: ', fn)
    print('Actual Sample: Normal, Predicted Sample: Normal \n True Positive: ', tp)
    print('Actual Sample: Abnormal, Predicted Sample: Abnormal \n True Negative: ', tn)


def print_stats(predictions, labels):
    l=[]
    p=[]
    fp = 0
    fn = 0
    tp=0
    tn=0
    print('Current threshold: ', t)
    for i in range(len(labels)):
        l.append(labels[i])
        p.append(predictions[i])

        print("-------------------------------")
        print(f'For {i+1} sample:')
        if l[i]==True and p[i]==True:
            print('Actual: Normal')
            print('Prediction: Normal')
        elif l[i]==True and p[i]==False:
            print('Actual: Normal')
            print('Prediction: Abnormal')
        elif l[i]==False and p[i]==True:
            print('Actual: Abnormal')
            print('Prediction: Normal')
        elif l[i]==False and p[i]==False:
            print('Actual: Abnormal')
            print('Prediction: Abnormal')
        if l[i]==p[i]:
            print('The prediction is correct.')
        else:
            print('The prediction is incorrect.')
        if l[i]==True and p[i]==False:
            fp+=1
        if l[i]==False and p[i]==True:
            fn+=1
        if l[i]==True and p[i]==True:
            tn+=1
        if l[i]==False and p[i]==False:
            tp+=1

    print(" ")
    print(f'For {len(labels)} sample:')
    print("Accuracy in terms of numbers = {}".format(round(accuracy_score(l, p, normalize=False))))
    print("Accuracy in terms of percentage = {}%".format((accuracy_score(l, p))*100))

    print("Recall = {}".format(recall_score(l, p)))
    print('Actual Sample: Normal, Predicted Sample: Abnormal \n False Positive: ', fp)
    print('Actual Sample: Abnormal, Predicted Sample: Normal \n False Negative: ', fn)
    print('Actual Sample: Normal, Predicted Sample: Normal \n True Positive: ', tp)
    print('Actual Sample: Abnormal, Predicted Sample: Abnormal \n True Negative: ', tn)


for i in range(len(thresh)):
    preds = predict(autoencoder, test_data, thresh[i])
    print(" ")
    print("--------------------------------------------")
    print(f'For threshold value: {thresh[i]}: ')
    print_stat(preds, test_labels)

print('!!!!!!!!!!!!!!!!!!!!!!!!!!')
print('Threshold List:')
print(thresh)
print('Accuracy List:')
print(accur)

plt.plot(thresh, accur)
plt.xlabel('Threshold value')
# naming the y axis
plt.ylabel('Accuracy')
plt.show()

print('     ')
print_stats(preds, test_labels)


model = LogisticRegression(solver='lbfgs')
model.fit(train_data, train_labels)
# predict probabilities
yhat = model.predict_proba(test_data)
# keep probabilities for the positive outcome only
yhat = yhat[:, 1]
# calculate roc curves
fpr, tpr, thresholds = roc_curve(test_labels, yhat)
# calculate the g-mean for each threshold
gmeans = np.sqrt(tpr * (1-fpr))
# locate the index of the largest g-mean
ix = np.argmax(gmeans)
print('Best Threshold=%f, G-Mean=%.3f' % (thresholds[ix], gmeans[ix]))
# plot the roc curve for the model
plt.plot([0,1], [0,1], linestyle='--', label='No Skill')
plt.plot(fpr, tpr, marker='.', label='Logistic')
plt.scatter(fpr[ix], tpr[ix], marker='o', color='black', label='Best')
# axis labels
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend()
# show the plot
plt.show()

preds = predict(autoencoder, test_data, thresholds[ix])
print(thresholds[ix])
print(len(preds), len(test_labels))
print_stats(~preds, ~test_labels)

'''
#Now we display our activations
number = int(input("Enter the amount of data you would like to see:"))
for i in range(number):
    data = test_data[i:i + 1]
    activations = get_activations(autoencoder.encoder, data, nodes_to_evaluate=None, layer_names="dense_2",
                                  output_format='simple', nested=False, auto_compile=True)
    with open("allactivationrecord.txt", 'a') as f:
        for key, value in activations.items():
            f.write(" ------------------------\n \n")
            f.write(f'Activation Value of  Image{i + 1}:\n')
            f.write('%s:%s\n' % (key, value))
    display_activations(activations, cmap=None, save=False, fig_size=(30, 30))
    display_activations(activations, cmap="Dark2", save=True, directory=f'Images/Image{i + 1}')
f.close()
fig = plt.figure(figsize=(10, 100))
# setting values to rows and column variables
rows = 3
columns = number // 2
# reading images
for i in range(number):
    Img1 = cv.imread(f'Images/Image{i + 1}/0_dense_2.png')
    fig.add_subplot(rows, columns, i + 1)
    plt.title(f"Image{i + 1}")
    plt.imshow(Img1)
    plt.axis('off')
plt.show()
antest = []
ntest =[]
datanumber = int(input("Enter sample size:"))
for i in range(datanumber):
    an = an_test_data[i:i + 1]
    n = n_test_data[i:i + 1]
    activations = get_activations(autoencoder.encoder, an, layer_names='dense_2', nodes_to_evaluate=None,
                                  output_format='simple', nested=False, auto_compile=True)
    print('--------------')
    print("Activation 1/ Abnormal")
    print(activations)
    print('--------------')
    activations2 = get_activations(autoencoder.encoder, n, layer_names='dense_2', nodes_to_evaluate=None,
                                  output_format='simple', nested=False, auto_compile=True)
    print("Activation 2/ Normal")
    print(activations2)
    print('--------------')
    with open("activation_record.txt", 'a') as f:
        for key, value in activations.items():
            f.write(" ------------------------\n \n")
            f.write(f'Activation Value of  Image{i+1}:\n')
            f.write('%s:%s\n' % (key, value))
    f.close()
    antest.append(activations['dense_2'][0])
    ntest.append(activations2['dense_2'][0])
    #display_activations(activations, cmap="Dark2", save=False, fig_size=(50, 50))
    #display_activations(activations, cmap="Dark2", save=True, directory=f'Images/Image{i + 1}')
antest1 = []
ntest1 =[]
node=int(input('Enter node number:'))
for i in range(len(antest)):
    antest1.append(antest[i][node-1])
    ntest1.append(ntest[i][node-1])
print(f"The activation values of {node} node for {datanumber} abnormal samples are: ")
print(antest1)
print(" ")
print(f"The activation values of {node} node for {datanumber} normal samples are: ")
print(ntest1)
barWidth = 0.15
fig = plt.subplots(figsize=(12, 8))
br1 = np.arange(1, len(antest1)+1)
br2 = [x + barWidth for x in br1]
plt.bar(br1, antest1, color='r', width=barWidth,
        edgecolor='grey', label='Abnormal Test Data')
plt.bar(br2, ntest1, color ='g', width = barWidth,
        edgecolor ='grey', label ='Normal Test Data')
plt.xlabel('Sample Number', fontsize=15)
plt.ylabel('Activation Value', fontsize=15)
plt.xticks(np.arange(1, len(antest1)+1))
plt.legend()
plt.show()
'''
