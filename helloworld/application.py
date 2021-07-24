#!flask/bin/python
import json
from flask import Flask, Response
from flask import request
from helloworld.flaskrun import flaskrun
import base64
import boto3
import os
import io
from flask_cors import CORS, cross_origin

application = Flask(__name__)
cors = CORS(application)

@application.route('/', methods=['GET'])
@cross_origin()
def get():
    try:
        return Response(json.dumps({'status': 'unautherized access'}), mimetype='application/json', status=200)

    except Exception as e:
            return Response(json.dumps({'status': 'unautherized access'}), mimetype='application/json', status=200)


@application.route('/', methods=['POST'])
@cross_origin()
def post():
    try:
        request_data = request.get_json()
        image = request_data.get('image', '')
        msg = base64.b64decode(image)
        
        try:
            client = boto3.client('dynamodb', region_name='us-east-2')
            data = client.scan(
                        TableName='hr-prediction-image-sample'
                    )
            data = json.dumps(data)
            data = json.loads(data)["Items"]
        except Exception as e:
            data = []
            
        final_data = []
        
        for x in data:
            s3_connection = boto3.resource('s3')
            s3_object = s3_connection.Object("hr-prediction-image-collection", x["image_path"]["S"])
            s3_response = s3_object.get()
            
            stream = io.BytesIO(s3_response['Body'].read())
            
            stream2 = io.BytesIO(msg)
            resp = compare_faces(stream2, stream)
            
            if len(resp):
                final_data.append({
                    "similarity": resp,
                    "user_data": x
                })
                
        return Response(json.dumps({'status': 'success', 'data': final_data}), mimetype='application/json', status=200)

    except Exception as e:
            return Response(json.dumps({'status': 'failed', 'data': str(e)}), mimetype='application/json', status=200)



def compare_faces(sourceFile, targetFile):
    try:
        client=boto3.client('rekognition', region_name='us-east-2')
    
    
        response=client.compare_faces(SimilarityThreshold=80,
                                      SourceImage={'Bytes': sourceFile.read()},
                                      TargetImage={'Bytes': targetFile.read()})
        
        print(response)
        for faceMatch in response['FaceMatches']:
            position = faceMatch['Face']['BoundingBox']
            similarity = str(faceMatch['Similarity'])
            print('The face at ' +
                   str(position['Left']) + ' ' +
                   str(position['Top']) +
                   ' matches with ' + similarity + '% confidence')
    
        print(response['FaceMatches'])
        return (response['FaceMatches'])   
    except Exception as e:
        return "0"




if __name__ == '__main__':
    flaskrun(application)
