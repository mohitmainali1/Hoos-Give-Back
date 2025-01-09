from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False

class ProjectStorage(S3Boto3Storage):
    location = ''

    def __init__(self, project_id, *args, **kwargs):
        self.location = f'projects/{project_id}'
        super().__init__(*args, **kwargs)