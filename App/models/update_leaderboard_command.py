from App.database import db
from .student import Student
from .leaderboard_snapshot import LeaderboardSnapshot
from .notification import Notification  # Assuming Notification is already defined
from datetime import datetime
import json
from .command import Command

class UpdateLeaderboardCommand(Command):
    __tablename__ = 'update_leaderboard_command'
    id = db.Column(db.Integer, primary_key=True)
    
    def execute(self):
        try:
            # Query all students ordered by rating
            students = Student.query.order_by(Student.rating_score.desc()).all()

            # Create the current leaderboard
            rank = 1
            snapshot_data = []

            # Keep track of the original ranks before making updates
            original_ranks = {student.id: student.curr_rank for student in students}

            for student in students:
                if student.curr_rank != rank:
                    # Update ranks if there's a change
                    student.prev_rank = student.curr_rank
                    student.curr_rank = rank

                    # Generate a notification message
                    if student.curr_rank < student.prev_rank:
                        message = f'RANK : {student.curr_rank}. Congratulations! Your rank has gone up!'
                    else:
                        message = f'RANK : {student.curr_rank}. Oh no! Your rank has gone down.'

                    # Create a Notification instance and add it to the student
                    notification = Notification(student_id=student.id, message=message)
                    student.add_notification(notification)

                # Prepare snapshot data
                student_data = {
                    "student_id": student.id,
                    "rating_score": student.rating_score,
                    "curr_rank": student.curr_rank
                }
                snapshot_data.append(student_data)

                # Increment rank for the next student
                rank += 1

                # Save student changes to the database
                db.session.add(student)

            # Commit all student updates
            db.session.commit()

            # Take a snapshot
            snapshot_id = self.take_snapshot(snapshot_data)
            if snapshot_id is None:
                raise Exception("Snapshot creation failed.")

            # Save rank history ONLY for students whose rank changed
            for student in students:
                original_rank = original_ranks[student.id]  # Retrieve the original rank
                if student.curr_rank != original_rank:
                    student.save_rank_history(rank=student.curr_rank, leaderboard_snapshot_id=snapshot_id)

        except Exception as e:
            db.session.rollback()
            print(f"Error updating leaderboard: {e}")


    def take_snapshot(self, snapshot_data):
        try:
            snapshot = LeaderboardSnapshot(leaderboard_data=snapshot_data)
            db.session.add(snapshot)
            db.session.commit()
            return snapshot.id
        except Exception as e:
            db.session.rollback()
            print(f"Error saving snapshot: {e}")
            return None