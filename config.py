import os

# Notion API credentials
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DBID_CHARS = os.getenv("NOTION_DBID_CHARS")
NOTION_DBID_ADVEN = os.getenv("NOTION_DBID_ADVEN")
NOTION_DBID_HABIT = os.getenv("NOTION_DBID_HABIT")
NOTION_DBID_EPICS = os.getenv("NOTION_DBID_EPICS")

# Todoist API credentials
TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")

# Flask app settings
FLASK_ENV = os.getenv("FLASK_ENV", "development")
DEBUG = FLASK_ENV == "development"
PORT = int(os.getenv("PORT", 5000))

# Other configurations can go here
