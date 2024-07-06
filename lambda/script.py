import json
import boto3
from urllib.parse import urlparse, unquote

# Configure AWS SDK
s3 = boto3.client('s3')
sqs = boto3.client('sqs')

def handler(event, context):
    for record in event['Records']:
        # Parse the SQS message body
        message_body = json.loads(record['body'])
        s3_url = message_body['s3Url']

        try:
            # Extract the bucket name and key from the S3 URL
            url = urlparse(s3_url)
            bucket_name = url.netloc.split('.')[0]
            key = unquote(url.path.lstrip('/'))

            # Fetch the video from S3
            params = {
                'Bucket': bucket_name,
                'Key': key
            }
            data = s3.get_object(**params)

            # Process the video (for example, logging its size)
            print(f'Fetched video from S3: {key}')
            print(f'Video size: {data["ContentLength"]} bytes')

            # You can add additional processing here, such as saving the video to another location or performing some analysis

        except Exception as error:
            print('Error fetching video from S3:', error)

# Example usage
if __name__ == "__main__":
    # Test event
    event = {
        "Records": [
            {
                "body": json.dumps({"s3Url": "https://example-bucket.s3.amazonaws.com/path/to/video.mp4"})
            }
        ]
    }
    handler(event, None)
