from todoist_api_python.api import TodoistAPI
from config import TODOIST_API_KEY

class TodoistService:
    base_url = "https://api.todoist.com/rest/v2"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {TODOIST_API_KEY}",
            "Content-Type": "application/json"
        }
        self._api = None  # Initialize _api to None

    @property
    def api(self):
        """Lazy loading of Todoist API client."""
        if self._api is None:
            self._api = TodoistAPI(TODOIST_API_KEY)  # Initialize _api here
        return self._api

    def healthcheck(self):
        """
        Check the health status of the Todoist service.
        
        Returns:
            dict: A dictionary containing the health status information
                {
                    'status': str ('healthy' or 'unhealthy'),
                    'message': str (status message or error details),
                    'api_connected': bool (True if API is accessible),
                    'projects_accessible': bool (True if can fetch projects)
                }
        """
        health_status = {
            'status': 'unhealthy',
            'message': '',
            'api_connected': False,
            'projects_accessible': False
        }

        try:
            # Test API Connection
            projects = self.api.get_projects()  # Accessing the api property
            
            # If we can fetch projects, the API is working
            health_status['api_connected'] = True
            health_status['projects_accessible'] = True
            health_status['status'] = 'healthy'
            health_status['message'] = 'Todoist service is functioning normally'
            
            # Additional connection info
            health_status['project_count'] = len(projects)
            
        except Exception as e:
            health_status['message'] = f"Todoist service error: {str(e)}"
            
            # Try to provide more specific error information
            if "Unauthorized" in str(e):
                health_status['message'] = "Authentication failed: Invalid API token"
            elif "Connection" in str(e):
                health_status['message'] = "Could not connect to Todoist API: Connection error"
            
        return health_status

    def check_connection(self):
        """
        Simple connection check that returns a boolean.
        
        Returns:
            bool: True if the connection is working, False otherwise
        """
        try:
            self.api.get_projects()  # Accessing the api property
            return True
        except Exception as e:
            print(f"❌ Todoist connection error: {str(e)}")
            return False

    def get_todoist_api(self):
        return TodoistAPI(TODOIST_API_KEY)
        
    def add_task(self, project_id, properties):
        task = None
        try:
            task = self. api.add_task(content=properties['content'], project_id=project_id
                                    , due_date=properties['due_date'], priority=properties['priority']
                                    , description=properties['description'], section_id=properties['section_id']
                                    , labels=properties['labels'])
            print(task)
        except Exception as error:
            print(error)
            raise
        return task  
        
    def get_projects(self):
        projects = None
        try:
            projects = self.api.get_projects()
            # print(projects)
        except Exception as error:
            print(error)
            raise
        return projects
