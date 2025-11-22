from ticktick import TickTick
from config import TICKTICK_ACCESS_TOKEN

class TickTickService:
    _instance = None  # Class variable to hold the single instance

    def __new__(cls, *args, **kwargs):
        """Override __new__ to implement Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(TickTickService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the TickTick service."""
        if not hasattr(self, 'initialized'):  # Check if already initialized
            self._api = TickTick(access_token=TICKTICK_ACCESS_TOKEN)
            self.initialized = True  # Mark as initialized
            print(self.healthcheck())

    def healthcheck(self):
        """
        Check the health status of the TickTick service.

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
            'message': '❌',
            'api_connected': False,
            'projects_accessible': False
        }

        try:
            # Test API Connection
            projects = self._api.get_projects()

            # If we can fetch projects, the API is working
            health_status['api_connected'] = True
            health_status['projects_accessible'] = True
            health_status['status'] = 'healthy'
            health_status['message'] = '✅ TickTick service is functioning normally'

            # Additional connection info
            health_status['project_count'] = len(projects)

        except Exception as e:
            health_status['message'] = f"❌ TickTick service error: {str(e)}"

            # Try to provide more specific error information
            if "401" in str(e) or "Unauthorized" in str(e):
                health_status['message'] = "❌ Authentication failed: Invalid API token"
            elif "Connection" in str(e):
                health_status['message'] = "❌ Could not connect to TickTick API: Connection error"

        return health_status

    def check_connection(self):
        """
        Simple connection check that returns a boolean.

        Returns:
            bool: True if the connection is working, False otherwise
        """
        try:
            self._api.get_projects()
            return True
        except Exception as e:
            print(f"❌ TickTick connection error: {str(e)}")
            return False

    def get_ticktick_api(self):
        return self._api

    def add_task(self, project_id, properties):
        task = None
        try:
            task = self._api.create_task(
                title=properties['content'],
                project_id=project_id,
                content=properties.get('description', ''),
                due_date=properties.get('due_date'),
                priority=self._map_priority(properties.get('priority', 1)),
                tags=properties.get('labels', []),
                list_id=properties.get('section_id')
            )
        except Exception as error:
            print(error)
            raise
        return task

    def _map_priority(self, todoist_priority):
        # Todoist: 1 (highest), 2, 3, 4 (lowest)
        # TickTick: 0 (none), 1 (low), 3 (medium), 5 (high)
        mapping = {1: 5, 2: 3, 3: 1, 4: 0}
        return mapping.get(todoist_priority, 0)

    def get_projects(self):
        projects = None
        try:
            projects = self._api.get_projects()
        except Exception as error:
            print(error)
            raise
        return projects