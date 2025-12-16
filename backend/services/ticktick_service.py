from ticktick.oauth2 import OAuth2        
from ticktick.api import TickTickClient   
from config import TICKTICK_PASS, TICKTICK_USER, TICKTICK_URI, TICKTICK_CLIENT_ID, TICKTICK_CLIENT_SECRET
class TickTickService:
    _instance = None  # Class variable to hold the single instance
    ticktickClient = None

    def __new__(cls, *args, **kwargs):
        """Override __new__ to implement Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(TickTickService, cls).__new__(cls)
        return cls._instance

    def __init__(self):

        if not hasattr(self, 'initialized'):  # Check if already initialized

            auth_client = OAuth2(client_id=TICKTICK_CLIENT_ID,
                                client_secret=TICKTICK_CLIENT_SECRET,
                                redirect_uri=TICKTICK_URI)

            client = TickTickClient(TICKTICK_USER, TICKTICK_PASS, auth_client)
            #self.ticktickClient = client
            self.initialized = True  # Mark as initialized



    def _map_priority(self, todoist_priority):
        # Todoist: 1 (highest), 2, 3, 4 (lowest)
        # TickTick: 0 (none), 1 (low), 3 (medium), 5 (high)
        mapping = {1: 5, 2: 3, 3: 1, 4: 0}
        return mapping.get(todoist_priority, 0)

