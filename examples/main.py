"""Train a model using a CLI or provide the hyperparameters directly to the CLI."""
from lightning.pytorch.loggers import TensorBoardLogger

# simple demo classes for your convenience
from TimeSeriesDL.model import ConvLSTM
from TimeSeriesDL.data import TSDataModule
from TimeSeriesDL.utils import TSLightningCLI


def cli_main():
    cli = TSLightningCLI(ConvLSTM, TSDataModule, run=False)

    # set up the logger
    logger = TensorBoardLogger("lightning_logs", name=cli.model.__class__.__name__)
    cli.trainer.logger = logger

    # train
    cli.trainer.fit(cli.model, cli.datamodule)


if __name__ == "__main__":
    cli_main()
