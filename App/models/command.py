from App.database import db
from abc import abstractmethod

class Command(db.Model):
    __abstract__ = True
    __tablename__ = 'command'
    
    @abstractmethod
    def execute(self, admin_id, competition_id):
        pass