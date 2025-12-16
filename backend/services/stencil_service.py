from argparse import Action
import requests
import random 
from datetime import date, datetime
from backend.services.notion_service import NotionService
from config import NOTION_API_KEY, NOTION_DBID_STENC
import random 

class StencilService:
    base_url = "https://api.notion.com/v1"
    GOLDEN_RATIO = 1.618033988749895
    percentage_per_day = 0.20
    multiplier = 2
    execution_log = []
    start_date_str = None
    end_date_str = None
    notion_service = None


    def __init__(self):
        """
        Initialize a StencilService instance with headers for API requests.

        Sets up the authorization headers using the NOTION_API_KEY and
        initializes a cache for storing character data.
        """
        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            'Content-Type': 'application/json'
        }
        self._cached_characters = None  # Initialize cache
        self.notion_service = NotionService()

    def translate_stencil_tasks(self, tasks):
        array_tasks = []
        for task in tasks:
            #print(task)
            names = ""
            whos = []
            abilities = []
            for title in task['properties']['name']['title']:
                names += title['plain_text'] + " "
            for character_id in task['properties']['who']['relation']:
                character = self.notion_service.get_character_by_id(character_id['id'])
                whos.append(character)
            for ability_id in task['properties']['abilities']['relation']:
                ability = self.notion_service.get_ability_by_id(ability_id['id'])
                abilities.append(ability)
            array_tasks.append({ 
                "id": task['id']
                ,"name": names
                ,"whos": whos
                ,"status": task['properties']['status']['status']['name']
                ,"coinRwd": task['properties']['coinRwd']['number']
                ,"xpRwd": task['properties']['xpRwd']['number']
                ,"abilities": abilities
                ,"due": task['properties']['due']['date']['start'] if task['properties']['due']['date'] else datetime.now().strftime('%Y-%m-%d')
                ,"assigned": task['properties']['asignee']['people'][0]['id']
                ,"last_edited_time": str(task['last_edited_time']).split('T')[0] if task['last_edited_time'] else datetime.now().strftime('%Y-%m-%d')
                ,"week_range":{ "start": self.start_date_str, "end": self.end_date_str }
                ,"alive_range":{ "start": task['properties']['dateRangeAlive']['formula']['date']['start'].split('T')[0]
                                , "end": task['properties']['dateRangeAlive']['formula']['date']['end'].split('T')[0]}
            })
        return array_tasks


    def get_by_week(self, week_number, year_number):
        """Get stencil activities for a given week."""
        self.start_date_str, self.end_date_str = self.notion_service.start_end_dates(week_number, year_number)
        print(__class__.__name__, self.start_date_str, self.end_date_str, f"w{week_number:02}")   
        # Prepare the query for Notion API
        url = f"{self.base_url}/databases/{NOTION_DBID_STENC}/query"
        data = {
            "filter": {
                "and": [
                    { "property": "due",
                        "date": { "on_or_after": self.start_date_str }
                    },
                    { "property": "due",
                        "date": { "on_or_before": self.end_date_str }
                    }
                ]
            }
        }
        response = requests.post(url, headers=self.headers, json=data)  
        if response.status_code == 200: 
            return self.translate_stencil_tasks(response.json().get("results", []))
        else:
            print("❌❌ get_by_week",__name__,response.status_code, response.text)  
            response.raise_for_status() 
        return None
    
    def evaluate_challenges(self, week_number, year_number):
        challenges = self.get_by_week(week_number, year_number)
        result = None
        if len(challenges) <= 0:
            print("no stencil challenges found for weeek ", week_number)
            result = {"status": "No stencil challenges found"}
        for challenge in challenges:
            result = self.evaluate_challenge(challenge, week_number, year_number)
        return result

    def evaluate_challenge(self, challenge, week_number, year_number):
        #print("✅",challenge)
        characters = []
        abilities = []
        self.execution_log = []
        pos_or_neg = 1 if challenge['status'] == 'Done' or challenge['status'] == 'Archived' else -1
        multiplier = pos_or_neg * self.multiplier
        xp = 0
        # days between dates
        days_alive = abs((datetime.strptime(challenge['alive_range']['end'], '%Y-%m-%d') 
                - datetime.strptime(challenge['alive_range']['start'], '%Y-%m-%d')).days)
        days_off = abs((datetime.strptime(challenge['alive_range']['end'], '%Y-%m-%d') 
                - datetime.strptime(challenge['due'], '%Y-%m-%d')).days)
        self.execution_log.append('[{}] {}'.format(challenge['status'],challenge['name']))
        for who in challenge['whos']:
            if multiplier > 0:
                who['coins'] += multiplier * challenge['coinRwd']
                who['xp'] += multiplier * days_alive
                self.execution_log.append('{} | {} days alive '.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), days_alive))
                xp = multiplier * challenge['xpRwd']
            else:
                xp = multiplier * ( challenge['xpRwd'] * self.percentage_per_day )
                xp += multiplier * days_off
                self.execution_log.append('{} | {} days off due '.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), days_off))
            who['xp'] += xp
            self.execution_log.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " | " 
                                    + who['name'] + (" earned " if multiplier > 0 else " lost ") 
                                    + str(multiplier * challenge['coinRwd']) + " coins and " 
                                    + str(xp) + " xp" )
            who['level'] += 1 if who['xp'] >= who['max_xp'] else 0
            datau = {"properties": { "coins": {"number": who['coins']} 
                                    , "xp": {"number": who['xp']}  
                                    , "level": {"number": who['level']} } }
            characters.append(self.notion_service.update_character(who, datau))

        for ability in challenge['abilities']:
            dlylog_array = []
            if multiplier > 0:
                ability['coins'] += multiplier * challenge['coinRwd']
                ability['xp'] += multiplier * days_alive
                xp = multiplier * challenge['xpRwd']
            else:
                xp = multiplier * ( challenge['xpRwd'] * self.percentage_per_day )
                xp += multiplier * days_off
            ability['xp'] += xp
            self.execution_log.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " | " 
                                    + ability['name'] + (" earned " if multiplier > 0 else " lost ") 
                                    + str(multiplier * challenge['coinRwd']) + " coins and " 
                                    + str(xp) + " xp" )
            daily_checklist = self.notion_service.get_daily_checklist(week_number, year_number)
            #print(daily_checklist)
            for dly_card in daily_checklist:
                if challenge['due'] == dly_card['cuando']:
                    dlylog_array.append({"id":dly_card['id']})
                    self.execution_log.append("📆 linked bcoz due date {}".format(dly_card['cuando']))
                arr1 = self.notion_service.dlychcklst_map[ability['name']]
                arr2 = dly_card['achieved']
                result = any(elem in arr2 for elem in arr1)
                if result is True:
                    dlylog_array.append({"id":dly_card['id']})
                    self.execution_log.append("🗓️ linked bcoz {} @ {}".format(arr1,dly_card['cuando']))
                # print(dly_card['cuando'],arr1, arr2,result)

            if len(dlylog_array) > 0:
                #dlylog_array = list(dict.fromkeys(dlylog_array))
                ability['dlylog'] = dlylog_array

            abilities.append(self.notion_service.persist_ability(ability))
            self.notion_service.add_blocks(ability['id'], "callout", self.notion_service.translate_execution_log(self.execution_log))
        return {"status":challenge['status'],"characters": characters, "abilities": abilities}