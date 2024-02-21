from typing import Optional

import boto3

from openplugin.plugins.models import Config
from openplugin.plugins.port import Port, PortType

from .file_to_cloud import FileToCloud


class FileToCloudWithS3(FileToCloud):
    aws_region: str
    aws_access_key: str
    aws_secret_access_key: str
    bucket_name: str
    save_filename: Optional[str]

    async def process_input(self, input: Port, config: Optional[Config] = None) -> Port:
        # Upload the file
        client = boto3.client(
            "s3",
            region_name=self.aws_region,
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_access_key,
        )
        if self.save_filename is None:
            self.save_filename = input.value
        client.upload_file(input.value, self.bucket_name, self.save_filename)
        path = f"https://{self.bucket_name}.s3.amazonaws.com/{self.save_filename}"
        return Port(
            data_type=PortType.FILEPATH,
            value=path,
        )
