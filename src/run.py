import dataclasses

import loguru
import pyspark
from pyspark.ml import clustering, evaluation

from src import configs, utils


def train(config: configs.TrainConfig):
    spark_config = config.spark
    spark = (
        pyspark.sql.SparkSession.builder.appName(spark_config.app_name)
        .master(spark_config.deploy_mode)
        .config("spark.driver.cores", spark_config.driver_cores)
        .config("spark.executor.cores", spark_config.executor_cores)
        .config("spark.driver.memory", spark_config.driver_memory)
        .config("spark.executor.memory", spark_config.executor_memory)
        .getOrCreate()
    )

    data = spark.read.option("sep", "\t").option("header", True).csv(config.data.data)
    df = utils.preprocess(data, config.data.columns, config.data.size)

    kmeans_kwargs = dataclasses.asdict(config.kmeans)
    loguru.logger.info("Using kmeans model with parameters: {}", kmeans_kwargs)
    loguru.logger.info("Training")
    model = clustering.KMeans(featuresCol=utils.FEATURES_COLUMN, **kmeans_kwargs)
    model_fit = model.fit(df)

    loguru.logger.info("Evaluation")
    evaluator = evaluation.ClusteringEvaluator(
        predictionCol="prediction",
        featuresCol=utils.FEATURES_COLUMN,
        metricName="silhouette",
        distanceMeasure="squaredEuclidean",
    )
    output = model_fit.transform(df)
    output.show()

    score = evaluator.evaluate(output)
    loguru.logger.info("Silhouette Score: {}", score)

    loguru.logger.info("Saving to {}", config.save_to)
    model_fit.write().overwrite().save(config.save_to)
