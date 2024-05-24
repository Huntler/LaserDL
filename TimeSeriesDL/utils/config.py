"""This module contains the config manager."""
from typing import Dict
import yaml
import torch
import numpy as np

from TimeSeriesDL.model.base_model import BaseModel


class Config:
    """Handles algorithm argument and model parameter load and save.
    """

    _precisions = {"float16": (np.float16, torch.float16),
                   "float32": (np.float32, torch.float32),
                   "float64": (np.float64, torch.float64),
                   "int8": (np.uint8, torch.uint8)}

    def __init__(self) -> None:
        self.__model_register = {}

    def register_model(self, name: str, model_class: BaseModel) -> None:
        """Method registers a model corresponding to the provided name.

        Args:
            name (str): The name, so the model can be accessed later on.
            model_class (BaseModel): The class of the model to register.
        """
        self.__model_register[name] = model_class

    def _set_precision(self, d: Dict) -> Dict:
        if not "precision" in d.keys():
            return d

        # check if precision is registered
        precisions = self._precisions.get(d["precision"], None)
        if not precisions:
            return d

        d["model"]["precision"] = precisions[1]
        d["dataset"]["precision"] = precisions[0]

        return d

    def get_model(self, name: str) -> BaseModel:
        """Method returns a registered BaseModel.

        Args:
            name (str): The models register name

        Raises:
            RuntimeError: Occurs if the model was not registered.

        Returns:
            BaseModel: The model corresponding to the name.
        """
        model = self.__model_register.get(name, None)
        if not model:
            raise RuntimeError(f"Model of type {name} is not registered.")

        return model

    def get_args(self, path: str) -> Dict:
        """This method reads the hyperparameters and program args of a 
        specified yaml and returns them as dictionary.

        Args:
            path (str): The yaml path file.

        Returns:
            Dict: The dictionary containing all arguments.
        """
        with open(path, "r", encoding="UTF-8") as stream:
            args = yaml.safe_load(stream)

        return self._set_precision(args)

    def store_args(self, path: str, args: Dict) -> None:
        """Stores the argument dictionary to a given file path.

        Args:
            path (str): The file path.
            args (Dict): The arguments.
        """
        with open(path, "w", encoding="UTF-8") as stream:
            yaml.safe_dump(args, stream)


config = Config()
