"""
manage.py
- provides a command line utility for interacting with the
  application to perform interactive debugging and setup
"""

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from crisismgmt.application import create_app
from crisismgmt.models import db, User, ContactList, RequestList, Event, Node, HelpDoc, ResourceList, Resource, ChatRoom, ChatParticipants, ChatMessages

app = create_app()

migrate = Migrate(app, db)
manager = Manager(app)

# provide a migration utility command
manager.add_command('db', MigrateCommand)

# enable python shell with application context
@manager.shell
def shell_ctx():
    return dict(app=app,
      db=db,
      User=User,
      ContactList=ContactList,
      RequestList=RequestList,
      Event=Event,
      Node=Node,
      HelpDoc=HelpDoc,
      ResourceList=ResourceList,
      Resource=Resource,
      ChatRoom=ChatRoom,
      ChatParticipants=ChatParticipants,
      ChatMessages=ChatMessages
    )

if __name__ == '__main__':
    manager.run()