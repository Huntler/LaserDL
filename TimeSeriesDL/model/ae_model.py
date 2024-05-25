"""This module contains a basic auto-encoder based on CNN."""

from datetime import datetime
from typing import Tuple
import torch
from torch import nn
from torch.utils.tensorboard import SummaryWriter
from torch.optim.lr_scheduler import ExponentialLR
from TimeSeriesDL.utils.activations import get_activation_from_string
from TimeSeriesDL.model.base_model import BaseModel
from TimeSeriesDL.utils.config import config


class AE(BaseModel):
    """This model uses CNN to auto-encode time-series.

    Args:
        BaseModel (BaseModel): The base model class.
    """

    def __init__(
        self,
        features: int = 1,
        sequence_length: int = 1,
        extracted_features: int = 1,
        latent_space: int = 1,
        kernel_size: int = 1,
        stride: int = 1,
        padding: int = 1,
        last_activation: str = "relu",
        lr: float = 1e-3,
        lr_decay: float = 9e-1,
        adam_betas: Tuple[float, float] = (9e-1, 999e-3),
        tag: str = "",
        log: bool = True,
    ) -> None:
        # if logging enalbed, then create a tensorboard writer, otherwise prevent the
        # parent class to create a standard writer
        if log:
            now = datetime.now()
            self._tb_sub = now.strftime("%d%m%Y_%H%M%S")
            self._tb_path = f"runs/{tag}/AE/{self._tb_sub}"
            self._writer = SummaryWriter(self._tb_path)
        else:
            self._writer = False

        super().__init__(self._writer)

        # data parameter
        self._features = features
        self._extracted_features = extracted_features
        self._sequence_length = sequence_length

        # cnn parameter
        self._kernel_size = kernel_size
        self._stride = stride
        self._padding = padding

        self._latent_space = latent_space
        self._last_activation = get_activation_from_string(last_activation)

        # check if the latent space will be bigger than the output after the first conv1d layer
        ef_length = ((sequence_length - kernel_size + 2 * padding) / stride) + 1
        ls_length = ((ef_length - kernel_size + 2 * padding) / stride) + 1
        if ef_length > ls_length:
            print(
                "Warning: Output after first encoder layer is smaller than latent "
                + f"space. {ef_length} > {ls_length}"
            )

        # setup the encoder based on CNN
        self._encoder = nn.Sequential(
            nn.Conv1d(
                self._features,
                self._extracted_features,
                self._kernel_size,
                self._stride,
                self._padding,
            ),
            nn.ReLU(),
            nn.Conv1d(
                self._extracted_features,
                self._latent_space,
                self._kernel_size,
                self._stride,
                self._padding,
            ),
            nn.ReLU(),
        )

        # setup decoder
        self._decoder = nn.Sequential(
            nn.ConvTranspose1d(
                self._latent_space,
                self._extracted_features,
                self._kernel_size,
                self._stride,
                self._padding,
            ),
            nn.ReLU(),
            nn.ConvTranspose1d(
                self._extracted_features,
                self._features,
                self._kernel_size,
                self._stride,
                self._padding,
            ),
            self._last_activation,
        )

        self._loss_fn = torch.nn.MSELoss()
        self._optim = torch.optim.AdamW(self.parameters(), lr=lr, betas=adam_betas)
        self._scheduler = ExponentialLR(self._optim, gamma=lr_decay)

    def encode(self, x: torch.tensor) -> torch.tensor:
        """Encodes the input.

        Args:
            x (torch.tensor): The input.

        Returns:
            torch.tensor: The encoded data.
        """
        return self._encoder(x)

    def decode(self, x: torch.tensor) -> torch.tensor:
        """Decodes the input, should be the same as before encoding the data.

        Args:
            x (torch.tensor): The input.

        Returns:
            torch.tensor: The decoded data.
        """
        return self._decoder(x)

    def freeze(self, unfreeze: bool = False) -> None:
        """Freezes or unfreezes the parameter of this AE to enable or disable parameter tuning.

        Args:
            unfreeze (bool, optional): Unfreezes the parameter if set to True. Defaults to False.
        """
        for param in self._encoder.parameters():
            param.requires_grad = not unfreeze

        for param in self._decoder.parameters():
            param.requires_grad = not unfreeze

    def forward(self, x: torch.tensor, future_steps: int = 0):
        x = self._encoder(x)
        return self._decoder(x)

    def load(self, path: str) -> None:
        self.load_state_dict(torch.load(path))
        self.eval()

config.register_model("SimpleModel", AE)
