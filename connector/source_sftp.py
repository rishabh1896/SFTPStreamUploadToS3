import argparse
import os
import sys

script_dir = os.path.dirname(__file__)
path_range = "../" * 3
mymodule_dir = os.path.join(script_dir, path_range)
sys.path.append(mymodule_dir)

from buffer_reader.reader import SftpBufferReader
from model.schema import ReadConfig
from utils.s3.s3 import S3BufferUploads

from datapipes_images_utils.file_utils.utils import read_config_file
from datapipes_images_utils.logger_utils.module_logger import get_module_logger

logger = get_module_logger(__name__)


class SourceSftp:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        config = read_config_file(args.config)
        self.config = ReadConfig(**config)
        logger.info(f"Config:{self.config}")

    def read(self):
        sftp_reader = SftpBufferReader(self.config.source.secret)
        s3_buffer_upload = S3BufferUploads(
            self.config.destination, self.config.source.file_type
        )

        logger.info(f"Starting SFTP read for file path:{self.config.source.file_path}")
        for stream in sftp_reader.read(
            self.config.source.file_path, self.config.stream_config.read_buffer
        ):

            if s3_buffer_upload.check_buffer_limit(
                self.config.stream_config.upload_buffer
            ):
                s3_buffer_upload.buffer_uploads()
            s3_buffer_upload.write_buffer(stream)

        s3_buffer_upload.upload_last_buffer()
