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
            students = Student.query.order_by(Student.rating_score.desc()).all()

            # Create the current leaderboard
            rank = 1
            snapshot_data = []

            for student in students:
                # Save the previous rank
                student.prev_rank = student.curr_rank
                # Update the current rank
                student.curr_rank = rank
                
                # Generate a notification message
                if student.prev_rank == 0:
                    message = f'RANK : {student.curr_rank}. Congratulations on your first rank!'
                elif student.curr_rank == student.prev_rank:
                    message = f'RANK : {student.curr_rank}. Well done! You retained your rank.'
                elif student.curr_rank < student.prev_rank:
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

            # Save rank history and update the current leaderboard
            for student in students:
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
