from ml_model_consume.helpers.constants import LINODE_OBJECT_STORAGE_URL
import os
import json
import logging
import boto
import boto.s3.connection

logger = logging.getLogger()

access_key, secret_key = None, None

if os.path.isfile("/etc/config.json"):
    with open("/etc/config.json") as config_file:
        config = json.load(config_file)
        logger.info("Production Deployment!!")
        access_key = config.get("LINODE_OBJECT_STORAGE_ACCESS_KEY")
        secret_key = config.get("LINODE_OBJECT_STORAGE_SECRET_KEY")
else:
    access_key = os.environ.get("LINODE_OBJECT_STORAGE_SECRET_KEY")
    secret_key = os.environ.get("LINODE_OBJECT_STORAGE_SECRET_KEY")


conn = boto.connect_s3(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    host=LINODE_OBJECT_STORAGE_URL,
    # is_secure=False,               # uncomment if you are not using ssl
    calling_format=boto.s3.connection.OrdinaryCallingFormat(),
)


class LinObjStoClient:
    def __init__(self) -> None:
        (
            self.bucket_obj,
            self.object_obj,
            self.bucket_name,
            self.object_name,
        ) = (
            None,
            None,
            "",
            "",
        )

    def get_bucket_by_name(self):
        for bucket in conn.get_all_buckets():
            if bucket.name == self.bucket_name:
                logger.info("Bucket object found")
                self.bucket_obj
                break
        else:
            logger.info("bucket name not found!")

    def get_object_from_bucket(self):
        self.object_obj = self.bucket_obj.get_key(self.object_name)
        logger.info(f"Got the object - {self.object_obj.name}")

    def load_model(self, bucket_name, object_name):
        self.bucket_name, self.object_name = bucket_name, object_name

        # self.get_bucket_by_name()
        # self.get_object_from_bucket()
