#!/bin/bash

source ../.venv/bin/activate
pygwalker config --set privacy=offline
streamlit run Welcome.py &> streamlit.log &