"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_user():
    return auth.current_user.get('id') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.define_table('images',
                Field('image_url')
                )

db.define_table('stars',
                Field('image', 'reference images'), # Image that is starred
                Field('rating', 'integer', default=0),
                Field('rater', 'reference auth_user', default=get_user) # User doing the rating.
                )

db.commit()
