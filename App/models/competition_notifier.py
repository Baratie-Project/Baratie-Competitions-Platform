from App.database import db
from App.models.competition_subject_interface import CompetitionSubject

class CompetitionNotifier(db.Model, CompetitionSubject):
    __tablename__ = 'competition_notifier'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, default="Global Notifier")

    students = db.relationship('Student', secondary='notifier_student', backref='notifiers', lazy=True)

    # Singleton implementation because you will only over need one instance
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CompetitionNotifier, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def register_student(self, student):

        if student not in self.students:
            self.students.append(student)
            db.session.commit()

    def unregister_student(self, student):

        if student in self.students:
            self.students.remove(student)
            db.session.commit()

    def update_student_ranking(self, new_rank): # So this will be inside a for loop and run when the ranking is updated
        for student in self.students:
            student.update(new_rank)