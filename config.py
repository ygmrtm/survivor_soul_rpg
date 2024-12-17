import os
from datetime import datetime
today_date = datetime.now()


# Notion API credentials
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DBID_CHARS = os.getenv('NOTION_DBID_CHARS')
NOTION_DBID_ADVEN = os.getenv('NOTION_DBID_ADVEN')
NOTION_DBID_HABIT = os.getenv('NOTION_DBID_HABIT')
NOTION_DBID_EPICS = os.getenv('NOTION_DBID_EPICS')
NOTION_DBID_DLYLG = os.getenv('NOTION_DBID_DLYLG')

# Todoist API credentials
TODOIST_API_KEY = os.getenv('TODOIST_API_KEY')

# Flask app settings
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == 'development'
PORT = int(os.getenv('PORT', 5000))

# Other configurations can go here
CREATED_LOG = [{'type': 'text','text': {'content': 'created on: ','link': None},'annotations': {'bold': True,'italic': False,'strikethrough': False,'underline': False, 'code': False, 'color': 'blue' }, 'plain_text': 'created on: ','href': None}
            ,{'type': 'text','text': {'content': ' ','link': None},'annotations': {'bold': True,'italic': False,'strikethrough': False,'underline': False, 'code': False, 'color': 'blue' }, 'plain_text': ' ','href': None}
            ,{'type': 'mention','mention': {'type': 'date','date': {'start': today_date.strftime('%Y-%m-%d'),'end': None,'time_zone': None}},'annotations': {'bold': False,'italic': True, 'strikethrough': False, 'underline': False,'code': False,'color': 'blue'},'plain_text': today_date.strftime('%Y-%m-%d'), 'href': None}
            ,{'type': 'text','text': {'content': '\n','link': None},'annotations': {'bold': False,'italic': True,'strikethrough': False,'underline': False, 'code': False, 'color': 'default'}, 'plain_text': '\n', 'href': None }
            ]

MISSED_LOG = [{'type': 'text','text': {'content': 'missed by: ','link': None},'annotations': {'bold': True,'italic': False,'strikethrough': False,'underline': False, 'code': False, 'color': 'gray' }, 'plain_text': 'missed on: ','href': None}
            ,{'type': 'text','text': {'content': ' ','link': None},'annotations': {'bold': True,'italic': False,'strikethrough': False,'underline': False, 'code': False, 'color': 'gray' }, 'plain_text': ' ','href': None}
            ,{'type': 'mention','mention': {'type': 'date','date': {'start': today_date.strftime('%Y-%m-%d'),'end': None,'time_zone': None}},'annotations': {'bold': False,'italic': True, 'strikethrough': False, 'underline': False,'code': False,'color': 'gray'},'plain_text': today_date.strftime('%Y-%m-%d'), 'href': None}
            ,{'type': 'text','text': {'content': '\n','link': None},'annotations': {'bold': False,'italic': True,'strikethrough': False,'underline': False, 'code': False, 'color': 'default'}, 'plain_text': '\n', 'href': None }
            ]

CLOSED_LOG = [{'type': 'text','text': {'content': 'closed|done: ','link': None},'annotations': {'bold': True,'italic': False,'strikethrough': False,'underline': False, 'code': False, 'color': 'green' }, 'plain_text': 'closed|done: ','href': None}
            ,{'type': 'text','text': {'content': ' ','link': None},'annotations': {'bold': True,'italic': False,'strikethrough': False,'underline': False, 'code': False, 'color': 'green' }, 'plain_text': ' ','href': None}
            ,{'type': 'mention','mention': {'type': 'date','date': {'start': today_date.strftime('%Y-%m-%d'),'end': None,'time_zone': None}},'annotations': {'bold': False,'italic': True, 'strikethrough': False, 'underline': False,'code': False,'color': 'green'},'plain_text': today_date.strftime('%Y-%m-%d'), 'href': None}
            ,{'type': 'text','text': {'content': '\n','link': None},'annotations': {'bold': False,'italic': True,'strikethrough': False,'underline': False, 'code': False, 'color': 'default'}, 'plain_text': '\n', 'href': None }
            ]

WON_LOG = [{'type': 'text','text': {'content': '👍🏼 W O N ‼️‼️','link': None},'annotations': {'bold': True,'italic': False,'strikethrough': False,'underline': False, 'code': False, 'color': 'green_background' }, 'plain_text': '👍🏼 W O N ‼️‼️','href': None}
            ,{'type': 'text','text': {'content': '\n','link': None},'annotations': {'bold': False,'italic': True,'strikethrough': False,'underline': False, 'code': False, 'color': 'default'}, 'plain_text': '\n', 'href': None }
            ]

LOST_LOG = [{'type': 'text','text': {'content': '👎🏼 L O S E ‼️‼️','link': None},'annotations': {'bold': True,'italic': False,'strikethrough': False,'underline': False, 'code': False, 'color': 'red_background' }, 'plain_text': '👎🏼 L O S E ‼️‼️','href': None}
            ,{'type': 'text','text': {'content': '\n','link': None},'annotations': {'bold': False,'italic': True,'strikethrough': False,'underline': False, 'code': False, 'color': 'default'}, 'plain_text': '\n', 'href': None }
            ]