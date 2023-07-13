import os
import sys
from uuid import uuid4

import paramiko

script_dir = os.path.dirname(__file__)
path_range = "../" * 3 + ".."
mymodule_dir = os.path.join(script_dir, path_range)
sys.path.append(mymodule_dir)

from datapipes_images_utils.file_utils.utils import create_temp_file
from datapipes_images_utils.logger_utils.module_logger import get_module_logger
from datapipes_model.sftp.secrets import SFTPSecrets, SFTPSecretType

logger = get_module_logger(__name__)

PRIVATE_KEY_PATH = f"{os.getcwd()}/private_key_{uuid4()}"


class SftpBufferReader:
    def __init__(self, source_config: SFTPSecrets) -> None:
        self.hostname = source_config.hostname
        self.username = source_config.username
        self.secret = source_config.secret
        self.secret_type = source_config.secret_type
        self.port = source_config.port
        self.sftp_client = self.get_client()
        logger.info(f"Opened sftp connection for host:{self.hostname}")

    def get_client(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.secret_type == SFTPSecretType.PRIVATE_KEY:
            private_key_path = create_temp_file(
                self.secret.get_secret_value(), PRIVATE_KEY_PATH
            )
            kwargs = {"key_filename": private_key_path}
        else:
            kwargs = {"password": self.secret.get_secret_value()}
        ssh_client.connect(
            hostname=self.hostname, username=self.username, port=self.port, **kwargs
        )
        return ssh_client.open_sftp()

    def read(self, remote_file_path: str, buffer_size: int = 5 * 1024 * 1024):
        logger.info(f"Reading buffer stream with size: {buffer_size}")
        with self.sftp_client.open(remote_file_path, "rb") as sftp_file:
            while True:
                data = sftp_file.read(buffer_size)
                if not data:
                    break
                yield data
