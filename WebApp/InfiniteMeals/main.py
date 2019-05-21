# -*- coding: utf-8 -*-
# @Author: Japan Parikh
# @Date:   2019-05-15 18:03:31
# @Last Modified by:   Shashi kiran gadhar
# @Last Modified time: 2019-05-15 20:10:13


import os
import boto3
import json

from flask import Flask, request, render_template, redirect, url_for
from flask_restful import Resource, Api
from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.security import generate_password_hash, \
    check_password_hash

app = Flask(__name__, static_folder='static', template_folder='templates')

api = Api(app)

db = boto3.client('dynamodb')


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("post method")
        response = {}
        username = request.form.get('username')
        password = request.form.get('password')
        try:

            result = db.scan(TableName="kitchens",
                             FilterExpression='username = :val',
                             ExpressionAttributeValues={
                                 ":val": {"S": username}
                             }
                             )

            if result['Count'] == 0:
                print("User not found.")
                return render_template('login.html')

            user = result.get('Items')

            if not check_password_hash(user[0]['password']['S'], password):
                print('Password incorrect')
                return render_template('login.html')

            return redirect(url_for('kitchen', id=user[0]['kitchen_id']['S']))
        except:
            raise BadRequest('Request failed. Please try again later.')

    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/report')
def report():
    return render_template('report.html')


@app.route('/kitchen')
def kitchen():
    print(request.args['id'])
    try:

        result = db.scan(TableName="kitchens",
                         FilterExpression='kitchen_id = :val',
                         ExpressionAttributeValues={
                             ":val": {"S": request.args['id']}
                         })

        if result['Count'] == 0:
            print("User not found.")
            return render_template('login.html')

        kitchen = result.get('Items')
        name = kitchen[0]['name']['S']

        return render_template('kitchen.html', mykitchen=name)
    except:
        raise BadRequest('Request failed. Please try again later.')




# api.add_resource(Users, '/api/v1/user')

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
