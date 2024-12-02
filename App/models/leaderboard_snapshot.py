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
        try:
            json.dumps(leaderboard_data)  # Validate input as JSON serializable
            self.leaderboard_data = json.dumps(leaderboard_data)
        except (TypeError, ValueError):
            raise ValueError("Invalid leaderboard data format.")

    def get_leaderboard_data(self):
        try:
            return json.loads(self.leaderboard_data)
        except json.JSONDecodeError:
            return {}

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "leaderboard_data": self.get_leaderboard_data()
        }