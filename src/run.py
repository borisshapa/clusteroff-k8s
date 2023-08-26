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

    schema, select_columns = utils.configure_schema(config.data.columns)
    data = spark.read.schema(schema).json(config.data.data)
    df = utils.preprocess(data, select_columns, config.data.size)

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
    score = evaluator.evaluate(output)
    loguru.logger.info("Silhouette Score: {}", score)

    loguru.logger.info("Saving to {}", config.save_to)
    model_fit.save(config.save_to)
