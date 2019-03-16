# -*- coding: utf-8 -*-
# @Author: Japan Parikh
# @Date:   2019-02-16 15:26:12
# @Last Modified by:   Japan Parikh
# @Last Modified time: 2019-03-14 19:25:12


import os
import uuid
import boto3
from datetime import datetime
from pytz import timezone

from flask import Flask, request, render_template
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_mail import Mail, Message

from werkzeug.exceptions import BadRequest

app = Flask(__name__, template_folder='assets')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['MAIL_USERNAME'] = os.environ.get('EMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('PASSWORD')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['DEBUG'] = False


mail = Mail(app)
api = Api(app)


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

        key = datetime.now(tz=timezone('US/Pacific')).strftime("%Y%m%d")

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
        order_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")
        order_time = datetime.now(tz=timezone('US/Pacific')).strftime("%H:%M:%S")

        if data.get('email') == None \
          or data.get('name') == None \
          or data.get('street') == None \
          or data.get('zipCode') == None \
          or data.get('city') == None \
          or data.get('state') == None \
          or data.get('totalAmount') == None \
          or data.get('paid') == None \
          or data.get('paymentType') == None \
          or data.get('mealOption1') == None \
          or data.get('mealOption2') == None \
          or data.get('phone') == None:
            raise BadRequest('Request failed. Please provide all \
                              required information.')

        order_id = uuid.uuid4().hex
        mealOption1 = data['mealOption1']
        mealOption2 = data['mealOption2']
        totalAmount = data['totalAmount']

        try:
            add_order = db.put_item(TableName='meal_orders',
                Item={'order_id': {'S': order_id},
                      'order_date': {'S': order_date},
                      'order_time': {'S': order_time},
                      'email': {'S': data['email']},
                      'name': {'S': data['name']},
                      'street': {'S': data['street']},
                      'zipCode': {'N': str(data['zipCode'])},
                      'city': {'S': data['city']},
                      'state': {'S': data['state']},
                      'totalAmount': {'N': str(totalAmount)},
                      'paid': {'BOOL': data['paid']},
                      'paymentType': {'S': data['paymentType']},
                      'mealOption1': {'N': str(mealOption1)},
                      'mealOption2': {'N': str(mealOption2)},
                      'phone': {'S': str(data['phone'])}
                }
            )
            
            msg = Message(subject='Order Confirmation',
                          sender=os.environ.get('EMAIL'),
                          html=render_template('emailTemplate.html',
                               option1=mealOption1, option2=mealOption2,
                               totalAmount=totalAmount),
                          recipients=[data['email']])

            mail.send(msg)

            response['message'] = 'Request successful'
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')

    def get(self):
        """Returns todays meal orders"""
        response = {}
        todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")

        try:
            orders = db.scan(TableName='meal_orders',
                FilterExpression='order_date = :value',
                ExpressionAttributeValues={
                    ':value': {'S': todays_date}
                }
            )

            response['result'] = orders['Items']
            response['message'] = 'Request successful'
            return response, 200
        except:
            raise BadRequest('Request failed. please try again later.')
    


api.add_resource(MealOrders, '/api/v1/meal/order')
api.add_resource(TodaysMealPhoto, '/api/v1/meal/image/upload')


if __name__ == '__main__':
    app.run()