package db

import org.apache.spark.sql.DataFrame
trait Database {
  def get_data(): DataFrame
  def set_predictions(df: DataFrame): Unit
}
