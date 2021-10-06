# cool_ct

This repository contains the code of `cool_ct`, a [computed tomography scan](https://en.wikipedia.org/wiki/CT_scan) simulator written in Python.

It was written for an assessment task for a university course.

## Features

* Generates incremental CT scans and sinogram.
* Configurable count and span of emitter-detector pairs and angular increment.
* Outputs the final image to a (mostly compliant) DICOM file.

## Basic usage

Create the virtual environment and install requirements:

```bash
python3 -m venv .env
source .env/bin/activate
pip3 install -r requirements.txt
```

Use the command-line interface to generate a CT scan using 180 emitter-detector pairs:

```console
$ python3 cli.py INPUT_IMAGE --span 40 --increment 2 --n 180
```

It is also possible to use the software interactively using the provided [Jupyter Notebook](CT.ipynb) file.

## Example image

![CT scan](images/CT_ScoutView.out_example.jpg)
