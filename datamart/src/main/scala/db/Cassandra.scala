package db

import org.apache.spark.sql.cassandra.DataFrameReaderWrapper
import org.apache.spark.sql.{DataFrame, SparkSession}

class SparkConfig(
                   val appName: String,
                   val deployMode: String,
                   val driverMemory: String,
                   val executorMemory: String,
                   val executorCores: Int,
                   val driverCores: Int
                 )

class DbConfig(
              val keyspace: String,
              val table: String
              )

class Cassandra(config: SparkConfig, val dbConfig: DbConfig) extends Database {
  private val spark = SparkSession.builder()
    .appName(config.appName)
    .master(config.deployMode)
    .config("spark.driver.cores", config.driverCores)
    .config("spark.executor.cores", config.executorCores)
    .config("spark.driver.memory", config.driverMemory)
    .config("spark.executor.memory", config.executorMemory)
    .config("spark.cassandra.connection.host", "cassandra")
    .config("spark.cassandra.connection.port", "9042")
    .getOrCreate()

  override def getData(): DataFrame = {
    spark.read.cassandraFormat(dbConfig.table, dbConfig.keyspace).load()
  }

  override def setPredictions(df: DataFrame): Unit = {
    df.writeTo(dbConfig.table)
  }
}
