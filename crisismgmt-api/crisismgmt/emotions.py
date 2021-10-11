import pandas as pd
import numpy as np
import json
from pyspark.ml import Pipeline
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from sparknlp.annotator import *
from sparknlp.base import *
 
from sparknlp.pretrained import PretrainedPipeline
from pyspark.sql.functions import col

spark = sparknlp.start()
MODEL_NAME='classifierdl_use_emotion'

text_list = [
            """ifheifheihf""",
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
print('######result.select#########')
result.select(F.explode(F.arrays_zip('document.result', 'sentiment.result')).alias("cols")) \
.select(F.expr("cols['1']").alias("sentiment")).show(truncate=False)
#result.collect()
# for row in result.collect()[0:3]:
# print((row["text"]),",",str(row["sentiment"]))
# value = result.collect()[0][3]
# value = result.collect()[0][3][0][3]



