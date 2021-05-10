"""
models.py
- Data classes for the crisismgmt application
"""

from datetime import datetime
from dateutil import parser
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from .services.misc import datetime_to_str, parse_datetime
import jwt

db = SQLAlchemy()

required_fields = {'users':['email', 'is_authority' 'first_name', 'last_name', 'password']}


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_authority = db.Column(db.Integer)
    first_name = db.Column(db.String(191), nullable=False)
    last_name = db.Column(db.String(191), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow)
    contact_number = db.Column(db.String(255), nullable=False)

    def __init__(self, is_authority, first_name, last_name, email, password, contact_number):
        self.is_authority = is_authority
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = generate_password_hash(password, method='sha256')
        self.status = 'null'
        self.location = 'location'
        self.contact_number = contact_number
    
    @classmethod
    def authenticate(cls, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')
        
        if not email or not password:
            return None

        user = cls.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return None

        return user

    @classmethod
    def decode_auth_token(cls, token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'])
            return payload['sub']
        except Exception:
            return 'Invalid token. Please log in again.'

    def to_dict(self):
        return {
            'user_id':self.user_id,
            'email':self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_authority': self.is_authority
        }

    def columns_to_dict(self):
        dict_ = {}
        for key in self.__mapper__.c.keys():
            dict_[key] = getattr(self, key)
        return dict_


class ContactList(db.Model):
    __tablename__ = 'contact_list'
    contact_list_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    contact_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    
    

    def __init__(self, user_id, contact_user_id):
        self.user_id = user_id
        self.contact_user_id = contact_user_id
    

    def columns_to_dict(self):
        dict_ = {}
        for key in self.__mapper__.c.keys():
            dict_[key] = getattr(self, key)
        return dict_


class Event(db.Model):
    __tablename__ = 'event'
    
    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_name = db.Column(db.String(500), nullable=False)
    severity = db.Column(db.String(191), nullable=False)
    event_type = db.Column(db.String(191), nullable=False)
    location = db.Column(db.String(191), nullable=False)
    is_active = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))

    def __init__(self, event_name, severity, event_type, location, user_id):
        
        self.event_name = event_name
        self.severity = severity
        self.event_type = event_type
        self.location = location
        self.is_active = 1
        self.user_id = user_id

    def to_dict(self):
        return {
            'event_id':self.event_id,
            'event_name':self.event_name,
            'severity':self.severity,
            'event_type':self.event_type,
            'location':self.location,
            'is_active':self.is_active,
            'user_id':self.user_id
        }
    
    def columns_to_dict(self):
        dict_ = {}
        for key in self.__mapper__.c.keys():
            dict_[key] = getattr(self, key)
        return dict_



class Node(db.Model):
    __tablename__ = 'node'

    node_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    node_name = db.Column(db.String(500), nullable=False)
    node_location = db.Column(db.String(500), nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)
    current_capacity = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id', ondelete='CASCADE'))

    def __init__(self, node_name, node_location, max_capacity, current_capacity, event_id):
        self.node_name = node_name
        self.node_location = node_location
        self.max_capacity = max_capacity
        self.current_capacity = 0
        self.event_id = event_id

    def to_dict(self):
        return{
            'node_id':self.node_id,
            'node_name':self.node_name,
            'node_location':self.node_location,
            'max_capacity':self.max_capacity,
            'current_capacity':self.current_capacity,
            'event_id':self.event_id
        }
    
    def columns_to_dict(self):
        dict_ = {}
        for key in self.__mapper__.c.keys():
            dict_[key] = getattr(self, key)
        return dict_

class HelpDoc(db.Model):
    __tablename__ = 'help_doc'

    help_doc_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content_url = db.Column(db.String(500), nullable=False)
    event_type = db.Column(db.String(191), nullable=False)
    def __init__(self, help_doc_id, content_url, event_type):
        this.help_doc_id = help_doc_id
        this.content_url = content_url
        this.event_type = event_type

    #def to_dict(self):

class ResourceList:
    __tablename__ = 'resource_list'

    resource_list_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_type = db.Column(db.String(500), nullable=False)
    

    def __init__(self, event_type):
        this.event_id = event_type
        this.resource_id = resource_id

    #def to_dict(self):
    

class Resource(db.Model):
    __tablename__ = 'resource'

    resource_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resource_name = db.Column(db.String(500), nullable=False)
    resource_multiplier = db.Column(db.Integer, nullable=False)

    def __init__(resource_name, resource_quantity, resource_multiplier):
        this.resource_name = resource_name
        this.resource_quantity = resource_quantity
        this.resource_multiplier = resource_multiplier

    #def to_dict(self):

class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'

    chatroom_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chatroom_name = db.Column(db.String(500), nullable=False)
    
    def to_dict(self):
        return {
            'chatroom_id':self.chatroom_id,
            'chatroom_name':self.chatroom_name
        }

class ChatParticipants(db.Model):
    __tablename__ = 'chat_participants'

    participant_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    chat_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.chatroom_id', ondelete='CASCADE'))

    def to_dict(self):
        return{
        'participant_id':self.participant_id,
        'user_id':self.user_id,
        'chat_id':self.chat_id
        }

    def columns_to_dict(self):
        dict_ = {}
        for key in self.__mapper__.c.keys():
            dict_[key] = getattr(self, key)
        return dict_


class ChatMessages(db.Model):
    __tablename__ = 'chat_messages'

    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chatroom_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.chatroom_id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'message_id':self.message_id,
            'chatroom_id':self.chatroom_id,
            'user_id':self.user_id,
            'message':self.message
            }
            
    def columns_to_dict(self):
        dict_ = {}
        for key in self.__mapper__.c.keys():
            dict_[key] = getattr(self, key)
        return dict_




