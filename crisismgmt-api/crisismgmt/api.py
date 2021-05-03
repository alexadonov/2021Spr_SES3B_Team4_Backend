"""
api.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""

from flask import Blueprint, jsonify, request, make_response, current_app
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
from sqlalchemy import exc
from sqlalchemy import inspect
from functools import wraps
from .models import db, User, ContactList, Event, Node, HelpDoc, ResourceList, Resource, ChatRoom, ChatParticipants, ChatMessages, required_fields
from .services.misc import pre_init_check, MissingModelFields, datetime_to_str, parse_datetime
import jwt
# import pymysql
# pymysql.install_as_MySQLdb()
api = Blueprint('api', __name__)

ODAPI_URL = 'http://127.0.0.1:8000/'

@api.route('/')
def index():
    response = { 'Status': "API is up and running!" }
    return make_response(jsonify(response), 200)


@api.route('/register', methods=('POST',))
def register():
    """
    Register new users
    """
    try:
        data = request.get_json()
        #pre_init_check(required_fields['users'], **data)
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    #except (MissingModelFields) as e:
       #return jsonify({ 'message': e.args }), 400
    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'User with email {} exists.'.format(data['email']) }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500


@api.route('/login', methods=('POST',))
def login():
    """
    Login for existing users
    """
    data = request.get_json()
    user = User.authenticate(**data)

    if not user:
        return jsonify({ 'message': 'Invalid credentials', 'authenticated': False }), 401
    
    token = jwt.encode(
        {
        'exp': datetime.now() + timedelta(minutes=90),
        'iat': datetime.now(),
        'sub': user.email
        },
        current_app.config['SECRET_KEY'],
        algorithm='HS256')
    #print(token)
    #user_id = data['user_id']
    #user = User.query.get(user_id)
    return jsonify({ 'user': user.to_dict(), 'token': token.decode('UTF-8') }), 200

 

# @api.route('/maps/filter', methods=('POST', 'GET'))
# def get_safe_locations():
#     # Get the nodeID for all nodes, then return if that node is safe or not. This should be under the Zone
#     # table which isn't done yet
    
#     try:
#         data = request.get_json();
#         locations = [];
#         # latitude = request.args.get('latitude', default=0, type=float)
#         # longitude = request.args.get('longitude', default=0, type=float)
#         # Getting the Node ID of safe and unsafe zones
#         safe = Zone.query.filter_by(nodeID = data['nodeID'], safety = 'Y')
#         unsafe = Zone.query.filter_by(nodeID = data['nodeID'],safety = 'N')     
#         # is_safe = request.args.get('is_safe', default=0, type=int)
#         # not_safe = request.args.get('not_safe', default=0, type=int)

#         #Appending safe and unsafe
#         locations.append({'safe': safe})
#         locations.append({'unsafe': unsafe})
#         db.session.commit()

#         #Return array 
#         payload = {'locations': locations };
#         return jsonify(payload), 200; 

#     except (Exception, exc.SQLAlchemyError) as e:
#         return jsonify({ 'message': e.args }), 500


# @api.route('/maps/toggle', methods=('POST', ))
# def toggle_location_permission():
#     """
#     Location permissions
#     """
#     # Maybe here have some user authentication here later
#     try:
#         data = request.get_json();
#         # location = request.args.get('location', default = None)
#         location_on = User.query.filter_by(location = data['location']).first()  
       
#         if location_on:
#             # contact_list = data['contact_list']
#             # is_authority = data['is_authority']
#             ContactList.query.filter_by(is_authority = data['is_authority']).delete()
#             db.session.commit()
#         else: 
#             # Raise exception
#             raise Exception('Location is already off')

#     except (Exception, exc.SQLAlchemyError) as e:
#         return jsonify({ 'message': e.args }), 500      
                   
  
@api.route('/maps/get_events', methods=('GET', ))
def get_events():
    """
    Returns a list of all active events and all associated nodes
    """
    try:
        data = request.get_json()
        payload = []
        results_query = db.session.query(Event).join(Node).filter(Event.is_active == 1)

        for e, n in results_query:
            payload.append({
                'event_id': e.event_id,
                'event_name': e.event_name,
                # 'node_id': n.node_id,
                # 'node_name': n.node_name,
                'is_active': e.is_active
            })
        return jsonify({'Active Events':payload}), 200
       
    except MissingModelFields as e:
        return jsonify({ 'message': e.args }), 400
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({ 'message': e.args }), 500

@api.route('/maps/get_civilian_locations', methods=('GET', ))
def get_civilian_locations():
    """
    Returns all civilian locations
    """
    try:
        data = request.get_json()
        payload = []
        results = User.query.filter_by(is_authority = 0).all()
        # loc = User.query.filter_by(location = data['location'], is_authority = 0).all()
        
        for u in results:
            latitude, longitude = (u.location).split(", ")
            payload.append({
                'user_id': u.user_id,
                'first_name': u.first_name, 
                'last_name': u.last_name,
                # 'location': (u.location)
                'latitude': latitude,
                'longitude': longitude
            })
        return jsonify({'Civilian location':payload}), 200

    except MissingModelFields as e:
        return jsonify({ 'message': e.args }), 400
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({ 'message': e.args }), 500

# This is a decorator function which will be used to protect authentication-sensitive API endpoints
def token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get('Authorization', '').split()

        invalid_msg = {
            'message': 'Invalid token. Registeration and / or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Reauthentication required.',
            'authenticated': False
        }

        if len(auth_headers) != 2:
            return jsonify(invalid_msg), 401

        try:
            token = auth_headers[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            user = User.query.filter_by(email=data['sub']).first()
            if not user:
                raise RuntimeError('User not found')
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(expired_msg), 401 # 401 is Unauthorized HTTP status code
        except (jwt.InvalidTokenError, Exception) as e:
            print(e)
            return jsonify(invalid_msg), 401

    return _verify

#converts a resultproxy object type to dict
def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


