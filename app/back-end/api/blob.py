#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import tempfile
import os
import traceback
from azure.storage.blob import (
    BlobServiceClient,
    ContentSettings,
)
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from langchain.document_loaders import (
    TextLoader,
    Docx2txtLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
)
from langchain.document_loaders.pdf import UnstructuredPDFLoader
from config import BLOB_CONTAINER_NAME


class Blob:
    def __init__(self, connection_string: str, service_client=None) -> None:
        if service_client is None:
            self.service_client = BlobServiceClient.from_connection_string(
                connection_string
            )
        else:
            self.service_client = service_client

    def form_metadata(
        self, uuid: str, filename: str, contact_person: str, language: str
    ):
        """
        Forms metadata for a blob.

        Args:
            uuid (str): The UUID of the blob.
            filename (str): The filename of the blob.
            contact_person (str): The contact person for the blob.
            language (str): The language of the blob.

        Returns:
            dict: A dictionary containing the metadata for the blob.
        """
        return {
            "uuid": uuid,
            "filename": filename,
            "contact_person": contact_person,
            "language": language,
        }

    def blob_upload(
        self,
        blob_name: str,
        container_name: str,
        file,
        metadata: dict,
        overwrite: bool = False,
    ) -> str:
        """blob_upload: Upload a single local file to Azure Blob Storage, under a specific container.

        Args:
            blob_name (str): blob name of the file that will be uploaded
            container_name (str): name of the container that the blob will be upload to
            file (_type_): file to be uploaded
            metadata (dict): metadata of the blob
            overwrite (bool, optional): To overwrite the blob if the blob already exists. Defaults to False.

        Raises:
            ResourceExistsError: _description_
            traceback.format_exc: _description_

        Returns:
            str : blob_name
        """
        try:
            blob_client = self.service_client.get_blob_client(
                container=container_name,
                blob=blob_name,
            )
            content_settings = ContentSettings(
                content_type=file.headers["Content-Type"],
                content_disposition=file.headers["Content-Disposition"],
            )
            blob_client.upload_blob(
                data=file.file.read(),
                metadata=metadata,
                content_settings=content_settings,
                overwrite=overwrite,
            )
            return blob_client.blob_name
        except ResourceExistsError:
            raise ResourceExistsError("The specified blob already exists.")
        except Exception as e:
            raise traceback.format_exc(e)

    def blob_download(self, container_name: str, blob_name: str) -> None:
        """blob_download: Download a single blob under a container to your local machine.
        We default the local file name is the same as your file name on Azure Storage.
        If the blob is not found, a ResourceNotFoundError will be raised.

        Args:
            container_name (str): name of the container that the blob is in
            blob_name (str): blob name of the file that will be downloaded

        Raises:
            ResourceNotFoundError: _description_
            traceback.format_exc: _description_

        Returns:
            str: blob content in string? TODO
        """
        try:
            blob_client = self.service_client.get_blob_client(
                container=container_name,
                blob=blob_name,
            )
            downloaded_blob = blob_client.download_blob()
            # TODO how to turn it into str

            return downloaded_blob.readall()
        except ResourceNotFoundError:
            raise ResourceNotFoundError("The specified blob does not exist.")
        except Exception as e:
            raise traceback.format_exc(e)

    def copy_blob_in_azure(
        self,
        src_container_name: str,
        src_blob_name: str,
        dest_container_name: str,
        dest_blob_name: str,
    ) -> str:
        """copy_blob_in_azure: Copy a blob from one container to another container in Azure Storage.

        Args:
            src_container_name (str): container name of the source blob
            src_blob_name (str): blob name of the source blob
            dest_container_name (str): container name of the destination blob
            dest_blob_name (str): blob name of the destination blob

        Raises:
            ResourceNotFoundError: _description_
            traceback.format_exc: _description_

        Returns:
            str: url of the destination blob (?) TODO
        """

        try:
            src_blob_client = self.service_client.get_blob_client(
                container=src_container_name,
                blob=src_blob_name,
            )
            dest_blob_client = self.service_client.get_blob_client(
                dest_container_name, dest_blob_name
            )

            source_blob = f"https://{src_blob_client.account_name}.blob.core.windows.net/{src_container_name}/{src_blob_name}"
            res = dest_blob_client.start_copy_from_url(source_blob)
            filename = dest_blob_client.get_blob_properties().metadata["filename"]
            if res["copy_status"] == "success":
                return dest_blob_client.url, filename
            else:
                raise Exception("File upload failed")

        except ResourceNotFoundError:
            raise ResourceNotFoundError("The specified blob does not exist.")
        except Exception as e:
            raise traceback.format_exc(e)

    def delete_blob(self, container_name: str, blob_name: str) -> None:
        """
        Deletes a blob from the specified container.

        Args:
            container_name (str): The name of the container.
            blob_name (str): The name of the blob to delete.

        Raises:
            Exception: If an error occurs while deleting the blob.
        """
        try:
            blob_client = self.service_client.get_blob_client(
                container=container_name,
                blob=blob_name,
            )
            blob_client.delete_blob()
        except Exception as e:
            raise e

    def load_blob(self, container_name: str, blob_name: str):
        """load_blob: Load a blob from Azure Storage and return the content as a string.

        Args:
            container_name (str): name of the container that the blob is in
            blob_name (str): blob name of the file that will be loaded

        Raises:
            Exception: _description_ TODO
            e: _description_ TODO

        Returns:
            _type_: _description_ TODO
        """
        try:
            blob_client = self.service_client.get_blob_client(
                container=container_name,
                blob=blob_name,
            )
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = f"{temp_dir}/{container_name}/{blob_name}"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(f"{file_path}", "wb") as file:
                    blob_data = blob_client.download_blob()
                    blob_data.readinto(file)
                try:
                    if file_path.lower().endswith(".txt"):
                        loader = TextLoader(file_path)
                    elif file_path.lower().endswith(".pdf"):
                        loader = UnstructuredPDFLoader(file_path)
                    elif file_path.lower().endswith(".docx"):
                        loader = Docx2txtLoader(file_path)
                    elif file_path.lower().endswith(".doc"):
                        loader = UnstructuredWordDocumentLoader(file_path)
                    elif file_path.lower().endswith(
                        ".pptx"
                    ) or file_path.lower().endswith(".ppt"):
                        loader = UnstructuredPowerPointLoader(file_path)
                    else:
                        raise Exception("Unsupported file type")
                    return loader.load()
                except Exception as e:
                    raise e
        except Exception as e:
            # TODO
            raise e

    def set_blob_metadata(
        self,
        metadata: dict,
        blob_name: str,
        container_name: str = BLOB_CONTAINER_NAME,
    ):
        """_summary_

        Args:
            blob_name (str): the blob name with extension
            original_name (str): the original file name with extension
            container_name (str, optional): Azure container name. Defaults to BLOB_CONTAINER_NAME.
        """
        try:
            blob_client = self.service_client.get_blob_client(
                container=container_name,
                blob=blob_name,
            )
            more_blob_metadata = metadata
            blob_client.set_blob_metadata(metadata=more_blob_metadata)
            return "OK"
        except Exception as e:
            # TODO
            raise e
