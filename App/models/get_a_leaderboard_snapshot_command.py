from App.database import db
from App.models.command import Command
from .student import Student
from .leaderboard_snapshot import LeaderboardSnapshot
from datetime import datetime
import json

class GetALeaderboardSnapshot(Command):
    __tablename__ = 'get_a_current_leaderboard'
    def execute(self, snapshot_id):
        try:
            # Get the leaderboard snapshot by the given ID
            snapshot = LeaderboardSnapshot.query.filter_by(id=snapshot_id).first()

            if not snapshot:
                print(f"No leaderboard snapshot found for ID {snapshot_id}.")
                return None

            # Retrieve leaderboard data from the snapshot
            leaderboard_data = snapshot.get_leaderboard_data()

            # Display or return the leaderboard data
            print(f"Leaderboard (as of {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}):")
            for entry in leaderboard_data:
                print(f"Rank {entry['curr_rank']}: Student ID {entry['student_id']} - Score {entry['rating_score']}")

            return leaderboard_data

        except Exception as e:
            print(f"Error retrieving leaderboard snapshot for ID {snapshot_id}: {e}")
            return None