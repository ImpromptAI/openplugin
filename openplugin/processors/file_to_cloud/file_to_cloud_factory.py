from openplugin.processors import ProcessorImplementationType

from .file_to_cloud import FileToCloud


def get_file_to_cloud(
    implementation_type: ProcessorImplementationType, metadata: dict
) -> FileToCloud:
    if implementation_type == ProcessorImplementationType.FILE_TO_CLOUD_WITH_S3:
        from .file_to_cloud_with_s3 import FileToCloudWithS3

        return FileToCloudWithS3(**metadata)
    else:
        raise ValueError("Invalid implementation type: {}".format(implementation_type))
