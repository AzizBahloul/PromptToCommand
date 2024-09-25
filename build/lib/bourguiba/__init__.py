# bourguiba/__init__.py

from .model_downloader import download_model
import os

# Set the custom model directory
model_dir = os.path.join(os.path.expanduser("~"), ".bourguiba_model")

# Download the model
download_model(model_dir)
