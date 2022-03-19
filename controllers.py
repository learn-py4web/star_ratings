"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email, get_user

IMAGES = ["rubber-duck.jpg", "rabbit.jpg", "teddy_bear.jpg",
    "colander.jpg", "coffeecup.jpg", "cowboy_hat.jpg"]

url_signer = URLSigner(session)

# This controller is used to initialize the database.
def do_setup():
    db(db.images).delete()
    db(db.stars).delete()
    for img in IMAGES:
        db.images.insert(image_url=URL('static', 'images/' + img))

@action('setup')
@action.uses(db)
def setup():
    do_setup()
    return "ok"

# The auth.user below forces login.
@action('index')
@action.uses('index.html', url_signer, auth.user)
def index():
    # If the database is empty, sets it up.
    if db(db.images).count() == 0:
        do_setup()
    return dict(
        # This is an example of a signed URL for the callback.
        # See the index.html template for how this is passed to the javascript.
        get_images_url = URL('get_images', signer=url_signer),
        get_rating_url = URL('get_rating', signer=url_signer),
        set_rating_url = URL('set_rating', signer=url_signer),
    )

@action('get_images')
@action.uses(url_signer.verify(), db)
def get_images():
    """Returns the list of images."""
    return dict(images=db(db.images).select().as_list())

@action('get_rating')
@action.uses(url_signer.verify(), db, auth.user)
def get_rating():
    """Returns the rating for a user and an image."""
    image_id = request.params.get('image_id')
    row = db((db.stars.image == image_id) &
             (db.stars.rater == get_user())).select().first()
    rating = row.rating if row is not None else 0
    return dict(rating=rating)

@action('set_rating', method='POST')
@action.uses(url_signer.verify(), db, auth.user)
def set_rating():
    """Sets the rating for an image."""
    image_id = request.json.get('image_id')
    rating = request.json.get('rating')
    assert image_id is not None and rating is not None
    db.stars.update_or_insert(
        ((db.stars.image == image_id) & (db.stars.rater == get_user())),
        image=image_id,
        rater=get_user(),
        rating=rating
    )
    return "ok" # Just to have some confirmation in the Network tab.
