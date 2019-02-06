#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import json
import webapp2
import jinja2
# import cloudstorage
# from google.appengine.api import app_identity
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from models import Order, Meal, Address
# import ordermeal.lib.cloudstorage as gcs

BUCKET_NAME = 'ordermeal'

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def _upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


class MainHandler(webapp2.RequestHandler):
    def get(self):
    	# path = os.path.join(os.path.dirname(__file__), 'index.html')
    	template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())

class ImageUploadHandler(webapp2.RequestHandler):
    def post(self):
    	file_data = self.request.POST['file']
    	print file

class OrderMealHandler(webapp2.RequestHandler):
	def post(self):
		jsonstring = self.request.body
		jsonobject = json.loads(jsonstring)

		if jsonobject.get('email') == None \
			or jsonobject.get('name') == None \
			or jsonobject.get('street') == None \
			or jsonobject.get('zipCode') == None \
			or jsonobject.get('city') == None \
			or jsonobject.get('state') == None \
			or jsonobject.get('totalAmount') == None \
			or jsonobject.get('paid') == None \
			or jsonobject.get('paymentType') == None\
			or jsonobject.get('deliveryTime') == None:
			self.response.out.write('Please provide all the details')
		
		email = jsonobject.get('email')
		name = jsonobject.get('name')
		zipCode = jsonobject.get('zipCode')
		city = jsonobject.get('city')
		state = jsonobject.get('state')
		street = jsonobject.get('street')
		totalAmount = jsonobject.get('totalAmount')
		paid = jsonobject.get('paid')
		paymentType = jsonobject.get('paymentType')
		deliveryTime = jsonobject.get('deliveryTime')

		address = Address(street=street,
						zipCode=zipCode,
						city=city,
						state=state)

		order = Order(name=name,
					email=email,
					address=address,
					totalAmount=totalAmount,
					paid=paid,
					paymentType=paymentType,
					deliveryTime=deliveryTime)

		order.put()
		self.response.out.write('Request successful.')


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/api/v1/image/upload', ImageUploadHandler),
    ('/api/v1/ordermeal', OrderMealHandler)
], debug=True)
