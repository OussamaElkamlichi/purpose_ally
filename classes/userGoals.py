from dbAgent.agent import goals_seeding, cron_seed

class UserGoals:
    def __init__(self, user_id):
        # Dictionary to hold main goals and their associated sub-goals
        self.goals = {}

    def add_main_goal(self, user_id, main_goal):
        # Check if the main goal exists for this user
        if main_goal not in self.goals:
            # Initialize an empty list for sub-goals
            self.goals[main_goal] = []

    def add_sub_goal(self, user_id, main_goal, sub_goal):
        # Add the sub-goal to the main goal's list
        if main_goal in self.goals:
            self.goals[main_goal].append(sub_goal)

    def get_goals_list(self):
        if not self.goals:
            return "لا توجد أهداف."
        return "\n".join([f"{main_goal}: {', '.join(sub_goals)}" for main_goal, sub_goals in self.goals.items()])
        
    def launch(self, user_id):
        res = goals_seeding(self.goals, user_id)
        return res
    
    def goals_count(self):
        return self.goals
    
    def cron_seed(self, user_id, params):
        res = cron_seed(user_id, params)
        return res
