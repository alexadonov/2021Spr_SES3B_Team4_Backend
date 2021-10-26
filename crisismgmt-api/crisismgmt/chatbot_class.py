# Python 3.9
# To retrain, delete pickle.data and model.tflearn files
# After making changes to intents.json, delete pickle.data file
# In Patterns in intents.json, leave out any punctuation

import pandas as pd
import pyspark.sql.functions as F
import numpy
import random
import json
import sparknlp
import tflearn
import pickle
import nltk
import breathing

from autocorrect import Speller
from sparknlp.annotator import *
from sparknlp.base import *
from pyspark.ml import Pipeline
from nltk.stem.lancaster import LancasterStemmer
#from google_speech import Speech



class ChatBot:
    """ChatBot class for automated messaging 
    and responses using machine learning"""

    def __init__(self):
        self.spell = Speller(lang='en')
        self.spark = sparknlp.start()
        self.MODEL_NAME='classifierdl_use_emotion'
        self.initialise_pipeline()
        self.empty_df = self.spark.createDataFrame([['']]).toDF("text")
        self.stemmer = LancasterStemmer()
        self.initialise_dataset()
        self.initialise_model()
        self.misunderstoodCount = 0
        self.negativeEmotionCount = 0
        self.countThresh = 3
        self.panicFlag = False

    def initialise_pipeline(self):
        documentAssembler = DocumentAssembler()\
            .setInputCol("text")\
            .setOutputCol("document")
        use = UniversalSentenceEncoder.pretrained(name="tfhub_use", lang="en")\
            .setInputCols(["document"])\
            .setOutputCol("sentence_embeddings")
        sentimentdl = ClassifierDLModel.pretrained(name=self.MODEL_NAME)\
            .setInputCols(["sentence_embeddings"])\
            .setOutputCol("sentiment")
        self.nlpPipeline = Pipeline(
            stages = [
                documentAssembler,
                use,
                sentimentdl
            ])

    def initialise_dataset(self):
        with open ("intents.json") as file:
            self.intents_data = json.load(file)
        try:
            with open("data.pickle", "rb") as f:
                self.words, self.labels, self.training, self.output = pickle.load(f)
        except:
            self.words = []
            self.labels = []
            self.docs_x = []
            self.docs_y = []

            for intents in self.intents_data["intents"]:
                for pattern in intents["patterns"]:
                    wrds = nltk.word_tokenize(pattern)
                    self.words.extend(wrds)
                    self.docs_x.append(wrds)
                    self.docs_y.append(intents["tag"])

                    if intents["tag"] not in self.labels:
                        self.labels.append(intents["tag"])

            self.words = [self.stemmer.stem(w.lower()) for w in self.words if w not in "?"]
            self.words = sorted(list(set(self.words)))
            self.labels = sorted(self.labels)
            self.training = []
            self.output = []

            out_empty = [0 for _ in range(len(self.labels))]
            [0,0,0,1]

            for x, doc in enumerate(self.docs_x):
                bag = []

                wrds = [self.stemmer.stem(w) for w in doc]

                for w in self.words:
                    if w in wrds:
                        bag.append(1)
                    else:
                        bag.append(0)

                output_row = out_empty[:]
                output_row[self.labels.index(self.docs_y[x])] = 1

                self.training.append(bag)
                self.output.append(output_row)

            training = numpy.array(self.training)
            output = numpy.array(self.output)

            with open("data.pickle", "wb") as f:
                pickle.dump((self.words, self.labels, self.training, self.output), f)


    def initialise_model(self):
        net = tflearn.input_data(shape=[None, len(self.training[0])])
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, len(self.output[0]), activation="softmax")
        net = tflearn.regression(net)
        try: 
            self.model = tflearn.DNN(net)
            self.model.load("model.tflearn")
        except:
            self.model = tflearn.DNN(net)
            self.model.fit(self.training, self.output, n_epoch=5000, batch_size=8, show_metric=True)
            self.model.save("model.tflearn")

    def bag_of_words(self, message):
        bag  = [0 for _ in range(len(self.words))]
        s_words = nltk.word_tokenize(message)
        s_words = [self.stemmer.stem(words.lower()) for words in s_words]

        for se in s_words:
            for i, w in enumerate(self.words): 
                if w == se:
                    bag[i] = 1

        return numpy.array(bag)

    def predict_response(self, corrected_message):

        output = []

        results = self.model.predict([self.bag_of_words(corrected_message.lower())])[0]
        results_index = numpy.argmax(results)
        tag = self.labels[results_index]
        # print(results)
       
        if results[results_index] > 0.8:
            for tg in self.intents_data["intents"]:
                if tg['tag'] == tag:
                    val = random.choice(tg['responses'])
                    responses = tg['responses']
                    responses = tg['responses']
            output.append(random.choice(responses))
        
            # emotions thinking
            pipelineModel = self.nlpPipeline.fit(self.empty_df)
            df = self.spark.createDataFrame(pd.DataFrame({"text":[corrected_message]}))
            result = pipelineModel.transform(df)
            result.select(F.explode(F.arrays_zip('document.result', 'sentiment.result')).alias("cols")) \
            .select(F.expr("cols['0']").alias("document"),
            F.expr("cols['1']").alias("sentiment")).show(truncate=False)
            sentValue = result.collect()[0][3][0][3]
        else:
            output.append("I did not get that. Please Try Again")
            self.misunderstoodCount = self.misunderstoodCount + 1
            return output, self.panicFlag

        if sentValue in breathing.emotions:
            self.negativeEmotionCount = self.negativeEmotionCount + 1

        # Also check if the value is greater then 3
        if (tag in breathing.keywords and sentValue in breathing.emotions) or \
                (self.negativeEmotionCount >= self.countThresh or \
                    self.misunderstoodCount >= self.countThresh):
            self.misunderstoodCount = 0
            self.negativeEmotionCount = 0
            self.panicFlag = True
            output.append("Are you panicking?")

        return output, self.panicFlag

    def spell_checker(self, message):
        print("Original: " + message)
        new_message = self.spell(message)
        print("Altered: " + new_message)
        return new_message

    def send_message(self, message, panicFlag):
        self.panicFlag = panicFlag

        # Spell check
        corrected_message = self.spell_checker(message)

        # Return predicted message
        return self.predict_response(corrected_message)
