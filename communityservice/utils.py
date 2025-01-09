import boto3

from django.conf import settings

def generate_presigned_url(project_id, file_name, expiration=3600):
    s3_client = boto3.client('s3',
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    return s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': f'projects/{project_id}/{file_name}'
        },
        ExpiresIn=expiration
    )