import os
import sys
from enum import Enum
from typing import Optional

from pydantic import BaseModel, SecretStr

script_dir = os.path.dirname(__file__)
path_range = "../" * 5

mymodule_dir = os.path.join(script_dir, path_range)
sys.path.append(mymodule_dir)

from datapipes_model.aws.secrets import AwsSecrets
from datapipes_model.sftp.secrets import SFTPSecrets


class SupportedFileTypes(str, Enum):
    PARQUET = "PARQUET"
    JSON = "JSON"
    JSONL = "JSONL"
    CSV = "CSV"


class MimeType(str, Enum):
    PARQUET = "parquet"


class SFTPSource(BaseModel):
    secret: SFTPSecrets
    file_path: str
    file_type: SupportedFileTypes


class S3BufferUploadDestination(BaseModel):
    bucket_name: str
    file_name: str
    secret: AwsSecrets


class StreamConfig(BaseModel):
    read_buffer: int = 5242880
    upload_buffer: int = 10485760


class ReadConfig(BaseModel):
    source: SFTPSource
    destination: S3BufferUploadDestination
    stream_config: Optional[StreamConfig] = StreamConfig()
