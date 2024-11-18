class RankHistory(db.Model):
    __tablename__ = 'rank_history'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, student_id, rank):
        self.student_id = student_id
        self.rank = rank

    def get_json(self):
        return {
            "student_id": self.student_id,
            "rank": self.rank,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
