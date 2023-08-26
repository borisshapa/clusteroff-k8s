import pyspark.sql
import ujson
from pyspark.ml import feature
from pyspark.sql import types

FEATURES_COLUMN = "scaled_feature"


def preprocess(
    df: pyspark.sql.DataFrame,
    select_columns: list[str],
    size: int,
) -> pyspark.sql.DataFrame:
    df_with_selected_columns = df.select(*select_columns)
    df_without_null = df_with_selected_columns.dropna()
    limited = df_without_null.limit(size)

    feature_columns = [
        item[0] for item in limited.dtypes if item[1].startswith("float")
    ]
    vec_assembler = feature.VectorAssembler(
        inputCols=feature_columns, outputCol="features"
    )
    df_with_features = vec_assembler.transform(limited)

    scaler = feature.StandardScaler(inputCol="features", outputCol=FEATURES_COLUMN)
    scaler_model = scaler.fit(df_with_features)
    df_scaled_features = scaler_model.transform(df_with_features)
    return df_scaled_features


def configure_schema(
    columns_filename: str,
) -> tuple[types.StructType, list[str]]:
    with open(columns_filename, "r") as columns_file:
        columns = ujson.load(columns_file)

    fields = []
    select_columns = []
    for col_name in columns["id"]:
        select_columns.append(col_name)
        fields.append(types.StructField(col_name, types.StringType(), nullable=False))

    nutriments = []
    for col_name in columns["nutriments"]:
        nutriments.append(types.StructField(col_name, types.FloatType(), nullable=True))
    fields.append(types.StructField("nutriments", types.StructType(nutriments)))
    select_columns.append("nutriments.*")

    for col_name in columns["categories"]:
        select_columns.append(col_name)
        fields.append(types.StructField(col_name, types.StringType(), nullable=True))

    return types.StructType(fields), select_columns
