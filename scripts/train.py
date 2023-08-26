import pyrallis

from src import configs, run


@pyrallis.wrap()
def main(config: configs.TrainConfig):
    run.train(config)


if __name__ == "__main__":
    main()
