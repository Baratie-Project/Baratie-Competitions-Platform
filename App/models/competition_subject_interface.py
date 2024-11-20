from App.database import db

class CompetitionSubject:
    def register_student(self, observer):
        raise NotImplementedError

    def unregister_student(self, observer):
        raise NotImplementedError

    def update_student_ranking(self):
        raise NotImplementedError