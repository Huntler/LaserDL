"""This module contains a variational auto-encoder based on CNN."""

from datetime import datetime
from typing import Tuple
import torch
from torch import nn
from torch.utils.tensorboard import SummaryWriter
from TimeSeriesDL.model import ConvAE
from TimeSeriesDL.utils.config import config


class ConvVAE(ConvAE):
    """This model uses a variational auto-encoder (VAE) based on Convolutional
    layers to auto-encode time-series.

    Args:
        BaseModel (BaseModel): The base model class.
    """

    def __init__(
        self,
        features: int = 1,
        sequence_length: int = 1,
        channels: int = 1,
        extracted_features: int = 1,
        latent_size: int = 1,
        kernel_size: int = 1,
        stride: int = 1,
        padding: int = 0,
        last_activation: str = "sigmoid",
        lr: float = 1e-3,
        lr_decay: float = 9e-1,
        adam_betas: Tuple[float, float] = (9e-1, 999e-3),
        tag: str = "",
        log: bool = True,
        precision: torch.dtype = torch.float32,
    ) -> None:
        super().__init__(features, sequence_length, channels, extracted_features, latent_size,
                         kernel_size, stride, padding, last_activation, lr, lr_decay,
                         adam_betas, tag, log, precision)
        # setup latent space distribution
        self._mean_layer = nn.Linear(
            self._enc_2_len * self._latent_space,
            self._enc_2_len * self._latent_space, dtype=self._precision
        )

        self._var_layer = nn.Linear(
            self._enc_2_len * self._latent_space,
            self._enc_2_len * self._latent_space, dtype=self._precision
        )

    def _init_writer(self, name, tag, log) -> None:
        if not log:
            return

        now = datetime.now()
        self._tb_sub = now.strftime("%d%m%Y_%H%M%S")
        self._tb_path = f"runs/{tag}/VAE/{self._tb_sub}"
        self._writer = SummaryWriter(self._tb_path)

    def reparameterization(self, mean: torch.tensor, var: torch.tensor) -> torch.tensor:
        """Samples from the latent representation, which is a random distribution in this case.

        Args:
            mean (torch.tensor): The mean of the encoded date.
            var (torch.tensor): The log_variance of the encoded data.

        Returns:
            torch.tensor: The sampled encoded data.
        """
        epsilon = torch.randn_like(var).to(self._device)
        z = mean + var * epsilon
        return z

    def encode(self, x: torch.tensor, as_array: bool = False) -> torch.tensor:
        # change input to batch, features, samples
        x, _ = self._encode(x)

        if as_array:
            return x.detach().cpu().numpy()
        return x

    def _encode(self, x: torch.tensor) -> Tuple[torch.tensor, torch.tensor]:
        # change input to batch, channels, features, samples
        x: torch.tensor = torch.swapaxes(x, 1, 3) # batch, feature, channel, sample
        x: torch.tensor = torch.swapaxes(x, 2, 1) # batch, channel, feature sample

        x = self._encoder_1.forward(x)
        x = torch.relu(x)

        x = self._encoder_2.forward(x)
        x = torch.relu(x)

        # change input to batch, features + samples * channels for Linear layer
        batch, channels, features, samples = x.shape
        x = x.view(batch, features * samples * channels)
        mean = self._mean_layer(x).view(batch, channels, features, samples)
        log_var = self._var_layer(x).view(batch, channels, features, samples)
        return mean, log_var

    def freeze(self, unfreeze: bool = False) -> None:
        """Freezes or unfreezes the parameter of this AE to enable or disable parameter tuning.

        Args:
            unfreeze (bool, optional): Unfreezes the parameter if set to True. Defaults to False.
        """
        super().freeze(unfreeze)

        layers = [
            self._mean_layer.parameters(),
            self._var_layer.parameters(),
        ]

        for layer in layers:
            for param in layer:
                param.requires_grad = not unfreeze

    def forward(self, x: torch.tensor):
        # encode the data to mean/log_var of latent space
        mean, log_var = self._encode(x)

        # takes exponential function (log var -> var)
        z = self.reparameterization(mean, torch.exp(0.5 * log_var))

        # decode data back
        return self.decode(z)

    def load(self, path: str) -> None:
        self.load_state_dict(torch.load(path))
        self.eval()


config.register_model("ConvVAE", ConvVAE)