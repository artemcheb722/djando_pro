import uuid
import boto3
from django.conf import settings


def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name='auto',
    )


def upload_book_image(file):
    ext = file.name.split('.')[-1]
    key = f'books/{uuid.uuid4()}.{ext}'

    client = get_s3_client()
    client.upload_fileobj(
        file,
        settings.R2_BUCKET_NAME,
        key,
        ExtraArgs={'ContentType': file.content_type}
    )

    return f'{settings.R2_PUBLIC_URL}/{key}'