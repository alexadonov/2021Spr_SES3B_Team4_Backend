"""
api.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""

from operator import or_
from flask import Blueprint, jsonify, request, make_response, current_app
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
from sqlalchemy import exc
from sqlalchemy import inspect,and_,or_,not_
from functools import wraps
from .models import db, User, ContactList, RequestList, Event, Node, HelpDoc, ResourceList, Resource, ChatRoom, ChatParticipants, ChatMessages, required_fields
from .services.misc import pre_init_check, MissingModelFields, datetime_to_str, parse_datetime, poly_pos
import jwt
import pymysql
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpathes
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
        return jsonify({ 'message': 'integrity error' }), 409
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
        return jsonify({ 'message': 'integrity error' }), 409
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
        return jsonify({ 'message': 'integrity error' }), 409
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
        return jsonify({ 'message': 'integrity error' }), 409
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
    

@api.route('/get_event', methods=('POST', ))
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

@api.route('/get_type_event', methods=('POST', ))
def getTypeEvent():
    """
    Returns a list of all active events
    """
    try:
        data = request.get_json()
        print(data)
        if data.get('event_type'):
            eventlist = db.session.query(Event)
            eventlist = eventlist.filter(Event.is_active == 1, Event.event_type == data['event_type'])
            # if data.get('event_type'):
            #     eventlist = eventlist.filter(Event.event_type == data['event_type'])
            payload = []
            for i in eventlist:
                event = i.columns_to_dict()
                payload.append(event)
            return jsonify({'Active Events' : payload}), 200
        else:
            return jsonify({'message': 'Must pass an event type through'}), 500
    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity error' }), 409
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
    

@api.route('/get_node', methods=('POST', ))
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
        return jsonify({ 'message': 'integrity error' }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500



@api.route('/add-contacts', methods=('POST',))
def add_contacts():
    """
    Takes string with list of contact numbers like "0437263746, 4837473272", finds if user exisits with the phone
    number and adds them as a contact
    """
    try:
        data = request.get_json()
        user = data['user_id']
        phone_numbers = data['phone_numbers'].split(",")
        contact_added = 0
        contact_not_found = 0
        contact_exists = 0
        total_contacts = 0

        for p in phone_numbers:
            total_contacts +=1
            print(p)
            query = User.query.filter_by(contact_number = p).first()

            if query:
                print(query.user_id)
                print(type(query.user_id))

                if(ContactList.query.filter_by(user_id = user).filter_by(contact_user_id = query.user_id).first()):
                    contact_exists +=1
                else:
                    contact = ContactList(user_id = user, contact_user_id = query.user_id)
                    db.session.add(contact)
                    db.session.commit()
                    contact_added +=1
            else:
                contact_not_found +=1


        return jsonify({'message' : " {} contacts passed.{} added, {} duplicates and {} not found".format(total_contacts, \
            contact_added, contact_exists, contact_not_found)}), 201

    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity errror' }), 409

    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500


@api.route('/get-contacts', methods=('POST',))
def get_contacts():
    """
    Returns all contacts associated with a user_id
    """
    try:
        data = request.get_json()
        user_id = data['user_id']
        payload = []
        contacts = ContactList.query.filter_by(user_id = user_id).all()
        for c in contacts:
            user = User.query.filter_by(user_id = c.contact_user_id).first()
            dict_column = user.columns_to_dict()
            dict_column.pop('password')
            dict_column.pop('created_date')
            dict_column.pop('updated_date')
            payload.append(dict_column)

        return jsonify({'contact_list': payload}), 200

    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity error' }), 409
        
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500
    

# ------------------------- Firend Request -------------------------------------------
@api.route('/search_user', methods=('POST', ))
def searchUser():
    """
    Returns a list of searching user through first name
    This is for searching user through first name while addFriends
    Frontend should give the search data called 'name', can be part of the frist name 
    """
    try:
        data = request.get_json()
        name = data['name'] # the search data
        userlist = db.session.query(User.first_name, User.last_name, User.user_id).filter(User.first_name.like('%'+name+'%')).order_by(-User.user_id)
        
        payload = []
        for i in userlist:
            list = {
                'first_name': i.first_name,
                'last_name': i.last_name,
                'user_id': i.user_id
            }
            payload.append(list)
        return jsonify({'User' : payload}), 200
       
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify({ 'message': 'integrity error' }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500   
    

@api.route('/add_friends', methods=('POST',))
def addFriends():
    """
    send friend request status: Applying, Success, Fail
    While accept the friendRequest, they will become friends and save in the contact list
    need two users'id (user_id and request_user_id) 
    """
    try:
        data = request.get_json()
        user_id = data['user_id']
        request_user_id = data['request_user_id']
        # search for add them mutiply
        contactlist = ContactList.query.filter(or_(and_(ContactList.contact_user_id == user_id, ContactList.user_id == request_user_id),
            and_(ContactList.user_id == user_id, ContactList.contact_user_id == request_user_id))).count()
        if contactlist:
            return jsonify({ 'message': 'You are already friends!' }), 601
        
        # search for add them mutiply
        list = RequestList.query.filter_by(user_id = user_id, request_user_id = request_user_id, status = 'Applying').count()
        if list:
            return jsonify({ 'message': 'You already send the request!' }), 602
        list = RequestList.query.filter_by(user_id = user_id, request_user_id = request_user_id, status = 'Success').count()
        if list:
            return jsonify({ 'message': 'You are already friends!' }), 603
        
        requestlist = RequestList(**data)
        db.session.add(requestlist)
        db.session.commit()
        return jsonify({'message' : 'Request sent Successfully!'}), 201

    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'User Not Found'.format(data['user_id']) }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500
    

@api.route('/get_friends', methods=('POST',))
def getFriends():
    """
    Returns all contacts associated with a user_id
    """
    try:
        data = request.get_json()
        uid = data['user_id']

        payload = []
        contacts = ContactList.query.filter(or_(ContactList.user_id == uid, ContactList.contact_user_id == uid)).group_by(-ContactList.contact_list_id).all()
        for c in contacts:
            
            if c.user_id != int(uid):
                user = db.session.query(User.first_name, User.last_name, User.email, User.contact_number, User.user_id).filter(User.user_id == c.user_id).first()
            else:
                user = db.session.query(User.first_name, User.last_name, User.email, User.contact_number, User.user_id).filter(User.user_id == c.contact_user_id).first()
            
            dict_column = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_id': user.user_id,
                'email': user.email,
                'contact_number': user.contact_number,
                'id': c.contact_list_id
            }
            
            payload.append(dict_column)

        return jsonify({'contact_list': payload}), 200
        
    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity error' }), 409
        
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500
    

@api.route('/get_receive_request', methods=('POST',))
def getReceiveRequest():
    """
    Returns a list of received request
    """
    try:
        data = request.get_json()
        uid = data['user_id']

        payload = []
        list = db.session.query(RequestList).filter(RequestList.request_user_id == uid).order_by(-RequestList.request_list_id).all()
        if (list):
            for c in list:
                user = db.session.query(User.first_name, User.last_name, User.email, User.contact_number, User.user_id).filter(User.user_id == c.user_id).first()
                
                dict_column = {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'content': c.content,
                    'request_id': c.request_list_id,
                    'status': c.status
                }
                payload.append(dict_column)

        return jsonify({'request_list': payload}), 200
        
    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity error' }), 409
        
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500


@api.route('/get_send_request', methods=('POST',))
def getSendRequest():
    """
    Returns a list of sent request
    """
    try:
        data = request.get_json()
        uid = data['user_id']

        payload = []
        list = RequestList.query.filter(RequestList.user_id == uid).order_by(-RequestList.request_list_id)
        for c in list:
            user = User.query.filter_by(user_id = c.request_user_id).first()
            userinfo = user.columns_to_dict()
            
            dict_column = {
                'first_name': userinfo['first_name'],
                'last_name': userinfo['last_name'],
                'content': c.content,
                'request_id': c.request_list_id,
                'status': c.status
            }
            payload.append(dict_column)

        return jsonify({'request_list': payload}), 200
        
    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity error' }), 409
        
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500


@api.route('/approve_request', methods=('POST',))
def approveRequest():
    """
    Accept/Confuse the friend request
    if accept, add contact list, create chatroom
    need request_list_id, status, reason
    """
    try:
        data = request.get_json()
        list = RequestList.query.filter_by(request_list_id=data['request_list_id']).first()
        
        if list:
            list.status = data['status']
            list.reason = data['reason']
            
            db.session.commit()

            if (data['status'] == 'Success'):
                # accept the request
                # add into contact list
                contact = ContactList(list.user_id, list.request_user_id)
                db.session.add(contact)
                db.session.commit()
                # create chatroom and chatroom participants
                user = db.session.query(User.first_name).filter(User.user_id==list.user_id).first()
                request_user = db.session.query(User.first_name).filter(User.user_id==list.request_user_id).first()
                # create a new chatroom for two users 
                room_name = user.first_name + '&' + request_user.first_name
                
                chatroom = ChatRoom(room_name)
                db.session.add(chatroom)
                db.session.commit()
                # create chatroom participants
                chatroom_id = db.session.query(ChatRoom.chatroom_id).order_by(-ChatRoom.chatroom_id).first()
                
                part_1 = ChatParticipants(list.user_id, chatroom_id.chatroom_id)
                part_2 = ChatParticipants(list.request_user_id, chatroom_id.chatroom_id)
                db.session.add_all([part_1, part_2])
                db.session.commit()
                
            return jsonify({'message' : 'Request approved Successfully!'}), 201
        else: 
            db.session.rollback()
            return jsonify({ 'message': 'Request Not Found.'}), 409  

    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500


@api.route('/display_user_location', methods=('POST',))
def DisplayUserLocation():
    """
    A list of all user location
    """
    try:
        # data = request.get_json()
        
        payload = []
        contacts = db.session.query(User.user_id, User.location, User.longitude, User.latitude, User.first_name, User.last_name).all()
        for c in contacts:
            dict_column = {
                'user_id': c.user_id,
                'location': c.location,
                'longitude': c.longitude,
                'latitude': c.latitude,
                'first_name': c.first_name,
                'last_name': c.last_name
            }
            payload.append(dict_column)

        return jsonify({'user location list': payload}), 200

    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity errror' }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500

@api.route('/check_danger', methods=('POST',))
def checkDanger():
    """
    If user location enters into Event radius, alert user
    data: longitude, latitude
    """
    try:
        data = request.get_json()
        
        # get all the events
        eventlist = Event.query.filter_by(is_active = 1).all()
        payload = []
        for i in eventlist:
            event = i.columns_to_dict()
            payload.append(event)
        
        indanger = False
        msg = ''
        # get the radius circle
        for j in payload:
            if j['longitude'] != '' and j['latitude'] != '' :
                xy = np.array([float(j['latitude']),float(j['longitude'])])
                circle = mpathes.Circle(xy,1)
                
                # If user location enters into Event radius, alert user
                long = float(data['longitude'])
                lat = float(data['latitude'])
                if circle.contains_point((lat, long)):
                    indanger = True
                    msg = "Warning! You're in a danger place, leave now!"
                    break
        
        return jsonify({ 'data': indanger, 'message': msg }), 200

    except exc.IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({ 'message': 'integrity errror' }), 409
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500
