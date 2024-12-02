import math
from App.database import db
from App.models import Moderator, Competition, Team, CompetitionTeam

MIN_RATING = 100  # Define a minimum rating threshold
MAX_PENALTY = 5   # Define a maximum penalty for low-rated participants

def create_moderator(username, password):
    mod = get_moderator_by_username(username)
    if mod:
        print(f'{username} already exists!')
        return None

    newMod = Moderator(username=username, password=password)
    try:
        db.session.add(newMod)
        db.session.commit()
        print(f'New Moderator: {username} created!')
        return newMod
    except Exception as e:
        db.session.rollback()
        print(f'Something went wrong creating {username}')
        return None

def get_moderator_by_username(username):
    return Moderator.query.filter_by(username=username).first()

def get_moderator(id):
    return Moderator.query.get(id)

def get_all_moderators():
    return Moderator.query.all()

def get_all_moderators_json():
    mods = Moderator.query.all()
    if not mods:
        return []
    mods_json = [mod.get_json() for mod in mods]
    return mods_json

def update_moderator(id, username):
    mod = get_moderator(id)
    if mod:
        mod.username = username
        try:
            db.session.add(mod)
            db.session.commit()
            print("Username was updated!")
            return mod
        except Exception as e:
            db.session.rollback()
            print("Username was not updated!")
            return None
    print("ID: {id} does not exist!")
    return None

def add_mod(mod1_name, comp_name, mod2_name):
    mod1 = Moderator.query.filter_by(username=mod1_name).first()
    comp = Competition.query.filter_by(name=comp_name).first()
    mod2 = Moderator.query.filter_by(username=mod2_name).first()

    if not mod1:
        print(f'Moderator: {mod1_name} not found!')
        return None
    elif not comp:
        print(f'Competition: {comp_name} not found!')
        return None
    elif not mod2:
        print(f'Moderator: {mod2_name} not found!')
        return None
    elif not mod1 in comp.moderators:
        print(f'{mod1_name} is not authorized to add results for {comp_name}!')
        return None
    else:
        return comp.add_mod(mod2)
                
def add_results(mod_name, comp_name, team_name, score):
    mod = Moderator.query.filter_by(username=mod_name).first()
    comp = Competition.query.filter_by(name=comp_name).first()
    teams = Team.query.filter_by(name=team_name).all()

    if not mod:
        print(f'{mod_name} was not found!')
        return None
    else:
        if not comp:
            print(f'{comp_name} was not found!')
            return None
        elif comp.confirm:
            print(f'Results for {comp_name} have already been finalized!')
            return None
        elif mod not in comp.moderators:
            print(f'{mod_name} is not authorized to add results for {comp_name}!')
            return None
        else:
            for team in teams:
                comp_team = CompetitionTeam.query.filter_by(comp_id=comp.id, team_id=team.id).first()

                if comp_team:
                    comp_team.points_earned = score
                    comp_team.rating_score = (score/comp.max_score) * 20 * comp.level
        
                    try:
                        db.session.add(comp_team)
                        db.session.commit()
                        print(f'Score successfully added for {team_name}!')
                        return comp_team
                    except Exception as e:
                        db.session.rollback()
                        print("Something went wrong!")
                        return None
    return None




def calculate_expected_rank(rating, opponents):
    """
    Calculate the expected rank of a participant based on their rating and opponents' ratings.
    """
    return sum(1 / (1 + math.pow(10, (opponent - rating) / 400)) for opponent in opponents)


def calculate_dynamic_k(rating):
    """
    Calculate a dynamic K-factor based on the participant's current rating.
    Lower-rated participants get a smaller K to reduce penalties.
    """
    base_k = 4  # Base K-factor
    scaling_factor = 1 + max(0, 400 - rating) / 400  # Scale K dynamically
    return base_k * scaling_factor

def calculate_rating_change(rating, actual_rank, expected_rank):
    """
    Calculate the change in Elo rating for a participant with dynamic K.
    """
    k = calculate_dynamic_k(rating)
    return k * (expected_rank - actual_rank)


def update_ratings(mod_name, comp_name):
    mod = Moderator.query.filter_by(username=mod_name).first()
    comp = Competition.query.filter_by(name=comp_name).first()

    if not mod:
        print(f'{mod_name} was not found!')
        return None
    elif not comp:
        print(f'{comp_name} was not found!')
        return None
    elif comp.confirm:
        print(f'Results for {comp_name} have already been finalized!')
        return None
    elif mod not in comp.moderators:
        print(f'{mod_name} is not authorized to update ratings for {comp_name}!')
        return None

    # Fetch students and their scores
    comp_teams = CompetitionTeam.query.filter_by(comp_id=comp.id).all()
    participants = []
    for comp_team in comp_teams:
        team = Team.query.filter_by(id=comp_team.team_id).first()
        participants.extend(team.students)

    if not participants:
        print("No participants found in this competition.")
        return None

    # Prepare participant data
    participants = sorted(participants, key=lambda s: s.rating_score, reverse=True)
    actual_ranks = {stud.id: rank + 1 for rank, stud in enumerate(participants)}
    ratings = [stud.rating_score for stud in participants]

    # Update ratings for each participant
    for student in participants:
        # Calculate expected rank
        expected_rank = calculate_expected_rank(student.rating_score, ratings)
        actual_rank = actual_ranks[student.id]

        # Calculate rating change with dynamic K
        rating_change = calculate_rating_change(
            rating=student.rating_score,
            actual_rank=actual_rank,
            expected_rank=expected_rank,
        )

        # Apply rating change
        student.rating_score += rating_change
        student.comp_count += 1

        try:
            db.session.add(student)
        except Exception as e:
            db.session.rollback()
            print(f"Error updating student {student.id}: {e}")
            return None

    # Mark the competition as finalized
    comp.confirm = True
    try:
        db.session.add(comp)
        db.session.commit()
        print("Ratings updated successfully using dynamic K Elo!")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error finalizing results: {e}")
        return None

