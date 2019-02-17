# -*- coding: utf-8 -*-
# @Author: Japan Parikh
# @Date:   2019-02-16 15:26:12
# @Last Modified by:   Japan Parikh
# @Last Modified time: 2019-02-16 18:04:36


import os
import uuid
import boto3
import datetime

from flask import Flask, request
from flask_mail import Mail, Message
from flask_restful import Resource, Api

from werkzeug.exceptions import BadRequest

app = Flask(__name__)

app.config['MAIL_USERNAME'] = os.environ.get('EMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('PASSWORD')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['DEBUG'] = True

api = Api(app)
mail = Mail(app)


db = boto3.client('dynamodb')
s3 = boto3.client('s3')


# aws s3 bucket where the image is stored
BUCKET_NAME = os.environ.get('MEAL_IMAGES_BUCKET')

# allowed extensions for uploading a profile photo file
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])



# =======HELPER FUNCTIONS FOR UPLOADING AN IMAGE=============
def upload_file(file, bucket, key):
    image_uploaded = False

    if file and allowed_file(file.filename):
        upload_file = s3.put_object(
                            Bucket=bucket,
                            Body=file,
                            Key=key,
                            ACL='public-read',
                            ContentType='image/jpeg'
                        )
        image_uploaded = True

    return image_uploaded

def allowed_file(filename):
    """Checks if the file is allowed to upload"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===========================================================

class TodaysMealPhoto(Resource):
    def post(self):
        """Uploads image to s3 bucket"""
        file = request.files['image']
        response = {}

        key = 'meal_image'

        try:
            image_uploaded = upload_file(file, BUCKET_NAME, key)
            if image_uploaded:
                response['message'] = 'File uploaded!'
            else:
                response ['message'] = 'File not allowed!'
            return response, 200
        except:
            raise BadRequest('Request failed. File not uploaded.')


class MealOrders(Resource):
    def post(self):
        """Collects the information of the order
           and stores it to the database.
        """
        response = {}
        data = request.get_json(force=True)
        order_date = datetime.datetime.now().strftime("%Y-%m-%d")
        order_time = datetime.datetime.now().strftime("%H:%M:%S")

        if request.get('email') == None \
          or request.get('name') == None \
          or request.get('street') == None \
          or request.get('zipCode') == None \
          or request.get('city') == None \
          or request.get('state') == None \
          or request.get('totalAmount') == None \
          or request.get('paid') == None \
          or request.get('paymentType') == None \
          or request.get('deliveryTime') == None \
          or request.get('mealOption1') == None \
          or request.get('mealOption2') == None:
            raise BadRequest('Request failed. Please provide all \
                              required information.')

        order_id = uuid.uuid4().hex

        try:
            add_order = db.put_item(TableName='meal_orders',
                Item={'order_id': {'S': order_id},
                      'order_date': {'S': order_date},
                      'order_time': {'S': order_time},
                      'email': {'S': request['email']},
                      'name': {'S': request['name']},
                      'street': {'S': request['street']},
                      'zipCode': {'N': request['zipCode']},
                      'city': {'S': request['city']},
                      'state': {'S': request['state']},
                      'totalAmount': {'N': request['totalAmount']},
                      'paid': {'BOOL': request['paid']},
                      'paymentType': {'S': request['paymentType']},
                      'deliveryTime': {'S': request['deliveryTime']},
                      'mealOption1': {'N': request['mealOption1']},
                      'mealOption2': {'N': request['mealOption2']}
                }
            )

            response['message'] = 'Request successful'
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')


api.add_resource(MealOrders, '/api/v1/meal/order')
api.add_resource(TodaysMealPhoto, '/api/v1/meal/image/upload')

if __name__ == '__main__':
    app.run()