import db.{Cassandra, Database, DbConfig, SparkConfig}
import org.apache.spark.ml.feature.{StandardScaler, VectorAssembler}
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.functions.col

class FoodDataMart(sparkConfig: SparkConfig, dbConfig: DbConfig, val limit: Int) {
  private val FEATURES_COLUMN = "scaled_features"
  private val COLUMNS = Map(
    "id" -> Array("code", "product_name"),
    "nutriments" -> Array(
      "energy-kcal_100g",
      "energy_100g",
      "fat_100g",
      "saturated-fat_100g",
      "trans-fat_100g",
      "cholesterol_100g",
      "carbohydrates_100g",
      "sugars_100g",
      "fiber_100g",
      "proteins_100g",
      "salt_100g",
      "sodium_100g",
      "calcium_100g",
      "iron_100g",
      "nutrition-score-fr_100g"
    ),
    "categories" -> Array("categories_en")
  )
  private val database: Database = new Cassandra(sparkConfig, dbConfig)

  private def preprocess(df: DataFrame): DataFrame = {
    val idColumns = COLUMNS.apply("id")
    val featureColumnNames = COLUMNS.apply("nutriments")
    val featureColumns = featureColumnNames.map(c => col(c).cast("float"))
    val catColumns = COLUMNS.apply("categories")

    val allColumns = idColumns.map(col) ++ featureColumns ++ catColumns.map(col)
    val dfWithSelectedColumns = df.select(allColumns: _*)
    val dfWithoutNull = dfWithSelectedColumns.na.drop()
    val limited = dfWithoutNull.limit(limit)

    val vac_assembler = new VectorAssembler()
      .setInputCols(featureColumnNames)
      .setOutputCol("features")
    val dfWithFeatures = vac_assembler.transform(limited)

    val scaler = new StandardScaler().setInputCol("features").setOutputCol(FEATURES_COLUMN)
    val scalerModel = scaler.fit(dfWithFeatures)
    scalerModel.transform(dfWithFeatures)
  }

  def getFood(): DataFrame = {
    val data = database.getData()
    preprocess(data)
  }

  def setPredictions(df: DataFrame): Unit = {
    database.setPredictions(df.select("code", "prediction"))
  }
}
