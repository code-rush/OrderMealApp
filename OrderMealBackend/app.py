# -*- coding: utf-8 -*-
# @Author: Japan Parikh
# @Date:   2019-02-16 15:26:12
# @Last Modified by:   Japan Parikh
# @Last Modified time: 2019-04-09 21:38:43


import os
import uuid
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
from pytz import timezone

from flask import Flask, request, render_template
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_mail import Mail, Message

from werkzeug.exceptions import BadRequest
from werkzeug.security import generate_password_hash, \
     check_password_hash

app = Flask(__name__, template_folder='assets')
cors = CORS(app, resources={r'/api/*': {'origins': '*'}})

app.config['MAIL_USERNAME'] = os.environ.get('EMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('PASSWORD')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['DEBUG'] = True


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


def upload_meal_img(file, bucket, key):
    if file and allowed_file(file.filename):
        filename = 'https://s3-us-west-2.amazonaws.com/' \
                   + str(bucket) + '/' + str(key)
        upload_file = s3.put_object(
                            Bucket=bucket,
                            Body=file,
                            Key=key,
                            ACL='public-read',
                            ContentType='image/jpeg'
                        )
        return filename
    return None

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
        created_at = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%dT%H:%M:%S")

        #print(data)
        if data.get('email') == None \
          or data.get('name') == None \
          or data.get('street') == None \
          or data.get('zipCode') == None \
          or data.get('city') == None \
          or data.get('state') == None \
          or data.get('totalAmount') == None \
          or data.get('paid') == None \
          or data.get('paymentType') == None \
          or data.get('order_items') == None \
          or data.get('phone') == None:
            raise BadRequest('Request failed. Please provide all \
                              required information.')

        order_id = uuid.uuid4().hex
        totalAmount= data['totalAmount']

        order_items = [{"M": x} for x in data['order_items']]
        # for item in data['order_items']:
        #     order_items.append({"M": item})


        # try:
        add_order = db.put_item(TableName='meal_orders',
            Item={'order_id': {'S': order_id},
                  'created_at': {'S': created_at},
                  'email': {'S': data['email']},
                  'name': {'S': data['name']},
                  'street': {'S': data['street']},
                  'zipCode': {'N': str(data['zipCode'])},
                  'city': {'S': data['city']},
                  'state': {'S': data['state']},
                  'totalAmount': {'N': str(totalAmount)},
                  'paid': {'BOOL': data['paid']},
                  'paymentType': {'S': data['paymentType']},
                  'order_items':{'L': order_items},
                  'phone': {'S': str(data['phone'])},

            }
        )

        # msg = Message(subject='Order Confirmation',
        #               sender=os.environ.get('EMAIL'),
        #               html=render_template('emailTemplate.html',
        #                    option1=mealOption1, option2=mealOption2,
        #                    totalAmount=totalAmount),
        #               recipients=[data['email']])

        # mail.send(msg)

        response['message'] = 'Request successful'
        return response, 200
        # except:
        #     raise BadRequest('Request failed. Please try again later.')

    def get(self):
        """RETURNS ALL ORDERS PLACED TODAY"""
        response = {}
        todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")
        try:
            orders = db.scan(TableName='meal_orders',
                FilterExpression='order_date = :date',
                ExpressionAttributeValues={
                    ':date': {'S': todays_date}
                }
            )

            response['result'] = orders['Items']
            response['message'] = 'Request successful'
            return response, 200
        except:
            raise BadRequest('Request failed. please try again later.')


class RegisterKitchen(Resource):
    def post(self):
        response = {}
        data = request.get_json(force=True)
        print(data)
        created_at = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%dT%H:%M:%S")

        if data.get('name') == None \
          or data.get('description') == None \
          or data.get('username') == None \
          or data.get('password') == None \
          or data.get('first_name') == None \
          or data.get('last_name') == None \
          or data.get('address') == None \
          or data.get('city') == None \
          or data.get('state') == None \
          or data.get('zipcode') == None \
          or data.get('phone_number') == None \
          or data.get('close_time') == None \
          or data.get('open_time') == None:
            raise BadRequest('Request failed. Please provide all \
                              required information.')

        #TODO1: scan through the kitchen table and filter the results with the kitchen name 
        #      used for signing up. Start by uncommenting the code below.

        # kitchen = db.scan(TableName="")

        # if kitchen.get('Items') != []:
        #     response['message'] = 'This kitchen name is already taken.'
        #     return response, 400

        kitchen_id = uuid.uuid4().hex

        try:
            add_kitchen = db.put_item(TableName='kitchens',
                Item={'kitchen_id': {'S': kitchen_id},
                      'created_at': {'S': created_at},
                      'name': {'S': data['name']},
                      'description': {'S': data['description']},
                      'username': {'S': data['username']},
                      'password': {'S': generate_password_hash(data['password'])},
                      'first_name': {'S': data['first_name']},
                      'last_name': {'S': data['last_name']},
                      'address': {'S': data['address']},
                      'city': {'S': data['city']},
                      'state': {'S': data['state']},
                      'zipcode': {'N': str(data['zipcode'])},
                      'phone_number': {'S': str(data['phone_number'])},
                      'open_time': {'S': str(data['open_time'])},
                      'close_time': {'S': str(data['close_time'])},
                      'isOpen': {'BOOL': False}
                }
            )

            response['message'] = 'Request successful'
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')
            
class Kitchens(Resource):
    def get(self):
        """Returns all kitchens"""
        response = {}


        try:

            openkitchens = db.scan(TableName='kitchens',
                               FilterExpression='isOpen = :value',
                               ExpressionAttributeValues={
                                   ':value': {'BOOL': True}
                               })

            response['message'] = 'Request successful'
            response['result'] = openkitchens['Items']
            print(openkitchens)
            return response, 200
        except Exception as e:
            print(e)
            raise BadRequest('Request failed. Please try again later.')

class Meals(Resource):
#     def post(self, kitchen_id):
#         response = {}

#         #TODO1: Go through the database schema and validate if the all the data
#         #       that is needed to post a meal is provided. If not, then raise a BadRequest Exception


#         #TODO2: create a unique id for the meal

#         try:
#             #TODO3: use put_item method to write data to the meals database table

#             response['message'] = 'Request successful'
#             return response, 201
#         except:
#             raise BadRequest('Request failed. Please try again later.')

    def get(self, kitchen_id):
        response = {}
        # TODO1: get todays date
        todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")
        try:
            # TODO2: scan through the orders table and filter orders by the kitchen id and by today's date
            meals = db.scan(TableName='meals',
                            FilterExpression='kitchen_id = :value and (contains(created_at, :x1))',
                            ExpressionAttributeValues={
                                ':value': {'S': kitchen_id},
                                ':x1': {'S': todays_date}
                            }
                            )
            response['message'] = 'Request successful!'
            response['result'] = meals['Items']
            print(response)
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')

class OrderReport(Resource):
    def get(self, kitchen_id):
        response = {}
        todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")
        k_id = kitchen_id
        try:
            orders = db.scan(TableName='meal_orders',
                FilterExpression='kitchen_id = :value AND order_date = :date',
                ExpressionAttributeValues={
                    ':value': {'S': k_id},
                    ':date': {'S': todays_date}
                }
            )

            response['result'] = orders['Items']
            response['message'] = 'Request successful'
            return response, 200
        except:
            raise BadRequest('Request failed. please try again later.')


api.add_resource(MealOrders, '/api/v1/meal/order')
api.add_resource(TodaysMealPhoto, '/api/v1/meal/image/upload')
api.add_resource(RegisterKitchen, '/api/v1/infinitemeals/kitchens/register')
api.add_resource(Meals, '/api/v1/meals/<string:kitchen_id>')
api.add_resource(OrderReport, '/api/v1/orderreport/<string:kitchen_id>')
api.add_resource(Kitchens, '/api/v1/kitchens')

if __name__ == '__main__':
    app.run()
