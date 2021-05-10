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
from .services.misc import pre_init_check, MissingModelFields, datetime_to_str, parse_datetime, poly_pos
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

@api.route('/chat/create-chatroom', methods=('POST',))
def create_chatroom():
    """
    Create new chat chatroom between two/multiple users
    """
    try:
        data = request.get_json()

        chatroom_data = data['chatroom_info']
        chatroom_participants = data['participants']
        #chatroom_data['chatroom_name'] = data.get('chatroom_name')
        chatroom = ChatRoom(**chatroom_data)
        db.session.add(chatroom)
        db.session.commit()

        chatroom_to_dict = chatroom.to_dict()
        print(chatroom_to_dict)
        chatroom_id = chatroom_to_dict['chatroom_id']
        print(chatroom_id)

        for i in chatroom_participants:
            print(i)
            participant = ChatParticipants(chat_id = chatroom_id, user_id = i)
            db.session.add(participant)
            db.session.commit()

        return jsonify({'message' : 'Chatroom added', 'chatroom': chatroom.to_dict(), 'chatroom_participants': chatroom_participants}), 201
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


@api.route('chat/get-chatroom-list', methods=('POST',))
def get_chatroom_list():
    """
    Create new chat chatroom between two users
    """
    try:
        data = request.get_json()
        chat_list = ChatParticipants.query.filter_by(user_id = data['user_id']).all()
        payload = []
        for u in chat_list:
            chatroom_name = ChatRoom.query.filter_by(chatroom_id = u.chat_id).first()
            print(chatroom_name.chatroom_name)
            dict_pa = u.columns_to_dict()
            dict_pa.pop('participant_id')
            dict_pa.pop('user_id')
            dict_pa.update({"chatroom_name" : chatroom_name.chatroom_name})
            payload.append(dict_pa)
        print (payload)


        return jsonify({'chatroom_list': payload}), 200
    #except (MissingModelFields) as e:
       #return jsonify({ 'message': e.args }), 400
    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity errror' }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500

@api.route('chat/get-chatroom-messages', methods=('POST',))
def get_chatroom_messages():
    """
    Create new chat chatroom between two users
    """
    try:
        data = request.get_json()
        chat_messages = ChatMessages.query.filter_by(chatroom_id = data['chatroom_id']).all()
        payload = []
        for c in chat_messages:
            user_name = User.query.filter_by(user_id = c.user_id).first()
            print(user_name.last_name)
            dict_column = c.columns_to_dict()
            dict_column.pop('chatroom_id')
            dict_column.update({"first_name" : user_name.first_name})
            dict_column.update({"last_name" : user_name.last_name})
            payload.append(dict_column)
        print (payload)


        return jsonify({'chatroom_messages': payload}), 200
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


@api.route('/create-event', methods=('POST',))
def createEvent():
    """
    Register a new event
    """
    try:
        data = request.get_json()
        event = Event(**data)
        db.session.add(event)
        db.session.commit()
        return jsonify({'message' : 'Event created', 'event' : event.to_dict()}), 201

    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'User Not Found'.format(data['user_id']) }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500

@api.route('/edit-event', methods=('POST',))
def editEvent():
    """
    edit an existing event by event_id
    """
    try:
        data = request.get_json()
        event = Event.query.filter_by(event_id=data['event_id']).first()
        if event:
            event.event_name = data['event_name']
            event.severity = data['severity']
            event.event_type = data['event_type']
            event.location = data['location']
            event.user_id = data['user_id']

            db.session.commit()
            return jsonify({'message' : 'Event updated', 'event' : event.to_dict()}), 201
        else: 
            db.session.rollback()
            return jsonify({ 'message': 'Event Not Found.'}), 409

    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500

@api.route('/delete-event', methods=('POST',))
def deleteEvent():
    """
    delete an existing event by event_id
    """
    try:
        data = request.get_json()
        event = Event.query.filter_by(event_id=data['event_id']).first()
        if event:
            db.session.delete(event)
            db.session.commit()
            return jsonify({'message' : 'Event delete'}), 201
        else: 
            db.session.rollback()
            return jsonify({ 'message': 'Event Not Found.'}), 409

    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500

@api.route('/get_event', methods=('GET', ))
def getEvent():
    """
    Returns a list of all active events
    """
    try:
        # data = request.get_json()
        eventlist = Event.query.filter_by(is_active = 1).all()
        payload = []
        for i in eventlist:
            event = i.columns_to_dict()
            payload.append(event)
        return jsonify({'Active Events' : payload}), 200
       
    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity errror' }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500

@api.route('/create-node', methods=('POST',))
def createNode():
    """
    Register a new node
    """
    try:
        data = request.get_json()
        node = Node(**data)
        db.session.add(node)
        db.session.commit()
        return jsonify({'message' : 'Node created', 'node' : node.to_dict()}), 201
        
    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'Event Not Found.'.format(data['event_id']) }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500

@api.route('/edit-node', methods=('POST',))
def editNode():
    """
    edit an existing node by node_id
    """
    try:
        data = request.get_json()
        node = Node.query.filter_by(node_id=data['node_id']).first()
        if node:
            node.node_name = data['node_name']
            node.node_location = data['node_location']
            node.max_capacity = data['max_capacity']
            node.current_capacity = 0
            node.event_id = data['event_id']

            db.session.commit()
            return jsonify({'message' : 'Node updated', 'node' : node.to_dict()}), 201
        else: 
            db.session.rollback()
            return jsonify({ 'message': 'Node Not Found.'}), 409  

    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500

@api.route('/delete-node', methods=('POST',))
def deleteNode():
    """
    delete an existing node by node_id
    """
    try:
        data = request.get_json()
        node = Node.query.filter_by(node_id=data['node_id']).first()
        if node:
            db.session.delete(node)
            db.session.commit()
            return jsonify({'message' : 'Node delete'}), 201
        else: 
            db.session.rollback()
            return jsonify({ 'message': 'Node Not Found.'}), 409
        
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500

@api.route('/get_node', methods=('GET', ))
def getNode():
    """
    Returns a list of all existing nodes
    """
    try:
        # data = request.get_json()
        nodelist = Node.query.all()
        payload = []
        for i in nodelist:
            node = i.columns_to_dict()
            payload.append(node)
        return jsonify({'Existing nodes' : payload}), 200
       
    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity errror' }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
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
