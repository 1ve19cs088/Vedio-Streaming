import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = 'your-s3-bucket-name'  # Replace with your bucket name
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        video_files = []
        for obj in response.get('Contents', []):
            video_files.append({"fileName": obj['Key']})

        return {
            'statusCode': 200,
            'body': video_files
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error fetching video list: {str(e)}'
        }
