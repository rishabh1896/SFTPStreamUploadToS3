# Datapipes SFTP and S3 Upload.
This image reads data from sftp server as a stream and uploads it s3 in binary stream of provided buffer size. By default it reads sftp stream in buffer of 5MB and uploads to s3 in 10MB buffer. S3 upload is multipart and thus results in single on s3.

## Image definitions in prod.
`sourceDefinitionId`: datapipes-sftp-source-to-s3
`name`: Datapipes Sftp Binary Stream Reader to S3
`dockerRepository`: asia.gcr.io/cc-datapipes-production/datapipes-airbyte/datapipes-sftp-source-to-s3
`dockerImageTag`: 0.0.2
`documentationUrl`: https://cldcvr.atlassian.net/l/c/mFyL2Z1w


## Steps to build image
1. `docker buildx build --platform linux/amd64 --load -t datapipes-sftp-source-to-s3:latest -f datapipes_airbyte_images/SFTPSourceConnector/connector/DockerFile .`
2. `docker tag s3_normalise_file_upload:latest <dockerRepository>:<new_version>`
3. `docker push <dockerRepository>:<new_version>`

## Steps to run on local machine.
1. command for python terminal: 
    `python3 $(pwd)/datapipes_docker_images/datapipes_airbyte_images/SFTPSourceConnector/connector/main.py read --config <path_to_config_file>`

## ChangeLog
- 0.0.1: Initial release to stream data from sftp server to s3.
- 0.0.2: Bug fix to get secret value for password auth.