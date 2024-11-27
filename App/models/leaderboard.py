from App.database import db
from .student import Student
from .leaderboard_snapshot import LeaderboardSnapshot
from datetime import datetime
import json


class Leaderboard(db.Model):
    def __init__(self):
        self.current_leaderboard = []

    def update_leaderboard(self):
        try:
            # Query all students and sort them by rating_score in descending order
            students = Student.query.order_by(Student.rating_score.desc()).all()

            # Create a snapshot of the current leaderboard
            self.current_leaderboard = []
            rank = 1
            snapshot_data = []

            for student in students:
                # Keep track of the previous rank
                student.prev_rank = student.curr_rank
                student.curr_rank = rank

                # Add to the snapshot data
                student_data = {
                    "student_id": student.id,
                    "rating_score": student.rating_score,
                    "curr_rank": student.curr_rank
                }
                snapshot_data.append(student_data)
                self.current_leaderboard.append(student_data)

                rank += 1

            # Save changes to the database
            db.session.commit()

            # Save a snapshot of the updated leaderboard and get the snapshot ID
            snapshot_id = self.take_snapshot(snapshot_data)

            # Save rank history with snapshot ID
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

    def get_all_snapshots(self):
        return LeaderboardSnapshot.query.order_by(LeaderboardSnapshot.timestamp).all()

    def get_current_leaderboard(self):
        return self.current_leaderboard
