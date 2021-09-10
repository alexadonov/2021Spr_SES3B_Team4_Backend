import pandas as pd
import numpy as np
import json
from pyspark.ml import Pipeline
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from sparknlp.annotator import *
from sparknlp.base import *
import sparknlp
from sparknlp.pretrained import PretrainedPipeline

spark = sparknlp.start()
MODEL_NAME='classifierdl_use_emotion'

text_list = [
            """I am hurt""",
            """That moment when you see your friend in a commercial. Hahahaha!""",
            """My soul has just been pierced by the most evil look from @rickosborneorg. A mini panic attack &amp; chill in bones followed soon after.""",
            """For some reason I woke up thinkin it was Friday then I got to school and realized its really Monday -_-""",
            """I'd probably explode into a jillion pieces from the inablility to contain all of my if I had a Whataburger patty melt right now. #drool""",
            """These are not emotions. They are simply irrational thoughts feeding off of an emotion""",
            """Found out im gonna be with sarah bo barah in ny for one day!!! Eggcitement :)""",
            """That awkward moment when you find a perfume box full of sensors!""",
            """Just home from group celebration - dinner at Trattoria Gianni, then Hershey Felder's performance - AMAZING!!""",
            """Nooooo! My dad turned off the internet so I can't listen to band music!""",
            ]

documentAssembler = DocumentAssembler()\
    .setInputCol("text")\
    .setOutputCol("document")
    
use = UniversalSentenceEncoder.pretrained(name="tfhub_use", lang="en")\
 .setInputCols(["document"])\
 .setOutputCol("sentence_embeddings")


sentimentdl = ClassifierDLModel.pretrained(name=MODEL_NAME)\
    .setInputCols(["sentence_embeddings"])\
    .setOutputCol("sentiment")

nlpPipeline = Pipeline(
      stages = [
          documentAssembler,
          use,
          sentimentdl
      ])

empty_df = spark.createDataFrame([['']]).toDF("text")

pipelineModel = nlpPipeline.fit(empty_df)
df = spark.createDataFrame(pd.DataFrame({"text":text_list}))
result = pipelineModel.transform(df)

result.select(F.explode(F.arrays_zip('document.result', 'sentiment.result')).alias("cols")) \
.select(F.expr("cols['0']").alias("document"),
        F.expr("cols['1']").alias("sentiment")).show(truncate=False)