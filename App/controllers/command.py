from App.database import db
from App.models import UpdateLeaderboardCommand, GetCurrentLeaderboard, LeaderboardSnapshot, Student
from App.models.get_a_leaderboard_snapshot_command import GetALeaderboardSnapshot

# Function to retrieve or create UpdateLeaderboardCommand
def get_or_create_update_leaderboard_command():
    try:
        # Check if a command already exists
        command = UpdateLeaderboardCommand.query.first()
        if not command:
            # Create a new command if none exists
            command = UpdateLeaderboardCommand()
            db.session.add(command)
            db.session.commit()
        return command
    except Exception as e:
        print(f"Error retrieving or creating UpdateLeaderboardCommand: {str(e)}")
        return None

# Function to execute UpdateLeaderboardCommand
def execute_update_leaderboard_command():
    command = get_or_create_update_leaderboard_command()
    if not command:
        print("Failed to retrieve or create UpdateLeaderboardCommand.")
        return None

    try:
        command.execute()
        print("UpdateLeaderboardCommand executed successfully.")
        return command
    except Exception as e:
        print(f"Error executing UpdateLeaderboardCommand: {str(e)}")
        return None

# Function to retrieve or create GetCurrentLeaderboard
def get_or_create_get_current_leaderboard_command():
    try:
        # Check if a command already exists
        command = GetCurrentLeaderboard.query.first()
        if not command:
            # Create a new command if none exists
            command = GetCurrentLeaderboard()
            db.session.add(command)
            db.session.commit()
        return command
    except Exception as e:
        print(f"Error retrieving or creating GetCurrentLeaderboard command: {str(e)}")
        return None

# Function to execute GetCurrentLeaderboard
def execute_get_current_leaderboard_command():
    command = get_or_create_get_current_leaderboard_command()
    if not command:
        print("Failed to retrieve or create GetCurrentLeaderboard command.")
        return None

    try:
        leaderboard_data = command.execute()
        if leaderboard_data:
            print("GetCurrentLeaderboardCommand executed successfully.")
            return leaderboard_data
        else:
            print("No leaderboard data retrieved.")
            return None
    except Exception as e:
        print(f"Error executing GetCurrentLeaderboardCommand: {str(e)}")
        return None

# Function to retrieve or create GetALeaderboardSnapshot
def get_or_create_get_leaderboard_snapshot_command():
    try:
        # Check if a command already exists
        command = GetALeaderboardSnapshot.query.first()
        if not command:
            # Create a new command if none exists
            command = GetALeaderboardSnapshot()
            db.session.add(command)
            db.session.commit()
        return command
    except Exception as e:
        print(f"Error retrieving or creating GetALeaderboardSnapshot command: {str(e)}")
        return None

# Function to execute GetALeaderboardSnapshot for a specific snapshot ID
def execute_get_leaderboard_snapshot_command(snapshot_id):
    command = get_or_create_get_leaderboard_snapshot_command()
    if not command:
        print("Failed to retrieve or create GetALeaderboardSnapshot command.")
        return None

    try:
        leaderboard_data = command.execute(snapshot_id)
        if leaderboard_data:
            print(f"GetALeaderboardSnapshotCommand executed successfully for snapshot ID {snapshot_id}.")
            return leaderboard_data
        else:
            print(f"No leaderboard data retrieved for snapshot ID {snapshot_id}.")
            return None
    except Exception as e:
        print(f"Error executing GetALeaderboardSnapshotCommand for snapshot ID {snapshot_id}: {str(e)}")
        return None
