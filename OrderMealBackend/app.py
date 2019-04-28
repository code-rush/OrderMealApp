# -*- coding: utf-8 -*-
# @Author: Japan Parikh
# @Date:   2019-02-16 15:26:12
# @Last Modified by:   Japan Parikh
# @Last Modified time: 2019-04-13 19:41:02


import os
import uuid
import boto3
import json
from datetime import datetime
from pytz import timezone

from flask import Flask, request, render_template
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_mail import Mail, Message

from werkzeug.exceptions import BadRequest, NotFound
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


@app.route('/<string:page_name>/')
def render_static(page_name):
    return render_template('%s.html' % page_name)



# aws s3 bucket where the image is stored
BUCKET_NAME = os.environ.get('MEAL_IMAGES_BUCKET')

# allowed extensions for uploading a profile photo file
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])



# =======HELPER FUNCTIONS FOR UPLOADING AN IMAGE=============
# def upload_file(file, bucket, key):
#     image_uploaded = False

#     if file and allowed_file(file.filename):
#         upload_file = s3.put_object(
#                             Bucket=bucket,
#                             Body=file,
#                             Key=key,
#                             ACL='public-read',
#                             ContentType='image/jpeg'
#                         )
#         image_uploaded = True

#     return image_uploaded


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

# class TodaysMealPhoto(Resource):
#     def post(self):
#         """Uploads image to s3 bucket"""
#         file = request.files['image']
#         response = {}

#         key = datetime.now(tz=timezone('US/Pacific')).strftime("%Y%m%d")

#         try:
#             image_uploaded = upload_file(file, BUCKET_NAME, key)
#             if image_uploaded:
#                 response['message'] = 'File uploaded!'
#             else:
#                 response ['message'] = 'File not allowed!'
#             return response, 200
#         except:
#             raise BadRequest('Request failed. File not uploaded.')


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
          or data.get('phone') == None \
          or data.get('kitchen_id') == None:
            raise BadRequest('Request failed. Please provide all \
                              required information.')

        order_id = uuid.uuid4().hex
        totalAmount = data['totalAmount']
        #Version of order_items submitted to DB
        order_details = []

        for i in data['order_items']:
            item = {}
            item['meal_id'] = {}
            item['meal_id']['S'] = i['meal_id']
            item['qty'] = {}
            item['qty']['N'] = str(i['qty'])
            order_details.append(item)

        order_items = [{"M": x} for x in order_details]

        try:
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
                      'kitchen_id': {'S': str(data['kitchen_id'])}
                }
            )
            
            kitchen = db.get_item(TableName='kitchens',
                Key={'kitchen_id': {'S': data['kitchen_id']}})

            # msg = Message(subject='Order Confirmation',
            #               sender=os.environ.get('EMAIL'),
            #               html=render_template('emailTemplate.html',
            #                    order_items=data['order_items'],
            #                    kitchen=kitchen['Item'],
            #                    totalAmount=totalAmount, name=data['name']),
            #               recipients=[data['email']])

            # mail.send(msg)

            response['message'] = 'Request successful'
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')

    def get(self):
        """RETURNS ALL ORDERS PLACED TODAY"""
        response = {}
        todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")

        try:
            orders = db.scan(TableName='meal_orders',
                FilterExpression='(contains(created_at, :x1))',
                ExpressionAttributeValues={
                    ':x1': {'S': todays_date}
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

        name = request.form['name']
        description = request.form['description']
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zipcode']
        phone_number = request.form['phone_number']
        close_time = request.form['close_time']
        open_time = request.form['open_time']

        created_at = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%dT%H:%M:%S")

        if name == None \
          or description == None \
          or username == None \
          or password == None \
          or first_name == None \
          or last_name == None \
          or address == None \
          or city == None \
          or state == None \
          or zipcode == None \
          or phone_number == None \
          or close_time == None \
          or open_time == None:
            raise BadRequest('Request failed. Please provide all \
                              required information.')

        # # scan to check if the kitchen name exists
        # kitchen = db.scan(TableName="kitchens",
        #     FilterExpression='name = :val',
        #     ExpressionAttributeValues={
        #         ':val': {'S': name}
        #     }
        # )
        #
        # # raise exception if the kitchen name already exists
        # if kitchen.get('Items') != []:
        #     response['message'] = 'This kitchen name is already taken.'
        #     return response, 400

        kitchen_id = uuid.uuid4().hex

        try:
            add_kitchen = db.put_item(TableName="kitchens",

                Item={"kitchen_id": {"S": kitchen_id},
                      "created_at": {"S": created_at},
                      "name": {"S": str(name)},
                      "description": {"S": str(description)},
                      "username": {"S": str(username)},
                      "password": {"S": generate_password_hash(password)},
                      "first_name": {"S": str(first_name)},
                      "last_name": {"S": str(last_name)},
                      "address": {"S": str(address)},
                      "city": {"S": str(city)},
                      "state": {"S": str(state)},
                      "zipcode": {"N": str(zipcode)},
                      "phone_number": {"S": str(phone_number)},
                      "open_time": {"S": str(open_time)},
                      "close_time": {"S": str(close_time)},
                      "isOpen": {"BOOL": False}
                      #'email': {'S': str(email)}
                }
            )

            response['message'] = 'Request successful'
            print('request sent')
            return response, 200
        except Exception as e:
            print(e)
            raise BadRequest('Request failed. Please try again later.')
            
class Kitchens(Resource):
    def get(self):
        """Returns all kitchens"""
        response = {}

        try:
            openkitchens = db.scan(TableName='kitchens',
                FilterExpression='isOpen = :value',
                ProjectionExpression='#kitchen_name, kitchen_id, close_time, description',
                ExpressionAttributeNames={
                    '#kitchen_name': 'name'
                },
                ExpressionAttributeValues={
                    ':value': {'BOOL': True}
                }
            )

            response['message'] = 'Request successful'
            response['result'] = openkitchens['Items']
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')

class Meals(Resource):
    def post(self, kitchen_id):
        response = {}

        if request.form.get('name') == None \
          or request.form.get('items') == None \
          or request.form.get('price') == None:
            raise BadRequest('Request failed. Please provide required details.')

        meal_id = uuid.uuid4().hex
        created_at = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%dT%H:%M:%S")

        meal_items = json.loads(request.form['items'])

        items = []
        for i in meal_items['meal_items']:
            item = {}
            item['title'] = {}
            item['title']['S'] = i['title']
            item['qty'] = {}
            item['qty']['N'] = str(i['qty'])
            items.append(item)

        description = [{'M': i} for i in items]

        try:
            photo_key = 'meals_imgs/{}_{}'.format(str(kitchen_id), str(meal_id))
            photo_path = upload_meal_img(request.files['photo'], BUCKET_NAME, photo_key)

            if photo_path == None:
                raise BadRequest('Request failed. \
                    Something went wrong uploading a photo.')

            add_meal = db.put_item(TableName='meals',
                Item={'meal_id': {'S': meal_id},
                      'created_at': {'S': created_at},
                      'kitchen_id': {'S': str(kitchen_id)},
                      'meal_name': {'S': str(request.form['name'])},
                      'description': {'L': description},
                      'price': {'S': str(request.form['price'])},
                      'photo': {'S': photo_path}
                }
            )

            kitchen = db.update_item(TableName='kitchens',
                Key={'kitchen_id': {'S': str(kitchen_id)}},
                UpdateExpression='SET isOpen = :val',
                ExpressionAttributeValues={
                    ':val': {'BOOL': True}
                }
            )

            response['message'] = 'Request successful'
            return response, 201
        except:
            raise BadRequest('Request failed. Please try again later.')

    def get(self, kitchen_id):
        response = {}
        todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")
        
        try:
            meals = db.scan(TableName='meals',
                FilterExpression='kitchen_id = :value and (contains(created_at, :x1))',
                ExpressionAttributeValues={
                    ':value': {'S': kitchen_id},
                    ':x1': {'S': todays_date}
                }
            )

            for meal in meals['Items']:
                description = ''

                for item in meal['description']['L']:
                    if int(item['M']['qty']['N']) > 1:
                        description = description + item['M']['qty']['N'] + ' ' \
                                     + item['M']['title']['S'] + ', '
                    else:
                        description = description + item['M']['title']['S'] + ', '

                del meal['description']
                meal['description'] = {}
                meal['description']['S'] = description

            response['message'] = 'Request successful!'
            response['result'] = meals['Items']
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
                FilterExpression='kitchen_id = :value AND (contains(created_at, :x1))',
                ExpressionAttributeValues={
                    ':value': {'S': k_id},
                    ':x1': {'S': todays_date}
                }
            )

            response['result'] = orders['Items']
            response['message'] = 'Request successful'
            return response, 200
        except:
            raise BadRequest('Request failed. please try again later.')


class KitchenSignIn(Resource):
    def post(self):
        response = {}
        data = request.get_json(force=True)

        if data.get('email') == None:
            raise BadRequest('Request failed. Please provide email.')

        try:
            user = db.query(TableName="kitchens",
                IndexName='email-index',
                Limit=1,
                KeyConditionExpression='email = :val',
                ExpressionAttributeValues={
                    ':val': {'S': data['email']}
                }
            )

            if user.get('Item') == None:
                raise NotFound('User not found.')

            response['message'] = 'Request successful!'
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')


api.add_resource(MealOrders, '/api/v1/orders')
# api.add_resource(TodaysMealPhoto, '/api/v1/meal/image/upload')
api.add_resource(RegisterKitchen, '/api/v1/kitchens/register')
api.add_resource(Meals, '/api/v1/meals/<string:kitchen_id>')
api.add_resource(OrderReport, '/api/v1/orders/report/<string:kitchen_id>')
api.add_resource(Kitchens, '/api/v1/kitchens')
api.add_resource(KitchenSignIn, '/api/v1/kitchens/sign_in')

if __name__ == '__main__':
    app.run()
