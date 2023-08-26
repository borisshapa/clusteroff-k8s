import loguru
import pyspark


def main():
    spark = (
        pyspark.sql.SparkSession.builder.master("local")
        .appName("Word Count")
        .getOrCreate()
    )

    data = [
        "Project Gutenberg’s",
        "Alice’s Adventures in Wonderland",
        "Project Gutenberg’s",
        "Adventures in Wonderland",
        "Project Gutenberg’s",
    ]

    def log_rdd(i: int, rdd: pyspark.RDD):
        loguru.logger.info("RDD{}: \n{}", i, "\n".join(map(str, rdd.collect())))

    rdd1 = spark.sparkContext.parallelize(data)
    log_rdd(1, rdd1)

    rdd2 = rdd1.flatMap(lambda f: f.split(" "))
    log_rdd(2, rdd2)

    rdd3 = rdd2.map(lambda m: (m, 1))
    log_rdd(3, rdd3)

    rdd4 = rdd3.filter(lambda a: a[0].startswith("a"))
    log_rdd(4, rdd4)

    rdd5 = rdd3.reduceByKey(lambda a, b: a + b)
    log_rdd(5, rdd5)

    rdd6 = rdd5.map(lambda a: (a[1], a[0])).sortByKey()
    log_rdd(6, rdd6)

    first_rec = rdd6.first()
    loguru.logger.info("First record: {}, {}", first_rec[0], first_rec[1])

    dat_max = rdd6.max()
    loguru.logger.info("Max record: {}, {}", dat_max[0], dat_max[1])

    total_word_count = rdd6.reduce(lambda a, b: (a[0] + b[0], a[1]))
    loguru.logger.info("data reduce record: {}", total_word_count[0])
    rdd5.saveAsTextFile("word_count")


if __name__ == "__main__":
    main()
