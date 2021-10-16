import numpy as np
import threading
import pandas as pd
import pyspark.sql.functions as F
import nltk
import numpy
import random
import json
import tflearn
import pickle
import sparknlp
import random
import breathing
from sparknlp.annotator import *
from sparknlp.base import *
from sparknlp.pretrained import PretrainedPipeline
from re import X
from autocorrect import Speller
from pyspark.ml import Pipeline
from pyspark.sql import SparkSession
from nltk import stem
from nltk.sem.relextract import class_abbrev
from nltk.stem.lancaster import LancasterStemmer
from tensorflow.python.ops.gen_array_ops import shape
from tensorflow.python.ops.gen_batch_ops import batch


#Speech Library
from google_speech import Speech

lang = "en"

keywords = np.array(['Emergency Keywords','Bot response: No Safe Place Found', 
'Bot response: Safe Place Found'])

emotions = np.array(['surprise', 'fear', 'sadness'])
#Hold your breath, and silently count from 1 to 7. Breathe out completely as you silently count from 1 to 8, repeat three times

sox_effects = ("speed", "1.1")

def speakThis(val):
    print(val)
    speech = Speech(val, lang)
    speech.play(sox_effects)

def keepBreathing(numberOfSecondsPassed):
    #Speech Library
    val = str(numberOfSecondsPassed) + " second(s)..."
    speakThis(val)

def calmDown():
    delay = int(1)
    event = threading.Event()
    val = "Hold your breath, and silently count from 1 to 7. Then, breathe out completely as you silently count from 1 to 8"
    speakThis(val)
    val = "We will repeat this 3 times"
    speakThis(val)


    r1 = range(3)
    for i in r1:
        val = "Let's now hold our breath together for 7 seconds"
        speakThis(val)
        r2 = range(7)
        for j in r2:
            event.wait(delay)
            keepBreathing(j+1)

        val = "Now let's now breathe out slowly for 8 seconds"
        speakThis(val)
        r2 = range(8)
        for j in r2:
            event.wait(delay)
            keepBreathing(j+1)
        
        if (i == 1):
            val = "Almost done, one last time"
            speakThis(val)