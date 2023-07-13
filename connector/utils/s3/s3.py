import io
import logging
import os
import sys

import boto3

script_dir = os.path.dirname(__file__)
path_range = "../" * 5

mymodule_dir = os.path.join(script_dir, path_range)
sys.path.append(mymodule_dir)

from model.schema import MimeType, S3BufferUploadDestination, SupportedFileTypes

from datapipes_images_utils.logger_utils.module_logger import get_module_logger

logger = get_module_logger(__name__)


class NonCloseableBufferedReader(io.BytesIO):
    def close(self):
        self.seek(0)
        self.truncate()


class S3BufferUploads:
    def __init__(
        self,
        destination_config: S3BufferUploadDestination,
        file_type: SupportedFileTypes,
    ) -> None:
        self.buffer = io.BytesIO()
        self.destination_config = destination_config
        self.bucket_name = destination_config.bucket_name
        self.file_name = destination_config.file_name
        self.batch_count = 0
        self.multipart_files = []
        self.create_clients(file_type)

    def create_clients(self, file_type: SupportedFileTypes):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.destination_config.secret.access_key,
            aws_secret_access_key=self.destination_config.secret.secret_key.get_secret_value(),
            region_name=self.destination_config.secret.region,
        )

        self.multipart_upload = self.s3_client.create_multipart_upload(
            ACL="private",
            Bucket=self.bucket_name,
            ContentType=MimeType[file_type.value].value,
            Key=self.file_name,
        )

    def write_buffer(self, data: bytes):
        self.buffer.write(data)

    def check_buffer_limit(self, buffer_size: int = 10 * 1024 * 1024):
        # Once the buffer reaches a certain size (e.g. 10MB), time to upload.
        if self.buffer.tell() >= buffer_size:
            logger.info(f"Buffer size ready to upload for batch:{self.batch_count+1}")
            return True
        return False

    def mutlipart_file_parts(self, upload_part: dict):
        self.multipart_files.append(
            {"PartNumber": self.batch_count, "ETag": upload_part["ETag"]}
        )

    @property
    def clear_buffer(self):
        self.buffer.seek(0)
        self.buffer.truncate()

    @property
    def next_batch_count(self):
        self.batch_count += 1
        return self.batch_count

    def buffer_uploads(self):
        self.next_batch_count

        # Reset the buffer's position to the beginning
        self.buffer.seek(0)

        # Upload the data to S3
        logger.info(f"Uploading batch:{self.batch_count}")

        # self.s3_client.upload_fileobj(self.buffer, self.bucket_name, self.temp_file_name)
        response = self.s3_client.upload_part(
            Bucket=self.bucket_name,
            Key=self.file_name,
            PartNumber=self.batch_count,
            UploadId=self.multipart_upload["UploadId"],
            Body=self.buffer,
        )
        self.mutlipart_file_parts(response)

        self.clear_buffer

    def upload_last_buffer(self):
        self.next_batch_count

        # Upload any remaining data in the buffer to S3
        if self.buffer.tell() > 0:
            logger.info(f"Writing last batch of buffer:{self.buffer.tell()}")
            self.buffer.seek(0)
            response = self.s3_client.upload_part(
                Bucket=self.bucket_name,
                Key=self.file_name,
                PartNumber=self.batch_count,
                UploadId=self.multipart_upload["UploadId"],
                Body=self.buffer,
            )
            self.mutlipart_file_parts(response)
            logger.info("last batch uploaded")

        logger.info(f"Combining file to one: {self.file_name}")
        self.s3_client.complete_multipart_upload(
            Bucket=self.bucket_name,
            Key=self.file_name,
            MultipartUpload={"Parts": self.multipart_files},
            UploadId=self.multipart_upload["UploadId"],
        )
