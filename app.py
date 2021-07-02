import json
import boto3
from botocore.exceptions import ClientError

# Declaring variables
#success_topic_arn = 'arn:aws:sns:us-east-1:089063229352:com-ebi-nx-success-alerts'
failure_topic_arn = 'arn:aws:sns:us-east-1:052257736952:s3_encrypt'


# SNS Function
def sns_s3_encryption(sns_arn=None, sns_msg=None):
    resource_sns = boto3.client('sns')
    resource_sns.publish(
        TopicArn='{}'.format(sns_arn),
        Message='{}'.format(json.dumps({'default': json.dumps(sns_msg)})),
        Subject='S3 bucket encryption status',
        MessageStructure='json')
    return "success"


def lambda_handler(event, context):
# Initialize or Calling the S3/SNS Resource
    resource_s3 = boto3.client('s3')
    bucketlist = resource_s3.list_buckets()

# For parameter [Buckets] refer https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_buckets
# For get_bucket_encryption parameters(Bucket) refer https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.get_bucket_encryption

    for bucket in bucketlist['Buckets']:
        try:
            encryption = resource_s3.get_bucket_encryption(Bucket=bucket['Name'])
            encrypt_rule = encryption['ServerSideEncryptionConfiguration']
            success_message = 'Bucket : {}, "S3 BUCKETS ARE ENCRYPTED AND COMPLIANT", Encryption_method: {}'.format(
                bucket['Name'], json.dumps(encrypt_rule))
            print(success_message)
            # publish_success_msg = sns_s3_encryption(sns_arn=success_topic_arn, sns_msg=success_message)

        except ClientError as error:
            if error.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                failure_message = 'Bucket: {}, "BUCKET IS NOT ENCRYPTED AND NON_COMPLIANT", Exception: {}'.format(
                    bucket['Name'], error)
                print(failure_message)
                publish_failure_msg = sns_s3_encryption(sns_arn=failure_topic_arn, sns_msg=failure_message)
            else:
                other_message = 'Bucket: {}, "UNEXPECTED ERROR", Other_error: {}'.format(bucket['Name'], error)
                print(other_message)
                publish_other_msg = sns_s3_encryption(sns_arn=failure_topic_arn, sns_msg=other_message)

