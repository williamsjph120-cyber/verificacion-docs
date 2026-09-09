import boto3
import uuid
from io import BytesIO
from src.config.settings import settings


class StorageService:
    def __init__(self):
        self._s3 = None
        self.bucket = settings.R2_BUCKET_NAME

    @property
    def s3(self):
        if self._s3 is None:
            self._s3 = boto3.client(
                "s3",
                endpoint_url=settings.R2_ENDPOINT_URL or f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                region_name="auto",
            )
        return self._s3

    def upload_file(self, file_data: BytesIO, filename: str, content_type: str = "application/pdf") -> str:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "pdf"
        key = f"documents/{uuid.uuid4()}.{ext}"

        self.s3.upload_fileobj(
            file_data,
            self.bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )
        return key

    def upload_qr(self, qr_data: BytesIO, document_token: str) -> str:
        key = f"qr-codes/{document_token}.png"

        self.s3.upload_fileobj(
            qr_data,
            self.bucket,
            key,
            ExtraArgs={"ContentType": "image/png"},
        )
        return key

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def delete_file(self, key: str):
        self.s3.delete_object(Bucket=self.bucket, Key=key)


storage = StorageService()
