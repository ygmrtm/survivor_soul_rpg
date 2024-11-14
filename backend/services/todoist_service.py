import requests
from config import TODOIST_API_KEY

class TodoistService:
    base_url = "https://api.todoist.com/rest/v2"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {TODOIST_API_KEY}",
            "Content-Type": "application/json"
        }

    def create_task(self, content, due_date=None):
        """Create a new Todoist task."""
        data = {"content": content}
        if due_date:
            data["due_date"] = due_date
        url = f"{self.base_url}/tasks"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
