# TimeSeriesDL: Predicting Future Curvature of Time Series
[![Python Package using Conda](https://github.com/Huntler/TimeSeriesDL/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/Huntler/TimeSeriesDL/actions/workflows/python-package-conda.yml)

Repository based on the first assignment of the deep learning course at Universiteit Maastricht. The TimeSeriesDL framework enables rapid model prototyping of time series prediction.

## Setup
Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) on your system and execute the follwing command afterwards.

```
conda env create -f environment-<device>.yml
```

After installation, the environment can be activated by calling 

```
conda activate timeseries-dl
```

## Usage
### Training
This program uses configuration `yaml`-files to set program arguments and deep learning hyperparameters. To configure a file, have a look at the example files located in ```examples/<subfolder>/```. To start an example, call the following command

```
python examples/<subfolder>/train.py
```

Now, the training is running and a log folder is created in the directory ```runs/<MODEL_TYPE>/<TIME_STAMP>```. Every log folder contains the `yaml`-configuration which was used to start a training. By this, it is easier to keep track of the best hyperparameters found so far.

### Tensorboard
Make sure the conda environment is enabled, then call

```
tensorboard --logdir=runs
```

to show all trainings in tensorboard. Press [here](http://localhost:6006) to access the webpage.

## Features
- [x] GPU support for CUDA capable graphic cards and Apple Silicon
- [x] Configuration management
- [x] Base model to simplify code of custom models
- [x] Simple CNN/LSTM model exploiting multiple time series for prediction
- [x] Tensorboard logging, model saving & more
- [x] Dataset normalization & transformation
- [x] Dataset random shuffle
- [x] Split into train- / validationset
- [ ] Load dataset as chunks for low memory training
- [x] Prediction of 'x' steps into future
- [x] Visualization of dataset / prediction
- [ ] Automatic parameter tuning
