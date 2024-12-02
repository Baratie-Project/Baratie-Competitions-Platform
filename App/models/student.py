from App.database import db
from App.models import User
from .ranking_history import RankHistory
from .leaderboard_snapshot import LeaderboardSnapshot

class Student(User):
    __tablename__ = 'student'

    rating_score = db.Column(db.Float, nullable=False, default=250)
    comp_count = db.Column(db.Integer, nullable=False, default=0)
    curr_rank = db.Column(db.Integer, nullable=False, default=0)
    prev_rank = db.Column(db.Integer, nullable=False, default=0)
    teams = db.relationship('Team', secondary='student_team', overlaps='students', lazy=True)
    notifications = db.relationship('Notification', backref='student', lazy=True)
    historical_ranking = db.relationship('RankHistory', backref='student', lazy=True)

    def __init__(self, username, password):
        super().__init__(username, password)
        self.rating_score = 250
        self.comp_count = 0
        self.curr_rank = 0
        self.prev_rank = 0
        self.teams = []
        self.notifications = []

    def save_rank_history(self, rank, leaderboard_snapshot_id):
        try:
            rank_history = RankHistory(
                student_id=self.id,
                rank=rank,
                leaderboard_snapshot_id=leaderboard_snapshot_id
            )
            db.session.add(rank_history)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error saving rank history: {e}")

    def add_notification(self, notification):
        if notification:
            try:
                self.notifications.append(notification)
                db.session.commit()
                return notification
            except Exception as e:
                db.session.rollback()
                print(f"Error adding notification: {e}")
                return None
        return None

    def get_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "rating_score": self.rating_score,
            "comp_count": self.comp_count,
            "curr_rank": self.curr_rank
        }

    def to_dict(self):
        return {
            "ID": self.id,
            "Username": self.username,
            "Rating Score": self.rating_score,
            "Number of Competitions": self.comp_count,
            "Rank": self.curr_rank
        }

    def __repr__(self):
        return f'<Student {self.id} : {self.username}>'