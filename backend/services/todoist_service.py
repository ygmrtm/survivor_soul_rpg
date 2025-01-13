import requests
from config import TODOIST_API_KEY
from todoist_api_python.api import TodoistAPI

class TodoistService:
    base_url = "https://api.todoist.com/rest/v2"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {TODOIST_API_KEY}",
            "Content-Type": "application/json"
        }

    def get_todoist_api(self):
        return TodoistAPI(TODOIST_API_KEY)
        
    def add_task(self, project_id, content, due_date, priority=1
                , description='', section_id=None, labels=None):
        task = None
        try:
            api = self.get_todoist_api()
            task = api.add_task(content=content, project_id=project_id, due_date=due_date 
                                , priority=priority, description=description
                                , section_id=section_id, labels=labels)
            print(task)
        except Exception as error:
            print(error)
            raise
        return task  
        
    def get_projects(self):
        projects = None
        try:
            api = self.get_todoist_api()
            projects = api.get_projects()
            print(projects)
        except Exception as error:
            print(error)
            raise
        return projects
