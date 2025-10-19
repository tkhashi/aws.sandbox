import json
import random
import boto3
import base64
import uuid
from io import BytesIO
from botocore.config import Config

bedrock_runtime = boto3.client('bedrock-runtime')
# 署名プロセスには、署名バージョン4(SigV4)を指定
# モデルはus-east-1だがS3はap-northeast-1
my_config = Config(region_name="ap-northeast-1", signature_version="s3v4") 
s3 = boto3.client("s3", config=my_config)
bucket_name = 'get-started-bedrock'

def lambda_handler(event, context):
    # CORS対応のヘッダー設定
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    }
    
    # OPTIONSリクエスト（プリフライト）の場合
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'CORS preflight'})
        }
    
    try:
        # POSTリクエストのボディからinput_textを取得
        if event.get('body'):
            body = json.loads(event['body'])
            input_text = body.get('input_text')
        else:
            input_text = event.get('input_text')
        
        if not input_text:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'input_text is required'})
            }
            
        seed = random.randint(0, 2147483647)
        native_request = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": input_text},
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": "standard",
                "cfgScale": 8.0,
                "height": 512,
                "width": 512,
                "seed": seed,
            },
        }
        request = json.dumps(native_request)

        # 実行
        response = bedrock_runtime.invoke_model(
            modelId='amazon.titan-image-generator-v1',
            body=request
        )

        # レスポンスから画像データを取得
        model_response = json.loads(response["body"].read())
        base64_image_data = model_response["images"][0]
        image_data = base64.b64decode(base64_image_data)
        image_file = BytesIO(image_data)

        # 生成された画像をS3にアップロード    
        random_uuid = uuid.uuid4().hex 
        s3_key = random_uuid + '.png'
        s3.upload_fileobj(
            image_file,
            bucket_name,
            s3_key,
            ExtraArgs={'ContentType': 'image/png'}
        )
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name,'Key': s3_key},
            ExpiresIn=3600
        ) 
        
        # 署名付きURLを返す（API Gateway形式のレスポンス）
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'presigned_url': presigned_url})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': str(e)})
        }