"""
models.py
- Data classes for the crisismgmt application
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    is_authority = db.Column(db.Integer)
    first_name = db.Column(db.String(191), nullable=False)
    last_name = db.Column(db.String(191), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow)

    contact_list = db.relationship("ContactList", backref="users", cascade='all, delete')

    def __init__(self, user_id, is_authority, first_name, last_name, email, password, status, location):
        self.user_id = user_id
        self.is_authority = is_authority
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = generate_password_hash(password, method='sha256')
        self.status = status
        self.location = location
    
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

    def to_dict(self):
        return dict(id=self.student_id, email=self.email)


class ContactList(db.Model):
    __tablename__ = 'contact_list'
    contact_list_id = db.Column(INTEGER(unsigned=True), primary_key=True)
    user_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('users.user_id'), nullable=False)
    contact_list = db.Column(db.Text, nullable=False)
    
    

    def __init__(self, contact_list_id, contact_list):
        self.contact_list_id = contact_list_id
        self.user_id = user_id
        self.contact_list = contact_list
    

    def to_dict(self):
        return dict('contact_list_id':contact_list_id, 
                    'user_id': user_id,
                    'contact_list' : contact_list)


class Event(db.Model):
    __tablename__ = 'event'
    
    event_id = db.Column(INTEGER(unsigned=True), primary_key=True)
    event_name = db.Column(db.String(500), nullable=False)
    severity = db.Column(db.String(191), nullable=False)
    resource_list_id = db.Column(db.Integer, nullable=False)
    help_doc_id = db.Column(db.Integer, nullable=False)

    def __init__(self, event_id, event_name, severity, resource_list_id, help_doc_id):
        self.event_id = event_id
        self.event_name = event_name
        self.severity = severity
        self.resource_list_id = resource_list_id
        self.help_doc_id = help_doc_id

    def to_dict(self):



class Node(db.Model):
    __tablename__ = 'Node'

    node_id = db.Column(INTEGER(unsigned=True), primary_key=True)
    node_name = db.Column(db.String(500), nullable=False)
    node_location = db.Column(db.String(500), nullable=False)
    node_type = db.Column(db.String(500), nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)
    current_capacity = db.Column(db.Integer, nullable=False)

    def __init__(self, node_id, node_name, node_location, node_type, max_capacity, current_capacity):
        self.node_id = node_id
        self.node_name = node_name
        self.node_location = node_location
        self.node_type = node_type
        self.max_capacity = max_capacity
        self.current_capacity = current_capacity

    def to_dict(self):

class HelpDoc(db.Model):
    __tablename__ = 'help_doc'

    help_doc_id = db.Column(INTEGER(unsigned=True), primary_key=True)
    content_url = db.Column(db.String(500), nullable=False)

    def __init__(help_doc_id,content_url)
        this.help_doc_id = help_doc_id
        this.content_url = content_url

    def to_dict(self):

class ResourceList:
    __tablename__ = 'resource_list'

    resource_list_id = db.Column(INTEGER(unsigned=True), primary_key=True)
    event_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('event.event_id'), nullable=False)
    resource_id = db.Column(db.Integer, nullable=False)

    def __init__(resource_list_id, event_id, resource_id):
        this.resource_list_id = resource_list_id
        this.event_id = event_id
        this.resource_id = resource_id

    def to_dict(self):
    

class Resource(db.Model):
    __tablename__ = 'resource'

    resource_id = db.Column(INTEGER(unsigned=True), primary_key=True)
    resource_name = db.Column(db.String(500), nullable=False)
    resource_quantity = db.Column(db.Integer, nullable=False)

    def __init__(resource_id, resource_name, resource_quantity):
        this.resource_id = resource_id
        this.resource_name = resource_name
        this.resource_quantity = resource_quantity

    def to_dict(self):






