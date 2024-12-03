from App.database import db
from App.models import UpdateLeaderboardCommand, GetCurrentLeaderboard, LeaderboardSnapshot, Student

# Function to create UpdateLeaderboardCommand
def create_update_leaderboard_command():
    try:
        command = UpdateLeaderboardCommand()
        db.session.add(command)
        db.session.commit()
        return command
    except Exception as e:
        print(f"Error creating UpdateLeaderboardCommand: {str(e)}")
        return None

# Function to execute UpdateLeaderboardCommand
def execute_update_leaderboard_command():

    command = create_update_leaderboard_command()
    if not command:
        print("Failed to create UpdateLeaderboardCommand.")
        return None

    try:
        command.execute()
        print("UpdateLeaderboardCommand executed successfully.")
        return command
    except Exception as e:
        print(f"Error executing UpdateLeaderboardCommand: {str(e)}")
        return None

# Function to create GetCurrentLeaderboard
def create_get_current_leaderboard_command():
    try:
        command = GetCurrentLeaderboard()
        db.session.add(command)
        db.session.commit()
        return command
    except Exception as e:
        print(f"Error creating GetCurrentLeaderboard command: {str(e)}")
        return None

# Function to execute GetCurrentLeaderboard
def execute_get_current_leaderboard_command():
    command = create_get_current_leaderboard_command()
    if not command:
        print("Failed to create GetCurrentLeaderboard command.")
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