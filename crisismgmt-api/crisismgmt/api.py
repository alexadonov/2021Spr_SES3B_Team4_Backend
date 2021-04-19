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
import pymysql
pymysql.install_as_MySQLdb()
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

@api.route('/chat/create-chat', methods=('POST',))
def create_chat():
    """
    Create new chat room between two/multiple users
    """
    try:
        data = request.get_json()

        room_data = data['room_info']
        room_participants = data['participants']
        #room_data['room_name'] = data.get('room_name')
        room = ChatRoom(**room_data)
        db.session.add(room)
        db.session.commit()

        room_to_dict = room.to_dict()
        print(room_to_dict)
        room_id = room_to_dict['room_id']
        print(room_id)

        for i in room_participants:
            print(i)
            participant = ChatParticipants(chat_id = room_id, user_id = i)
            db.session.add(participant)
            db.session.commit()

        return jsonify({'message' : 'Chat room added', 'room': room.to_dict(), 'participants': room_participants}), 201
    #except (MissingModelFields) as e:
       #return jsonify({ 'message': e.args }), 400
    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity errror' }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500


@api.route('chat/save-message', methods=('POST',))
def save_message():
    """
    Save a chat message
    """
    try:
        data = request.get_json()
        message = ChatMessages(**data)
        db.session.add(message)
        db.session.commit()

        return jsonify({'message' : 'Chat msg saved', 'chat_message': message.to_dict()}), 201
    #except (MissingModelFields) as e:
       #return jsonify({ 'message': e.args }), 400
    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity errror' }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500


@api.route('chat/get-chatroom-list', methods=('GET',))
def get_chatroom_list():
    """
    Create new chat room between two users
    """
    try:
        data = request.get_json()
        chat_list = ChatParticipants.query.filter_by(user_id = data['user_id']).all()
        payload = []
        for u in chat_list:
            payload.append(u.columns_to_dict())
        print (payload)


        return jsonify({'chat_room_list': payload}), 201
    #except (MissingModelFields) as e:
       #return jsonify({ 'message': e.args }), 400
    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity errror' }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500

@api.route('chat/get-chatroom-messages', methods=('GET',))
def get_chatroom_messages():
    """
    Create new chat room between two users
    """
    try:
        data = request.get_json()
        chat_messages = ChatMessages.query.filter_by(room_id = data['room_id']).all()
        payload = []
        for c in chat_messages:
            payload.append(c.columns_to_dict())
        print (payload)


        return jsonify({'chat_room_messages': payload}), 201
    #except (MissingModelFields) as e:
       #return jsonify({ 'message': e.args }), 400
    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity errror' }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
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


