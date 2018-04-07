#!/usr/bin/env bash

pip install -r russell_requirements.txt

jupyter notebook --NotebookApp.token= --NotebookApp.base_url={}

python ***.py