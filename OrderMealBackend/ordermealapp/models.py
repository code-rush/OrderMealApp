# -*- coding: utf-8 -*-
# @Author: japs
# @Date:   2018-10-20 17:50:22
# @Last Modified by:   japs
# @Last Modified time: 2018-11-10 15:20:01

import datetime
from google.appengine.ext import ndb
from protorpc import messages


class Address(ndb.Model):
	street = ndb.StringProperty(required=True)
	zipCode = ndb.IntegerProperty(required=True)
	city = ndb.StringProperty(required=True)
	state = ndb.StringProperty(required=True)

class Order(ndb.Model):
    """User Profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    deviceID = ndb.StringProperty(required=False)
    address = ndb.StructuredProperty(Address, required=True)
    totalAmount = ndb.FloatProperty(required=True)
    paid = ndb.BooleanProperty(required=True)
    paymentType = ndb.StringProperty(required=True)
    deliveryTime = ndb.StringProperty(required=True)

class Meal(ndb.Model):
	mealID = ndb.DateTimeProperty(auto_now_add=True)
	creationDate = ndb.DateProperty(auto_now_add=True)
	mealImage = ndb.StringProperty(required=True)
	price = ndb.FloatProperty(required=True)


# class UserForm(messages.Message):
#     """User Form"""
#     first_name = messages.StringField(1, required=True)
#     last_name = messages.StringField(2, required=True)
#     email = messages.StringField(3, required=True)
#     deviceID = messages.StringField(4)
#     address = messages.