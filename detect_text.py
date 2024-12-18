import json
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    
    print(f"Event: {event}")

    # Get the object key and bucket name from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # Extract the file name from the object key
    file_name = object_key.split('/')[-1]
    file_name = file_name.split('.')[0]

    print("File name: ", file_name)
    
    # Set up the S3 client to use the same bucket for input and output
    s3_output = boto3.resource('s3').Bucket(bucket_name)
    
    # Get the input file from the 'images' folder
    input_obj = s3.get_object(Bucket=bucket_name, Key=object_key)
    input_stream = input_obj['Body'].read()

    if len(input_stream) == 0:
        return {
            'statusCode': 400,
            'body': 'Error: The input stream is empty.'
        }
        
    # Use the Rekognition service to detect text in the image
    rekognition = boto3.client('rekognition')
    response = rekognition.detect_text(
        Image={
            'Bytes': input_stream
        }
    )
        
    folder_name = 'responses/'
    # Write the response to a JSON file with the same name as the uploaded file
    json_response = json.dumps(response)
    output_obj = s3_output.Object(bucket_name=bucket_name, key=f'{folder_name}{file_name}.json')
    output_obj.put(Body=json.dumps(response, indent=2))
    
    return {
        'statusCode': 200,
        'body': json.dumps(response, indent=2)
    }