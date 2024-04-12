=================
File To Cloud
=================

File to Cloud Processor is a processor that uploads a file from the local system to a cloud storage service. It facilitates the transfer of files to the cloud, making them accessible from remote locations.

**Supported Input Port:**

filepath: The File to Cloud Processor accepts input through the "filepath" port. The input should be the file path of the local file that needs to be uploaded to the cloud.

**Supported Output Port:**

filepath: The processor produces output through the "filepath" port. The output is the file path of the uploaded file in the cloud storage.

List of Implementations:
===========================

S3 Implementation
----------------------------

The S3 implementation of the File to Cloud Processor utilizes Amazon S3 (Simple Storage Service) to upload files to the cloud.

**Metadata**

.. list-table::
   :widths: 15 20 10 10 45
   :header-rows: 1

   * - Field
     - Type
     - Required
     - User Provided
     - Description
   * - aws_region
     - string
     - Yes
     - Yes
     - The AWS region where the S3 bucket is located.
   * - aws_access_key
     - string
     - Yes
     - Yes
     - The access key for authenticating with AWS.
   * - aws_secret_access_key
     - string
     - Yes
     - Yes
     - The secret access key for authenticating with AWS.
   * - bucket_name
     - string
     - No
     - Yes
     - The name of the S3 bucket where the file will be uploaded. The default value is "openplugin-output".
   * - save_filename
     - string
     - No
     - No
     - The name of the file when saved in the cloud storage. The default value is "response.txt".


Sample processor configuration:
----------------------------------

NOTE: Processor is always added to a module(Input or Output). The module is then added to the pipeline.


.. code-block:: json

     {
        "processor_type": "file_to_cloud",
        "processor_implementation_type": "file_to_cloud_with_s3",
        "input_port": "filepath",
        "output_port": "filepath",
        "metadata": {},
    }
