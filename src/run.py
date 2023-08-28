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
        .config("spark.cassandra.connection.host", "cassandra")
        .config("spark.cassandra.connection.port", "9042")
        .getOrCreate()
    )
    data = (
        spark.read.format("org.apache.spark.sql.cassandra")
        .options(**dataclasses.asdict(config.db))
        .load()
    )
    df = utils.preprocess(data, config.data.columns, config.data.size)

    df.show()

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

    loguru.logger.info("Writing result into database")
    output.select("code", "prediction").write.format(
        "org.apache.spark.sql.cassandra"
    ).options(table="food", keyspace="off").mode("append").save()
