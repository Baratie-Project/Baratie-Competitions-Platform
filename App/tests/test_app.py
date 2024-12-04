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
          "rating_score": 250,
          "comp_count": 0,
          "curr_rank": 0,
          "historical_ranking": fetched_student.historical_ranking
      }
      self.assertDictEqual(fetched_student.get_json(), expected)


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