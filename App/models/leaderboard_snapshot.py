from App.database import db
from App.models import User
from datetime import datetime
import json

class LeaderboardSnapshot(db.Model):
    __tablename__ = 'leaderboard_snapshot'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    leaderboard_data = db.Column(db.Text, nullable=False)  

    def __init__(self, leaderboard_data):
        self.leaderboard_data = json.dumps(leaderboard_data) 

    def get_leaderboard_data(self):
        return json.loads(self.leaderboard_data)

    def to_dict(self):
 
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "leaderboard_data": self.get_leaderboard_data()
        }

    def __repr__(self):
        return f"<LeaderboardSnapshot {self.id} at {self.timestamp}>"