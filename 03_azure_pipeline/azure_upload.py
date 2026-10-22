"""Uploads the cleaned CSVs to Azure Blob Storage.
Setup:  pip install azure-storage-blob
        export AZURE_STORAGE_CONNECTION_STRING="<Storage account > Access keys>"
Run:    python azure_upload.py
"""
import os, glob
from azure.storage.blob import BlobServiceClient
svc = BlobServiceClient.from_connection_string(os.environ["AZURE_STORAGE_CONNECTION_STRING"])
container = svc.get_container_client("clean")
if not container.exists(): container.create_container()
clean = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "clean", "*.csv")
for path in glob.glob(clean):
    with open(path, "rb") as f: container.upload_blob(os.path.basename(path), f, overwrite=True)
    print("uploaded", os.path.basename(path))
