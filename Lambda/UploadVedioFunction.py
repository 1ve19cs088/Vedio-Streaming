import boto3
import re

s3 = boto3.client('s3')

# Lambda function to validate and upload .mp4 file
def lambda_handler(event, context):
    # Assuming the event contains the file details in a JSON format
    file_name = event['file_name']
    file_content = event['file_content']
    bucket_name = 'your-s3-bucket-name'  # Replace with your bucket name
    
    # Validate the file extension
    if not re.match(r'.*\.mp4$', file_name):
        return {
            'statusCode': 400,
            'body': 'Invalid file type. Only .mp4 files are allowed.'
        }
    
    # Upload the file to S3
    try:
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)
        return {
            'statusCode': 200,
            'body': f'File {file_name} uploaded successfully.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error uploading file: {str(e)}'
        }
