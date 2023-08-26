import dataclasses
from typing import Optional


@dataclasses.dataclass
class KMeansConfig:
    k: int = dataclasses.field(default=2)
    maxIter: int = dataclasses.field(default=20)
    seed: Optional[int] = dataclasses.field(default=None)


@dataclasses.dataclass
class DataConfig:
    data: str = dataclasses.field(default="data/openfoodfacts-products.jsonl")
    columns: str = dataclasses.field(default="configs/columns.json")
    size: int = dataclasses.field(default=100000)


@dataclasses.dataclass
class SparkConfig:
    app_name: str = dataclasses.field(default="clusteroff")
    deploy_mode: str = dataclasses.field(default="local")
    driver_memory: str = dataclasses.field(default="4g")
    executor_memory: str = dataclasses.field(default="16g")
    executor_cores: int = dataclasses.field(default=1)
    driver_cores: int = dataclasses.field(default=1)


@dataclasses.dataclass
class TrainConfig:
    kmeans: KMeansConfig = dataclasses.field(default_factory=KMeansConfig)
    data: DataConfig = dataclasses.field(default_factory=DataConfig)
    spark: SparkConfig = dataclasses.field(default_factory=SparkConfig)
    save_to: str = dataclasses.field(default="models/clusteroff")
