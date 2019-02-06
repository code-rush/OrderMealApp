# -*- coding: utf-8 -*-
# @Author: japs
# @Date:   2018-10-20 19:24:40
# @Last Modified by:   japs
# @Last Modified time: 2018-11-10 15:09:19


import endpoints
import datetime
from protorpc import remote, messages, message_types
from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from models import Order, Meal, Address
from utils import get_by_urlsafe

GET_MEAL_REQUEST = endpoints.ResourceContainer(
	urlsafe_meal_key=messages.StringField(1)
)

@endpoints.api(name='orderMeal', version='v1')
class OrderMealAPI(remote.Service):
	@endpoints.method(GET_MEAL_REQUEST, MEAL_FORM, name='getMeal',
		path='meal/{urlsafe_meal_key}', http_method='GET')
	def get_meal(self, request):
		meal = get_by_urlsafe(request.urlsafe_meal_key, Meal)
		return


api = endpoints.api_server([OrderMealAPI])


