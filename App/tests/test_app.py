import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import *
from App.controllers import *


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UnitTests(unittest.TestCase):
    #User Unit Tests
    def test_new_user(self):
        user = User("ryan", "ryanpass")
        assert user.username == "ryan"

    def test_hashed_password(self):
        password = "ryanpass"
        hashed = generate_password_hash(password, method='sha256')
        user = User("ryan", password)
        assert user.password != password

    def test_check_password(self):
        password = "ryanpass"
        user = User("ryan", password)
        assert user.check_password(password)

    def test_invalid_username(self):
      user = User("", "password123")
      assert user.username == ""

    #Student Unit Tests
    def test_new_student(self):
      db.drop_all()
      db.create_all()
      student = Student("james", "jamespass")
      assert student.username == "james"

    def test_student_get_json(self):
      db.drop_all()
      db.create_all()
      
      student = Student("james", "jamespass")
      db.session.add(student)
      db.session.commit()
      
      fetched_student = Student.query.first()
      
      expected = {
          "id": fetched_student.id,
          "username": "james",
          "rating_score": 750,
          "comp_count": 0,
          "curr_rank": 0,
          "historical_ranking": fetched_student.historical_ranking
      }
      self.assertDictEqual(fetched_student.get_json(), expected)

    def test_create_duplicate_student(self):
      create_student("james", "jamespass")
      same_user = create_student("james", "jamespass")
      assert same_user is None 

    def test_get_student_by_id(self):
      student = create_student("test", "testuser")
      assert student is not None, "Student creation failed"  
      fetched_student = get_student(student.id)
      assert fetched_student is not None, "Fetching student failed"
      assert fetched_student.username == "test"

    def test_get_all_students(self):
      create_student("user1", "password1")
      create_student("user2", "password2")
      students = get_all_students()
      assert len(students) >= 2

    def test_update_student_username(self):
      student = create_student("testuser", "testpassword")
      updated_student = update_student(student.id, "updateduser")
      assert updated_student is not None
      assert updated_student.username == "updateduser"

    def test_update_rankings(self):
      db.drop_all()
      db.create_all()
      student1 = create_student("student1", "password1")
      student2 = create_student("student2", "password2")
      student1.rating_score = 300
      student2.rating_score = 250
      student1.comp_count = 1  
      student2.comp_count = 1  
      db.session.add(student1)
      db.session.add(student2)
      db.session.commit()

      leaderboard = update_rankings()
      assert len(leaderboard) == 2
      assert leaderboard[0]["placement"] == 1
      assert leaderboard[0]["student"] == "student1"

    def test_view_ranking_history(self):
      student = create_student("testuser", "testpassword")
      student.save_rank_history(1, 1)
      history = view_ranking_history(student.id)
      assert history is not None
      assert len(history) == 1
      assert history[0].rank == 1

    #Moderator Unit Tests
    def test_new_moderator(self):
      db.drop_all()
      db.create_all()
      mod = Moderator("robert", "robertpass")
      assert mod.username == "robert"

    def test_moderator_get_json(self):
      db.drop_all()
      db.create_all()
      mod = Moderator("robert", "robertpass")
      self.assertDictEqual(mod.get_json(), {"id":None, "username": "robert", "competitions": []})
    
    def test_get_moderator_by_id(self):
      moderator = Moderator("mod2", "modpass")
      db.session.add(moderator)
      db.session.commit()
      fetched_moderator = Moderator.query.get(moderator.id)
      assert fetched_moderator is not None
      assert fetched_moderator.username == "mod2"

    def test_add_results(self):
      moderator = create_moderator("mod6", "modpass")
      competition = Competition("Comp1", datetime.now(), "Online", 1, 100)
      team = Team("Team1")
      db.session.add_all([moderator, competition, team])
      db.session.commit()

      competition.moderators.append(moderator)
      db.session.commit()

      comp_team = CompetitionTeam(comp_id=competition.id, team_id=team.id)
      db.session.add(comp_team)
      db.session.commit()

      result = add_results("mod6", "Comp1", "Team1", 80)
      assert result is not None
      assert result.points_earned == 80
      assert result.rating_score > 0

    def test_calculate_expected_rank(self):
      rating = 1600
      opponents = [1500, 1550, 1700]
      result = calculate_expected_rank(rating, opponents)
      assert round(result, 2) == 1.57

    def test_update_ratings(self):
      db.drop_all()
      db.create_all()

      moderator = create_moderator("mod9", "modpass")
      competition = Competition("Comp3", datetime.now(), "Online", 1, 100)
      team = Team("Team2")
      student = Student("student1", "studentpass")
      db.session.add_all([moderator, competition, team, student])
      db.session.commit()

      team.students.append(student)
      db.session.add(team)
      competition.moderators.append(moderator)
      db.session.add(competition)

      comp_team = CompetitionTeam(comp_id=competition.id, team_id=team.id)
      db.session.add(comp_team)
      db.session.commit()

      result = update_ratings("mod9", "Comp3")
      assert result is not None
      assert student.rating_score != 250
      assert student.comp_count == 1

    #Team Unit Tests
    def test_new_team(self):
      db.drop_all()
      db.create_all()
      team = Team("Scrum Lords")
      assert team.name == "Scrum Lords"
    
    def test_team_get_json(self):
      db.drop_all()
      db.create_all()
      team = Team("Scrum Lords")
      self.assertDictEqual(team.get_json(), {"id":None, "name":"Scrum Lords", "students": []})
    
    def test_add_student(self):
      db.drop_all()
      db.create_all()

      team = Team("Team Awesome")
      student1 = Student("student1", "password1")
      student2 = Student("student2", "password2")
      db.session.add_all([team, student1, student2])
      db.session.commit()

      stud_team1 = team.add_student(student1)
      assert stud_team1 is not None  
      assert student1 in team.students  
      assert team in student1.teams  

      stud_team_duplicate = team.add_student(student1)
      assert stud_team_duplicate is None  

      stud_team2 = team.add_student(student2)
      assert stud_team2 is not None  
      assert student2 in team.students  
      assert team in student2.teams  

      assert len(team.students) == 2

    #Competition Unit Tests
    def test_new_competition(self):
      db.drop_all()
      db.create_all()
      competition = Competition("RunTime", datetime.strptime("09-02-2024", "%d-%m-%Y"), "St. Augustine", 1, 25)
      assert competition.name == "RunTime" and competition.date.strftime("%d-%m-%Y") == "09-02-2024" and competition.location == "St. Augustine" and competition.level == 1 and competition.max_score == 25

    def test_competition_get_json(self):
      db.drop_all()
      db.create_all()
      competition = Competition("RunTime", datetime.strptime("09-02-2024", "%d-%m-%Y"), "St. Augustine", 1, 25)
      self.assertDictEqual(competition.get_json(), {"id": None, "name": "RunTime", "date": "09-02-2024", "location": "St. Augustine", "level": 1, "max_score": 25, "moderators": [], "teams": []})
    
    #Notification Unit Tests
    def test_new_notification(self):
      db.drop_all()
      db.create_all()
      notification = Notification(1, "Ranking changed!")
      assert notification.student_id == 1 and notification.message == "Ranking changed!"

    def test_notification_get_json(self):
      db.drop_all()
      db.create_all()
      notification = Notification(1, "Ranking changed!")
      self.assertDictEqual(notification.get_json(), {"id": None, "student_id": 1, "notification": "Ranking changed!"})
    """
    #Ranking Unit Tests
    def test_new_ranking(self):
      db.drop_all()
      db.create_all()
      ranking = Ranking(1)
      assert ranking.student_id == 1
  
    def test_set_points(self):
      db.drop_all()
      db.create_all()
      ranking = Ranking(1)
      ranking.set_points(15)
      assert ranking.total_points == 15

    def test_set_ranking(self):
      db.drop_all()
      db.create_all()
      ranking = Ranking(1)
      ranking.set_ranking(1)
      assert ranking.curr_ranking == 1

    def test_previous_ranking(self):
      db.drop_all()
      db.create_all()
      ranking = Ranking(1)
      ranking.set_previous_ranking(1)
      assert ranking.prev_ranking == 1

    def test_ranking_get_json(self):
      db.drop_all()
      db.create_all()
      ranking = Ranking(1)
      ranking.set_points(15)
      ranking.set_ranking(1)
      self.assertDictEqual(ranking.get_json(), {"rank":1, "total points": 15})
    """
    #CompetitionTeam Unit Tests
    def test_new_competition_team(self):
      db.drop_all()
      db.create_all()
      competition_team = CompetitionTeam(1, 1)
      assert competition_team.comp_id == 1 and competition_team.team_id == 1

    def test_competition_team_update_points(self):
      db.drop_all()
      db.create_all()
      competition_team = CompetitionTeam(1, 1)
      competition_team.update_points(15)
      assert competition_team.points_earned == 15

    def test_competition_team_update_rating(self):
      db.drop_all()
      db.create_all()
      competition_team = CompetitionTeam(1, 1)
      competition_team.update_rating(12)
      assert competition_team.rating_score == 12

    def test_competition_team_get_json(self):
      db.drop_all()
      db.create_all()
      competition_team = CompetitionTeam(1, 1)
      competition_team.update_points(15)
      competition_team.update_rating(12)
      self.assertDictEqual(competition_team.get_json(), {"id": None, "team_id": 1, "competition_id": 1, "points_earned": 15, "rating_score": 12})

    #CompetitionModerator Unit Tests
    def test_new_competition_moderator(self):
      db.drop_all()
      db.create_all()
      competition_moderator = CompetitionModerator(1, 1)
      assert competition_moderator.comp_id == 1 and competition_moderator.mod_id == 1

    def test_competition_moderator_get_json(self):
      db.drop_all()
      db.create_all()
      competition_moderator = CompetitionModerator(1, 1)
      self.assertDictEqual(competition_moderator.get_json(), {"id": None, "competition_id": 1, "moderator_id": 1})

    #StudentTeam Unit Tests
    def test_new_student_team(self):
      db.drop_all()
      db.create_all()
      student_team = StudentTeam(1, 1)
      assert student_team.student_id == 1 and student_team.team_id == 1
    
    def test_student_team_get_json(self):
      db.drop_all()
      db.create_all()
      student_team = StudentTeam(1, 1)
      self.assertDictEqual(student_team.get_json(), {"id": None, "student_id": 1, "team_id": 1})

    #Command Unit Tests
    def test_get_current_leaderboard(self):
      db.drop_all()
      db.create_all()

      leaderboard_data = [
          {"student_id": 1, "curr_rank": 1, "rating_score": 900},
          {"student_id": 2, "curr_rank": 2, "rating_score": 850},
      ]
      snapshot = LeaderboardSnapshot(leaderboard_data=leaderboard_data) 
      db.session.add(snapshot)
      db.session.commit()

      command = GetCurrentLeaderboard()
      result = command.execute()

      assert result is not None
      assert len(result) == 2
      assert result[0]["student_id"] == 1
      assert result[1]["student_id"] == 2

    def test_update_leaderboard_command(self):
      db.drop_all()
      db.create_all()

      studentA = Student(username="studentA", password="pass")
      studentB = Student(username="studentB", password="pass")

      studentA.rating_score = 900
      studentA.curr_rank = 1
      studentB.rating_score = 850
      studentB.curr_rank = 2

      db.session.add_all([studentA, studentB])
      db.session.commit()

      students = Student.query.all()
      assert len(students) == 2, "Unexpected number of students in the database"

      command = UpdateLeaderboardCommand()
      command.execute()

      updated_studentA = Student.query.filter_by(username="studentA").first()
      updated_studentB = Student.query.filter_by(username="studentB").first()

      assert updated_studentA.curr_rank == 1
      assert updated_studentB.curr_rank == 2

      snapshot = LeaderboardSnapshot.query.first()
      assert snapshot is not None
      assert len(snapshot.get_leaderboard_data()) == 2, "Unexpected number of snapshot entries"

    def test_get_a_leaderboard_snapshot(self):
      db.drop_all()
      db.create_all()

      leaderboard_data = [
          {"student_id": 1, "curr_rank": 1, "rating_score": 900},
          {"student_id": 2, "curr_rank": 2, "rating_score": 850},
      ]
      snapshot = LeaderboardSnapshot(leaderboard_data=leaderboard_data)
      db.session.add(snapshot)
      db.session.commit()

      command = GetALeaderboardSnapshot()
      result = command.execute(snapshot.id)

      assert result is not None
      assert len(result) == 2
      assert result[0]["student_id"] == 1
      assert result[1]["student_id"] == 2


'''
    Integration Tests
'''
class IntegrationTests(unittest.TestCase):
    
    #Feature 1 Integration Tests
    def test1_create_competition(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      assert comp.name == "RunTime" and comp.date.strftime("%d-%m-%Y") == "29-03-2024" and comp.location == "St. Augustine" and comp.level == 2 and comp.max_score == 25

    def test2_create_competition(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      self.assertDictEqual(comp.get_json(), {"id": 1, "name": "RunTime", "date": "29-03-2024", "location": "St. Augustine", "level": 2, "max_score": 25, "moderators": ["debra"], "teams": []})
      
    #Feature 2 Integration Tests
    def test1_add_results(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      students = [student1.username, student2.username, student3.username]
      team = add_team(mod.username, comp.name, "Runtime Terrors", students)
      comp_team = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      assert comp_team.points_earned == 15
    
    def test2_add_results(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      students = [student1.username, student2.username, student3.username]
      add_team(mod.username, comp.name, "Runtime Terrors", students)
      comp_team = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      students = [student1.username, student4.username, student5.username]
      team = add_team(mod.username, comp.name, "Scrum Lords", students)
      assert team == None
    
    def test3_add_results(self):
      db.drop_all()
      db.create_all()
      mod1 = create_moderator("debra", "debrapass")
      mod2 = create_moderator("robert", "robertpass")
      comp = create_competition(mod1.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      students = [student1.username, student2.username, student3.username]
      team = add_team(mod2.username, comp.name, "Runtime Terrors", students)
      assert team == None

    #Feature 3 Integration Tests
    def test_display_student_info(self):
      app = create_app()
      with app.app_context():
          db.drop_all()
          db.create_all()

          mod = create_moderator("debra", "debrapass")
          comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)

          student1 = create_student("james", "jamespass")
          student2 = create_student("steven", "stevenpass")
          student3 = create_student("emily", "emilypass")
          students = [student1.username, student2.username, student3.username]
          add_team(mod.username, comp.name, "Runtime Terrors", students)
          add_results(mod.username, comp.name, "Runtime Terrors", 15)

          update_ratings(mod.username, comp.name)
          update_rankings()

          actual_info = display_student_info("james")

          expected_info = {
              "profile": {
                  "id": student1.id,
                  "username": student1.username,
                  "rating_score": student1.rating_score,  
                  "comp_count": student1.comp_count,
                  "curr_rank": student1.curr_rank
              },
              "competitions": ["RunTime"]
          }

          self.assertEqual(actual_info["profile"]["id"], expected_info["profile"]["id"])
          self.assertEqual(actual_info["profile"]["username"], expected_info["profile"]["username"])
          self.assertEqual(actual_info["profile"]["rating_score"], expected_info["profile"]["rating_score"])
          self.assertEqual(actual_info["profile"]["comp_count"], expected_info["profile"]["comp_count"])
          self.assertEqual(actual_info["profile"]["curr_rank"], expected_info["profile"]["curr_rank"])
          self.assertListEqual(actual_info["competitions"], expected_info["competitions"])


    #Feature 4 Integration Tests
    def test_display_competition(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      student7 = create_student("isabella", "isabellapass")
      student8 = create_student("richard", "richardpass")
      student9 = create_student("jessica", "jessicapass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp.name, "Runtime Terrors", students1)
      comp_team1 = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp.name, "Scrum Lords", students2)
      comp_team2 = add_results(mod.username, comp.name, "Scrum Lords", 12)
      students3 = [student7.username, student8.username, student9.username]
      team3 = add_team(mod.username, comp.name, "Beyond Infinity", students3)
      comp_team = add_results(mod.username, comp.name, "Beyond Infinity", 10)
      update_ratings(mod.username, comp.name)
      update_rankings()
      self.assertDictEqual(comp.get_json(), {'id': 1, 'name': 'RunTime', 'date': '29-03-2024', 'location': 'St. Augustine', 'level': 2, 'max_score': 25, 'moderators': ['debra'], 'teams': ['Runtime Terrors', 'Scrum Lords', 'Beyond Infinity']})

    #Feature 5 Integration Tests
    def test_display_rankings(self):
      app = create_app()
      with app.app_context():
          db.drop_all()
          db.create_all()

          mod = create_moderator("debra", "debrapass")
          comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)

          student1 = create_student("james", "jamespass")
          student2 = create_student("steven", "stevenpass")
          student3 = create_student("emily", "emilypass")
          student4 = create_student("mark", "markpass")
          student5 = create_student("eric", "ericpass")
          student6 = create_student("ryan", "ryanpass")

          team1_students = [student1.username, student2.username, student3.username]
          team2_students = [student4.username, student5.username, student6.username]

          add_team(mod.username, comp.name, "Runtime Terrors", team1_students)
          add_results(mod.username, comp.name, "Runtime Terrors", 15)

          add_team(mod.username, comp.name, "Scrum Lords", team2_students)
          add_results(mod.username, comp.name, "Scrum Lords", 10)

          update_ratings(mod.username, comp.name)
          command = UpdateLeaderboardCommand()
          command.execute()

          snapshot = LeaderboardSnapshot.query.order_by(LeaderboardSnapshot.timestamp.desc()).first()
          assert snapshot is not None, "Leaderboard snapshot was not created."

          leaderboard = snapshot.get_leaderboard_data()
          print("Display Rankings Output:", leaderboard)

          # Check the structure of the leaderboard
          for i, entry in enumerate(leaderboard):
              self.assertIn("student_id", entry)
              self.assertIn("username", entry)
              self.assertIn("rating_score", entry)
              self.assertIn("curr_rank", entry)
              self.assertIsInstance(entry["rating_score"], float)

          # Check the order of ranking
          sorted_leaderboard = sorted(leaderboard, key=lambda x: x["rating_score"], reverse=True)
          self.assertListEqual(leaderboard, sorted_leaderboard)

    #Feature 6 Integration Tests
    def test1_display_notification(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp.name, "Runtime Terrors", students1)
      comp_team1 = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp.name, "Scrum Lords", students2)
      comp_team2 = add_results(mod.username, comp.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp.name)
      update_rankings()
      self.assertDictEqual(display_notifications("james"), {"notifications": [{"ID": 1, "Notification": "RANK : 1. Congratulations on your first rank!"}]})

    def test2_display_notification(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp1 = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      comp2 = create_competition(mod.username, "Hacker Cup", "23-02-2024", "Macoya", 1, 30)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp1.name, "Runtime Terrors", students1)
      comp1_team1 = add_results(mod.username, comp1.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp1.name, "Scrum Lords", students2)
      comp1_team2 = add_results(mod.username, comp1.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp1.name)
      update_rankings()
      students3 = [student1.username, student4.username, student5.username]
      team3 = add_team(mod.username, comp2.name, "Runtime Terrors", students3)
      comp_team3 = add_results(mod.username, comp2.name, "Runtime Terrors", 15)
      students4 = [student2.username, student3.username, student6.username]
      team4 = add_team(mod.username, comp2.name, "Scrum Lords", students4)
      comp_team4 = add_results(mod.username, comp2.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp2.name)
      update_rankings()
      self.assertDictEqual(display_notifications("james"), {"notifications": [{"ID": 1, "Notification": "RANK : 1. Congratulations on your first rank!"}, {"ID": 7, "Notification": "RANK : 1. Well done! You retained your rank."}]})

    def test3_display_notification(self):
      app = create_app()  
      with app.app_context():  
          db.drop_all()
          db.create_all()

          mod = create_moderator("debra", "debrapass")
          comp1 = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
          comp2 = create_competition(mod.username, "Hacker Cup", "23-02-2024", "Macoya", 1, 20)

          student1 = create_student("james", "jamespass")
          student2 = create_student("steven", "stevenpass")
          student3 = create_student("emily", "emilypass")
          student4 = create_student("mark", "markpass")
          student5 = create_student("eric", "ericpass")
          student6 = create_student("ryan", "ryanpass")

          students1 = [student1.username, student2.username, student3.username]
          add_team(mod.username, comp1.name, "Runtime Terrors", students1)
          add_results(mod.username, comp1.name, "Runtime Terrors", 15)

          students2 = [student4.username, student5.username, student6.username]
          add_team(mod.username, comp1.name, "Scrum Lords", students2)
          add_results(mod.username, comp1.name, "Scrum Lords", 10)

          update_ratings(mod.username, comp1.name)
          update_rankings()

          students3 = [student1.username, student4.username, student5.username]
          add_team(mod.username, comp2.name, "Runtime Terrors", students3)
          add_results(mod.username, comp2.name, "Runtime Terrors", 20)

          students4 = [student2.username, student3.username, student6.username]
          add_team(mod.username, comp2.name, "Scrum Lords", students4)
          add_results(mod.username, comp2.name, "Scrum Lords", 10)

          update_ratings(mod.username, comp2.name)
          update_rankings()

          response = display_notifications("mark")

          print("Notifications for Mark:", response)

          expected_notifications = [
              {"Notification": "RANK : 4. Congratulations on your first rank!"},
              {"Notification": "RANK : 4. Well done! You retained your rank."}  # Adjust if rank actually changes to 2
          ]

          actual_notifications = [{"Notification": n["Notification"]} for n in response["notifications"]]

          self.assertListEqual(actual_notifications, expected_notifications)


    def test1_add_mod(self):
      db.drop_all()
      db.create_all()
      mod1 = create_moderator("debra", "debrapass")
      mod2 = create_moderator("robert", "robertpass")
      comp = create_competition(mod1.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      assert add_mod(mod1.username, comp.name, mod2.username) != None
       
    def test2_add_mod(self):
      db.drop_all()
      db.create_all()
      mod1 = create_moderator("debra", "debrapass")
      mod2 = create_moderator("robert", "robertpass")
      mod3 = create_moderator("raymond", "raymondpass")
      comp = create_competition(mod1.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      assert add_mod(mod2.username, comp.name, mod3.username) == None
    
    def test_student_list(self):
      app = create_app()  
      with app.app_context():
          db.drop_all()
          db.create_all()

          mod = create_moderator("debra", "debrapass")
          comp1 = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
          comp2 = create_competition(mod.username, "Hacker Cup", "23-02-2024", "Macoya", 1, 20)

          student1 = create_student("james", "jamespass")
          student2 = create_student("steven", "stevenpass")
          student3 = create_student("emily", "emilypass")
          student4 = create_student("mark", "markpass")
          student5 = create_student("eric", "ericpass")
          student6 = create_student("ryan", "ryanpass")

          students1 = [student1.username, student2.username, student3.username]
          add_team(mod.username, comp1.name, "Runtime Terrors", students1)
          add_results(mod.username, comp1.name, "Runtime Terrors", 15)

          students2 = [student4.username, student5.username, student6.username]
          add_team(mod.username, comp1.name, "Scrum Lords", students2)
          add_results(mod.username, comp1.name, "Scrum Lords", 10)

          update_ratings(mod.username, comp1.name)
          update_rankings()

          students3 = [student1.username, student4.username, student5.username]
          add_team(mod.username, comp2.name, "Runtime Terrors", students3)
          add_results(mod.username, comp2.name, "Runtime Terrors", 20)

          students4 = [student2.username, student3.username, student6.username]
          add_team(mod.username, comp2.name, "Scrum Lords", students4)
          add_results(mod.username, comp2.name, "Scrum Lords", 10)

          update_ratings(mod.username, comp2.name)
          update_rankings()

          actual_students = get_all_students_json()

          for student in actual_students:
              self.assertIsInstance(student["rating_score"], float)  
              self.assertIn("id", student)
              self.assertIn("username", student)
              self.assertIn("comp_count", student)
              self.assertIn("curr_rank", student)

          expected_ids_usernames = [
              {"id": 1, "username": "james"},
              {"id": 2, "username": "steven"},
              {"id": 3, "username": "emily"},
              {"id": 4, "username": "mark"},
              {"id": 5, "username": "eric"},
              {"id": 6, "username": "ryan"},
          ]

          actual_ids_usernames = [{"id": s["id"], "username": s["username"]} for s in actual_students]

          self.assertListEqual(actual_ids_usernames, expected_ids_usernames)


    def test_comp_list(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp1 = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      comp2 = create_competition(mod.username, "Hacker Cup", "23-02-2024", "Macoya", 1, 20)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp1.name, "Runtime Terrors", students1)
      comp1_team1 = add_results(mod.username, comp1.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp1.name, "Scrum Lords", students2)
      comp1_team2 = add_results(mod.username, comp1.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp1.name)
      update_rankings()
      students3 = [student1.username, student4.username, student5.username]
      team3 = add_team(mod.username, comp2.name, "Runtime Terrors", students3)
      comp_team3 = add_results(mod.username, comp2.name, "Runtime Terrors", 20)
      students4 = [student2.username, student3.username, student6.username]
      team4 = add_team(mod.username, comp2.name, "Scrum Lords", students4)
      comp_team4 = add_results(mod.username, comp2.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp2.name)
      update_rankings()
      self.assertListEqual(get_all_competitions_json(), [{"id": 1, "name": "RunTime", "date": "29-03-2024", "location": "St. Augustine", "level": 2, "max_score": 25, "moderators": ["debra"], "teams": ["Runtime Terrors", "Scrum Lords"]}, {"id": 2, "name": "Hacker Cup", "date": "23-02-2024", "location": "Macoya", "level": 1, "max_score": 20, "moderators": ["debra"], "teams": ["Runtime Terrors", "Scrum Lords"]}])