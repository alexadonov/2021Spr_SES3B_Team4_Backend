# Python 3.9
# To retrain, delete pickle.data and model.tflearn files
# After making changes to intents.json, delete pickle.data file
# In Patterns in intents.json, leave out any punctuation

import nltk
import numpy
import tensorflow
import random
import json
import tflearn
import pickle


from re import X
from autocorrect import Speller
from nltk import stem
from nltk.sem.relextract import class_abbrev
from nltk.stem.lancaster import LancasterStemmer
from tensorflow.python.ops.gen_array_ops import shape
from tensorflow.python.ops.gen_batch_ops import batch

stemmer = LancasterStemmer()
with open ("intents.json") as file:
    data = json.load(file)
try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intents in data ["intents"]:
        for pattern in intents["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intents["tag"])

            if intents["tag"] not in labels:
                labels.append(intents["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w not in "?"]
    words = sorted(list(set(words)))
    labels = sorted(labels)
    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]
    [0,0,0,1]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)

    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

# model = tflearn.DNN(net)
try: 
    model = tflearn.DNN(net)
    model.load("model.tflearn")
except:
    model = tflearn.DNN(net)
    model.fit(training, output, n_epoch=10000, batch_size=15, show_metric=True)
    model.save("model.tflearn")

def bag_of_words(s, words):
    bag  = [0 for _ in range(len(words))]
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(words.lower()) for words in s_words]

    for se in s_words:
        for i, w in enumerate(words): 
            if w == se:
                bag[i] = 1

    return numpy.array(bag)

def chat():
    print("Axel Bot here, Here to Help(type quit to stop)")
    while True: 
        inp = input("You: ")
        if inp.lower() == "quit":
            break

        # Spell checker
        spell = Speller(lang='en')
        print("Original: " + inp)
        inp = spell(inp)
        print("Altered: " + inp)

        results = model.predict([bag_of_words(inp.lower(), words)])[0]
        results_index = numpy.argmax(results)
        tag = labels[results_index]
        print(results)
       
        if results[results_index] > 0.6:
            for tg in data["intents"]:
                if tg['tag'] == tag:
                    responses = tg['responses']
            print(random.choice(responses)) 
        else:
            print("I did not get that. Please Try Again")      
chat()