# 🥑 ClusterOFF

Clustering Open Food Facts dataset. 

For clustering, a KMeans algorithm from the [pyspark](https://spark.apache.org/docs/latest/api/python/index.html) framework is used.

## Structure
* `configs` contains the yaml files that define the parameters that necessary for running the algorithm;
* `scripts` ‒ executable files (`python -m scripts.<script-name> [ARGS]`);
* `src` ‒ source code of the function used by scripts;

## Installation
Local installation via pip:
```shell
git clone https://github.com/borisshapa/wine-quality
cd wine-quality
pip install -r requirements.txt
```

Or run build and run docker-compose (recommended):

```shell
docker compose build && \
docker compose up
```
## Data

You can download the data from the link: [https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv](https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv)

Clustering uses only the following columns
* energy-kcal_100g
* energy_100g
* fat_100g
* saturated-fat_100g
* trans-fat_100g
* cholesterol_100g
* carbohydrates_100g
* sugars_100g
* fiber_100g 
* proteins_100g 
* salt_100g
* sodium_100g
* calcium_100g
* iron_100g
* nutrition-score-fr_100g

These columns are convenient because they are of the float type. You can change the list of used columns in the file [configs/columns.json](./configs/columns.json)

Before being transmitted to the algorithm, the data is preprocessed. Preprocessing includes the following steps:

* Deleting rows in which the values of the columns used are `null`.
* Limiting the set to a threshold defined by the config value `data.size`.
* Creating a vector from features.
* Normalization of the vector.

## Model

The algorithm is based on [pyspark KMeans algorithm](https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.ml.clustering.KMeans.html). 
The algorithm is configured using an YAML file. Here is an example of such a config.

```yaml
kmeans:
  k: 5
  maxIter: 20

  seed: 21

data:
  data: "data/en.openfoodfacts.org.products.csv"
  columns: "configs/columns.json"
  size: 10000

spark:
  app_name: "clusteroff"
  deploy_mode: "local"
  driver_memory: "4g"
  executor_memory: "16g"
  executor_cores: 1
  driver_cores: 1

db:
  keyspace: "off"
  table: "food"

datamart: "datamart/target/scala-2.12/datamart_2.12-0.1.0-SNAPSHOT.jar"
save_to: "models/clusteroff"
```

## Training

To run the algorithm, use the following script:

```shell
python -m scripts.train --config_path=configs/train.yml
```

## Database

The algorithm reads data from the cassandra database.
Setup cassandra following the [instruction](https://cassandra.apache.org/_/quickstart.html) and initialize it from csv file using the command:

```yaml
chmod +x cassandra-init.sh && ./cassandra-init.sh
```

## Datamart

To build a jar file with datamart run 

```shell
cd datamart && sbt package && cd ..
```

And specify the path to the jar file in the `datamart` field of config.

## K8S

To deploy cassandra service to kubernetes run `./deploy-cassandra.sh`, then deploy spark application `./deploy-spark-app.sh`.

All the k8s configs are placed in the [configs](./configs) directory.

You can use [minikube](https://minikube.sigs.k8s.io/docs/) as a test cluster.