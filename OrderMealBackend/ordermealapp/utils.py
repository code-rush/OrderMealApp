# -*- coding: utf-8 -*-
# @Author: japs
# @Date:   2018-10-20 19:18:37
# @Last Modified by:   japs
# @Last Modified time: 2018-10-20 19:19:23


import endpoints
from google.appengine.ext import ndb

def get_by_urlsafe(urlsafe, model):
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity