# -*- coding: utf-8 -*-
# @Author: Japan Parikh
# @Date:   2019-05-24 19:40:12
# @Last Modified by:   Japan Parikh
# @Last Modified time: 2019-06-09 13:37:30


import string
import random
import boto3
import json
import uuid
import requests

from datetime import datetime
from pytz import timezone

from flask import (Flask, Blueprint, request, render_template, 
    redirect, url_for, flash)
from flask import session as login_session
from flask_login import (LoginManager, login_required, current_user, 
	UserMixin, login_user, logout_user)
from flask_mail import Mail, Message

from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.security import (generate_password_hash, 
    check_password_hash)


app = Flask(__name__, static_folder='static', template_folder='templates')

login_manager = LoginManager(app)

secret_key = 'app_secret_key'

app.config['SECRET_KEY'] = secret_key
app.config['MAIL_USERNAME'] = 'infiniteoptions.meals@gmail.com'
app.config['MAIL_PASSWORD'] = 'annApurna'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

AWS_KEY_ID = 'aws-key-id'
AWS_SECRET_KEY = 'aws-secret-access-key'

db = boto3.client('dynamodb', 
          region_name='us-west-2',
          aws_access_key_id=AWS_KEY_ID,
          aws_secret_access_key=AWS_SECRET_KEY)

s3 = boto3.client('s3',
    aws_access_key_id=AWS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_KEY)


# aws s3 bucket where the image is stored
BUCKET_NAME = 'ordermealapp'

API_BASE_URL = 'https://o5yv1ecpk1.execute-api.us-west-2.amazonaws.com/dev/'

# allowed extensions for uploading a profile photo file
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])



# =======HELPER FUNCTIONS FOR UPLOADING AN IMAGE=============

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


class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        return User(user_id)


@login_manager.user_loader
def _login_manager_load_user(user_id):
    return User.get(user_id)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/accounts/logout')
@login_required
def logout():
    del login_session['user_id']
    del login_session['name']
    logout_user()
    return redirect(url_for('index'))


@app.route('/accounts', methods=['GET', 'POST'])
@app.route('/accounts/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in login_session:
        return redirect(url_for('kitchen', id=login_session['user_id']))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Enter an email and password')
            return render_template('login.html')

        try:
            user = db.query(TableName="kitchens",
                IndexName='email-index',
                Limit=1,
                KeyConditionExpression='email = :val',
                ExpressionAttributeValues={
                    ':val': {'S': email}
                }
            )

            if user.get('Count') == 0:
                flash('User not found.')
                return render_template('login.html')

            if not check_password_hash(user['Items'][0]['password']['S'], \
              password):
                flash('Password is incorrect.')
                return render_template('login.html')
            else:
                user_id = user['Items'][0]['kitchen_id']['S']
                login_session['name'] = user['Items'][0]['name']['S']
                login_session['user_id'] = user_id
                login_user(User(user_id))
                return redirect(url_for('kitchen', \
                        id=user_id))

        except:
            flash('Password is incorrect.')
            return render_template('login.html')

    return render_template('login.html')



@app.route('/accounts/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        verifyPassword = request.form.get('verify-password')
        username = request.form.get('username')
        firstName = request.form.get('first_name')
        lastName = request.form.get('last_name')
        kitchenName = request.form.get('name')
        phoneNumber = request.form.get('phone_number')
        closeTime = request.form.get('close_time')
        openTime = request.form.get('open_time')
        zipcode = request.form.get('zipcode')
        state = request.form.get('state')
        city = request.form.get('city')
        street = request.form.get('address')
        description = request.form.get('description')

        if email == None or password == None or verifyPassword == None \
          or username == None or firstName == None or lastName == None \
          or kitchenName == None or phoneNumber == None or closeTime == None \
          or openTime == None or zipcode == None or state == None or city == None \
          or street == None or description == None:
            flash('Please fill in all the required fields')
            return render_template('register.html')
        
        if verifyPassword != password:
            flash('Your passwords don\'t match')
            return render_template('register.html')

        request_data = {'email': email, 'password': password, 
                        'username': username, 'first_name': firstName,
                        'last_name': lastName, 'name': kitchenName, 
                        'address': street, 'city': city, 'state': state,
                        'zipcode': zipcode, 'description': description,
                        'phone_number': phoneNumber, 'close_time': closeTime,
                        'open_time': openTime}

        apiURL = API_BASE_URL +'api/v1/kitchens/register'
        response = requests.post(apiURL, data=json.dumps(request_data))

        if response.json().get('message') == 'Request failed. Please try again later.':
            flash('Kitchen registered successfully.')
            return
        else:
            return redirect(url_for('kitchen', id=response.json().get('kitchen_id')))

    return render_template('register.html')


@app.route('/kitchens/<string:id>')
@login_required
def kitchen(id):
    if 'name' not in login_session:
        return redirect(url_for('index'))

    apiURL = API_BASE_URL +'/api/v1/meals/' + current_user.get_id()
    response = requests.get(apiURL)
    
    todaysMenu = response.json().get('result')

    return render_template('kitchen.html', 
                            name=login_session['name'], 
                            id=login_session['user_id'],
                            todaysMeals=todaysMenu)


@app.route('/kitchens/registration', methods=['POST'])
@login_required
def updateRegistration():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == None or password == None
        print('Missing username or password')
        return

    kitchen_id = current_user.get_id()

    db.update_item(TableName='kitchens',
        Key={'kitchen_id': {'S': str(kitchen_id)}},
        UpdateExpression='SET username = :un, password = :pw',
        ExpressionAttributeValue={
            ':un': {'S': username},
            ':pw': {'S': password}
        }
    )

    return render_template('kitchen-information.html')


@app.route('/kitchens/personal-information', methods=['POST'])
@login_required
def updatePersonalInformation():
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    zipcode = request.form.get('zipcode')
    phone_number = request.form.get('phoneNumber')
    email = request.form.get('email')

    if first_name == None or last_name == None or address == None
      or city == None or state == None or zipcode == None
      or phone_number == None or email == None
        flash('Please fill in all the required fields')
        return render_template('kitchen-information.html')

    kitchen_id = current_user.get_id()

    db.update_item(TableName='kitchens',
        Key={'kitchen_id': {'S': str(kitchen_id)}},
        UpdateExpression='SET first_name = :fn, last_name = :ln, address = :a, city = :c, state = :s, zipcode = :z, phone_number = :pn, email = :e',
        ExpressionAttributeValue={
            ':fn': {'S': first_name},
            ':ln': {'S': last_name},
            ':a': {'S': address},
            ':c': {'S': city},
            ':s': {'S': state},
            ':z': {'N': zipcode},
            ':pn': {'S': phone_number},
        }
    )
    return render_template('kitchen-information.html')


@app.route('/kitchens/kitchen-information', methods=['POST'])
@login_required
def updateKitchenInformation():
    name = request.form.get('kitchenName')
    description = request.form.get('description')
    open_time = request.form.get('openTime')
    close_time = request.form.get('closeTime')
    delivery_open_time = request.form.get('deliveryOpenTime')
    delivery_close_time = request.form.get('deliveryCloseTime')
    delivery_option = request.form.get('deliveryOption')

    if name == None or description == None or open_time == None
      or close_time == None or delivery_open_time == None or delivery_close_time == None
      or delivery_option == None
        flash('Please fill in all the required fields')
        return render_template('kitchen-information.html')

    kitchen_id = current_user.get_id()

    db.update_item(TableName='kitchens',
        Key={'kitchen_id': {'S': str(kitchen_id)}},
        UpdateExpression='SET name = :n, description = :d, open_time = :ot, close_time = :ct, delivery_open_time = :dot, delivery_close_time = :dct, delivery_option= :do',
        ExpressionAttributeValue={
            ':n': {'S': name},
            ':d': {'S': description},
            ':ot': {'S': open_time},
            ':ct': {'S': close_time},
            ':dot': {'S': delivery_open_time},
            ':dct': {'S': delivery_close_time},
            ':do': {'S': delivery_option}
        }
    )
    return render_template('kitchen-information.html')


@app.route('/kitchens/meals/create', methods=['POST'])
@login_required
def postMeal():
    name = request.form.get('name')
    price = request.form.get('price')
    photo = request.files.get('photo')
    itemsData = request.form.get('items')
    
    if name == None or price == None or photo == None or itemsData == None:
        print('Meal details missing')
        return

    kitchen_id = current_user.get_id()

    meal_id = uuid.uuid4().hex
    created_at = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%dT%H:%M:%S")

    meal_items = json.loads(itemsData)

    items = []
    for i in meal_items['meal_items']:
        item = {}
        item['title'] = {}
        item['title']['S'] = i['title']
        item['qty'] = {}
        item['qty']['N'] = str(i['qty'])
        items.append(item)

    description = [{'M': i} for i in items]

    # try:
    photo_key = 'meals_imgs/{}_{}'.format(str(kitchen_id), str(meal_id))
    photo_path = upload_meal_img(photo, BUCKET_NAME, photo_key)

    if photo_path == None:
        raise BadRequest('Request failed. \
            Something went wrong uploading a photo.')

    add_meal = db.put_item(TableName='meals',
        Item={'meal_id': {'S': meal_id},
              'created_at': {'S': created_at},
              'kitchen_id': {'S': str(kitchen_id)},
              'meal_name': {'S': str(name)},
              'description': {'L': description},
              'price': {'S': str(price)},
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

    return redirect(url_for('kitchen', id=current_user.get_id()))
    # except:
    #     raise BadRequest('Request failed. Please try again later.')


@app.route('/kitchens/report')
@login_required
def report():
    if 'name' not in login_session:
        return redirect(url_for('index'))

    todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")
    orders = db.scan(TableName='meal_orders',
        FilterExpression='kitchen_id = :value AND (contains(created_at, :x1))',
        ExpressionAttributeValues={
            ':value': {'S': current_user.get_id()},
            ':x1': {'S': todays_date}
        }
    )

    apiURL = API_BASE_URL +'/api/v1/meals/' + current_user.get_id()
    response = requests.get(apiURL)
    
    todaysMenu = response.json().get('result')
    mealsToCook = todaysMenu

    for item in mealsToCook:
        item['qty'] = 0

    for order in orders['Items']:
        for meals in order['order_items']['L']:
            for item in mealsToCook:
                if item['meal_id']['S'] == meals['M']['meal_id']['S']:
                    item['qty'] += int(meals['M']['qty']['N'])
            for item in todaysMenu:
                if item['meal_id']['S'] == meals['M']['meal_id']['S']:
                    meals['M']['meal_name'] = item['meal_name']

    print(orders['Items'])
    print(mealsToCook)

    return render_template('report.html', 
                            name=login_session['name'], 
                            id=login_session['user_id'],
                            mealsToCook=mealsToCook,
                            orders=orders['Items'])


def closeKitchen(kitchen_id):
    closeKitchen = db.update_item(TableName='kitchens',
        Key={'kitchen_id': {'S': kitchen_id}},
        UpdateExpression='SET isOpen = :val',
        ExpressionAttributeValues={
            ':val': {'BOOL': False}                                                       
        }
    )

@app.route('/kitchens/hours')
def updateKitchensStatus():
    if request.headers['X-Appengine-Cron'] == 'true':
        currentTime = datetime.now(tz=timezone('US/Pacific')).strftime('%H:%M')

        kitchens = db.scan(TableName='kitchens')
        for kitchen in kitchens['Items']:
            closeTime = kitchen['close_time']['S']
            if kitchen['isOpen']['BOOL'] == True:
                if currentTime.rsplit(':', 1)[0] == closeTime.rsplit(':', 1)[0]:
                    if int(currentTime.rsplit(':', 1)[1]) > int(closeTime.rsplit(':', 1)[1]):
                        closeKitchen(kitchen['kitchen_id']['S'])
                elif int(currentTime.rsplit(':', 1)[0]) > int(closeTime.rsplit(':', 1)[0]):
                    closeKitchen(kitchen['kitchen_id']['S'])
        return 'testing cron jobs'


if __name__ == '__main__':
    app.run(debug=False)