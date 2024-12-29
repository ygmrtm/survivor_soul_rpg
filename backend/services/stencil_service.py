from datetime import date, datetime
from backend.services import notion_service
from backend.services.notion_service import NotionService
import random 
import time

class StencilService:
    GOLDEN_RATIO = 1.618033988749895
    encounter_log = []

    def get_by_week(self, week_number, notion_service=None):
        """Get Stencil activities for a given week."""
        notion_service = NotionService() if not notion_service else notion_service