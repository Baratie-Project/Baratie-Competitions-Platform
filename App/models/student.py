from App.database import db
from App.models import User
from App.models.student_observer_interface import StudentObserver

class Student(User, StudentObserver):
    __tablename__ = 'student'

    rating_score = db.Column(db.Float, nullable=False, default=0)
    comp_count = db.Column(db.Integer, nullable=False, default=0)
    curr_rank = db.Column(db.Integer, nullable=False, default=0)
    prev_rank = db.Column(db.Integer, nullable=False, default=0)
    teams = db.relationship('Team', secondary='student_team', overlaps='students', lazy=True)
    notifications = db.relationship('Notification', backref='student', lazy=True)
    ranking_history = db.relationship('RankHistory', backref='student', lazy=True)

    def __init__(self, username, password):
        super().__init__(username, password)
        self.rating_score = 0
        self.comp_count = 0
        self.curr_rank = 0
        self.prev_rank = 0
        self.teams = []
        self.notifications = []

    def add_notification(self, notification):
        if notification:
            try:
                self.notifications.append(notification)
                db.session.commit()
                return notification
            except Exception as e:
                db.session.rollback()
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

    def to_Dict(self):
        return {
            "ID": self.id,
            "Username": self.username,
            "Rating Score": self.rating_score,
            "Number of Competitions": self.comp_count,
            "Rank": self.curr_rank
        }

    def update_rank(self, new_rank):
        self.prev_rank = self.curr_rank
        self.curr_rank = new_rank

        rank_entry = RankHistory(student_id=self.id, rank=new_rank)
        try:
            db.session.add(rank_entry)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Failed to update rank history: {e}")

    def __repr__(self):
        return f'<Student {self.id} : {self.username}>'

assert hasattr(Student, "update_rank"), "Student must implement the update_rank method"
