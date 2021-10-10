# Python 3.9
# To retrain, delete pickle.data and model.tflearn files
# After making changes to intents.json, delete pickle.data file
# In Patterns in intents.json, leave out any punctuation

import pandas as pd
import pyspark.sql.functions as F
import numpy
import random
import sparknlp

from autocorrect import Speller
from sparknlp.annotator import *
from sparknlp.base import *
from pyspark.ml import Pipeline


class ChatBot:
    """ChatBot class for automated messaging 
    and responses using deep learning"""

    def __init__(self):
        self.spell = Speller(lang='en')
        self.words = []
        self.model = 0
        self.labels = []
        self.intents_data = []
        self.spark = sparknlp.start()
        self.MODEL_NAME='classifierdl_use_emotion'
        self.documentAssembler = DocumentAssembler()\
            .setInputCol("text")\
            .setOutputCol("document")
        self.use = UniversalSentenceEncoder.pretrained(name="tfhub_use", lang="en")\
            .setInputCols(["document"])\
            .setOutputCol("sentence_embeddings")
        self.sentimentdl = ClassifierDLModel.pretrained(name=self.MODEL_NAME)\
            .setInputCols(["sentence_embeddings"])\
            .setOutputCol("sentiment")
        self.nlpPipeline = Pipeline(
            stages = [
                self.documentAssembler,
                self.use,
                self.sentimentdl
            ])
        self.empty_df = self.spark.createDataFrame([['']]).toDF("text")

    def bag_of_words(self, message):
        bag  = [0 for _ in range(len(self.words))]
        # s_words = nltk.word_tokenize(s)

    def predict(self, corrected_message):
        results = self.model.predict([self.bag_of_words(corrected_message.lower())])[0]
        results_index = numpy.argmax(results)
        tag = self.labels[results_index]
        print(results)

        if results[results_index] > 0.6:
            for tg in self.intents_data["intents"]:
                if tg['tag'] == tag:
                    # val = random.choice(tg['responses'])
                    # speech = Speech(val, lang)
                    # sox_effects = ("speed", "1.0")
                    # speech.play(sox_effects)
                    responses = tg['responses']
            print(random.choice(responses))
        
            #emotions thinking
            pipelineModel = self.nlpPipeline.fit(self.empty_df)
            df = self.spark.createDataFrame(pd.DataFrame({"text":[corrected_message]}))
            result = pipelineModel.transform(df)
            result.select(F.explode(F.arrays_zip('document.result', 'sentiment.result')).alias("cols")) \
            .select(F.expr("cols['0']").alias("document"),
            F.expr("cols['1']").alias("sentiment")).show(truncate=False)
        else:
            print("I did not get that. Please Try Again") 

    def spell_checker(self, message):
        print("Original: " + message)
        new_message = self.spell(message)
        print("Altered: " + new_message)
        return new_message

    def send_message(self, message):
        # Spell check
        corrected_message = self.spell_checker(message)

        # Return predicted message
        return self.predict(corrected_message)