import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    file_name = event['file_name']
    bucket_name = 'your-s3-bucket-name'  # Replace with your bucket name
    
    try:
        # Retrieve the .mp4 file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        
        # Return the file content as a response
        file_content = response['Body'].read()
        return {
            'statusCode': 200,
            'body': file_content,
            'headers': {
                'Content-Type': 'video/mp4',
                'Content-Disposition': f'attachment; filename={file_name}'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error retrieving file: {str(e)}'
        }
