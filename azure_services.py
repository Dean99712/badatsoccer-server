import os

from azure.storage.blob import BlobServiceClient

conn_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')


def create_blob_service():
    return BlobServiceClient.from_connection_string(conn_str=conn_string)


def blob_exists(container_client, blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    try:
        blob_client.get_blob_properties()
        return True
    except Exception as e:
        return False


def container_exists(blob_service, name):
    try:
        container_client = blob_service.create_container(name)
        print(f"Container '{name}' created.")
        return container_client

    except Exception as _:
        print(f"Container '{name}' already exists.")
        return blob_service.get_container_client(name)


def connect_to_azure_storage(container_name):
    blob_service = create_blob_service()
    container_client = container_exists(blob_service, container_name)

    try:
        if container_exists(blob_service, container_name):
            container_client = blob_service.get_container_client(container=container_name)
            container_client.get_container_properties()
            return container_client
        return container_client
    except:
        container_client = blob_service.create_container(container_name)
        return container_client
