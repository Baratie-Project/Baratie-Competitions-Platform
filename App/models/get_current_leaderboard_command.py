from App.database import db
from App.models.command import Command
from .student import Student
from .leaderboard_snapshot import LeaderboardSnapshot
from datetime import datetime
import json


class GetCurrentLeaderboard(Command):

    def execute(self):
        try:
            # Get the most recent leaderboard snapshot
            latest_snapshot = LeaderboardSnapshot.query.order_by(LeaderboardSnapshot.timestamp.desc()).first()

            if not latest_snapshot:
                print("No leaderboard snapshot available.")
                return None

            # Retrieve leaderboard data from the snapshot
            leaderboard_data = latest_snapshot.get_leaderboard_data()

            # Display or return the leaderboard data
            print(f"Leaderboard (as of {latest_snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}):")
            for entry in leaderboard_data:
                print(f"Rank {entry['curr_rank']}: Student ID {entry['student_id']} - Score {entry['rating_score']}")

            return leaderboard_data

        except Exception as e:
            print(f"Error retrieving leaderboard: {e}")
            return None