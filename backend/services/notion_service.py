import requests
import random 
import json
from datetime import datetime, timedelta
from config import NOTION_API_KEY, NOTION_DBID_CHARS, NOTION_DBID_ADVEN, NOTION_DBID_HABIT, NOTION_DBID_DLYLG, CREATED_LOG, CLOSED_LOG, WON_LOG, LOST_LOG, MISSED_LOG

class NotionService:
    base_url = "https://api.notion.com/v1"
    GOLDEN_RATIO = 1.618033988749895
    max_xp = 500
    max_hp = 100
    max_sanity = 60    
    lines_per_paragraph = 80
    yogmortuum = {"id": "31179ebf-9b11-4247-9af3-318657d81f1d"}

    """
    Initialize a NotionService instance with headers for API requests.

    Sets up the authorization headers using the NOTION_API_KEY and
    initializes a cache for storing character data.
    """
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            'Content-Type': 'application/json'
        }
        self._cached_characters = None  # Initialize cache

    """
    Retrieve all characters from the Notion database and cache the results.

    If the characters are already cached, return the cached data.
    Otherwise, fetch the characters from the Notion database, cache
    the results, and return them.

    Returns:
        list: A list of character data retrieved from the Notion database.
    """
    def get_all_characters(self):
        """Fetch all characters from Notion database, caching the result."""
        if self._cached_characters is None:  # Check if cache is empty
            url = f"{self.base_url}/databases/{NOTION_DBID_CHARS}/query"
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            self._cached_characters = response.json().get("results", [])  # Cache the result
            print("Fetched and cached characters:", len(self._cached_characters))
        else:
            print("Using cached characters:", len(self._cached_characters))
        return self._cached_characters

    def get_character_by_id(self, character_id):
        """Retrieve a character by its ID from the cached characters."""
        characters = self.get_all_characters()  # Ensure we have the latest characters
        for character in characters:
            if character['id'] == character_id:
                pictures = character['properties']['picture']['files']
                random_picture = random.choice(pictures) if pictures else None
                character_level = character['properties']['level']['number']
                max_xp = self.max_xp
                max_hp = self.max_hp
                max_sanity = self.max_sanity
                for i in range(character_level):
                    max_xp *= self.GOLDEN_RATIO
                    max_hp *= self.GOLDEN_RATIO
                    max_sanity *= self.GOLDEN_RATIO
                return { 
                "id": character['id']
                ,"name": character['properties']['name']['title'][-1]['plain_text']
                ,"status": character['properties']['status']['select']['name']
                ,"picture": random_picture['file']['url']
                ,"level": character['properties']['level']['number']
                ,"coins": character['properties']['coins']['number']
                ,"xp": character['properties']['xp']['number']
                ,"max_xp": max_xp
                ,"hp": character['properties']['hp']['number']
                ,"max_hp": max_hp
                ,"sanity": character['properties']['sanity']['number']
                ,"max_sanity": max_sanity
                ,"attack": character['properties']['force']['number']
                ,"defense": character['properties']['defense']['number']
                ,"magic": character['properties']['magic']['number']
                ,"inventory": character['properties']['inventory']['multi_select']
                ,"npc": character['properties']['npc']['checkbox']
                ,"deep_level": character['properties']['deeplevel']['formula']['string']
                ,"alter_ego": character['properties']['alter ego']['relation'][0]['id'] if character['properties']['alter ego']['relation'] else None
                ,"respawn": character['properties']['respawn']['number']
                }
        return None  # Return None if the character is not found

    def update_character(self, character_id, updates):
        """Update character attributes."""
        url = f"{self.base_url}/pages/{character_id}"
        response = requests.patch(url, headers=self.headers, json=updates)
        #print("update_character::",response.status_code, response.text)  
        response.raise_for_status()
        return response.json()

    def persist_adventure(self, adventure, characters):
        #print(self.translate_encounter_log(adventure['encounter_log']))
        self.add_blocks(adventure['id'], 'paragraph', self.translate_encounter_log(adventure['encounter_log']))
        RESULT_LOG = adventure['resultlog'] + CLOSED_LOG + (WON_LOG if adventure['status'] == 'won' else MISSED_LOG if adventure['status'] == 'missed' else LOST_LOG)
        datau = {
            "properties": { "status": {"status": {"name":adventure['status']}},
                            "resultlog": { "rich_text": RESULT_LOG  } }
        }  
        upd_adventure = self.update_character(adventure['id'], datau)
        for character in characters if characters else []:
            character['level'] += 1 if character['xp'] >= character['max_xp'] else 0
            character['hp'] = character['hp'] if character['hp'] < character['max_hp'] else character['max_hp']
            character['sanity'] = character['sanity'] if character['sanity'] < character['max_sanity'] else character['max_sanity']
            pct = character['hp'] / character['max_hp']
            character['status'] = 'dead' if character['hp'] <= 0 else 'dying' if pct <= 0.15 else 'rest' if pct<=0.3 else character['status']
            character['xp'] += 2 if character['hp'] <= 0 else 0
            datau = {"properties": { "level": {"number": character['level']}, 
                                    "hp": {"number": character['hp']}, 
                                    "xp": {"number": character['xp']}, 
                                    "sanity": {"number": character['sanity']}, 
                                    "force": {"number": character['attack']}, 
                                    "defense": {"number": character['defense']}, 
                                    "coins": {"number": character['coins']}, 
                                    "magic": {"number": character['magic']} ,
                                    "status": {"select": {"name":character['status']} }}}
            upd_character = self.update_character(character['id'], datau)
            #print(datau)
        return upd_adventure, upd_character

    def add_blocks(self, parent_id, block_type, childrens):
        """
        Add a block to a Notion page.

        :param token: The Notion integration token.
        :param parent_id: The ID of the parent page where the block will be added.
        :param block_type: The type of block to add (e.g., "paragraph", "heading_1", "to_do").
        :return: The response from the Notion API.
        """

        childrens_to_send = []
        url = f"{self.base_url}/blocks/{parent_id}/children"
        count_child = 0
        for children in childrens:
            count_child += 1
            childrens_to_send.append(children)
            if len(childrens_to_send) == self.lines_per_paragraph or len(childrens) == count_child:
                block_data = {
                    "object": "block",
                    "type": block_type,
                    block_type: {"rich_text": childrens_to_send}
                }
                para_data = {
                    "children": [block_data]
                }
                response = requests.patch(url, headers=self.headers, json=para_data)
                if response.status_code == 200:
                    print("Block added successfully!")
                else:
                    print(f"Failed to add block: {response.status_code} - {response.text}")
                    response.raise_for_status()
                childrens_to_send = []
        
    def translate_encounter_log(self, encounter_log):
        translated_encounter = []
        for encounter in encounter_log:
            translated_encounter.append({'type': 'text','text': {'content': '\n' + str(encounter['time']),'link': None}
                                        ,'annotations': {'bold': False,'italic': True,'strikethrough': False
                                        ,'underline': False, 'code': False, 'color': 'gray_background'}
                                        , 'plain_text': '\n' + str(encounter['time']), 'href': None })
            translated_encounter.append({'type': 'text','text': {'content': ' '+encounter['why']+' ','link': None}
                                        ,'annotations': {'bold': False,'italic': False,'strikethrough': False
                                        ,'underline': False, 'code': False, 'color': 'gray'}
                                        , 'plain_text': ' '+encounter['why']+' ', 'href': None })
            if encounter['type'] != '':
                color = 'green' if encounter['points'] >= 0 else 'red'
                mas_menos = ('+' if encounter['points'] >= 0 else '-') + str(abs(encounter['points'])) + ' ' 
                translated_encounter.append({'type': 'text','text': {'content': mas_menos + encounter['type'],'link': None}
                                            ,'annotations': {'bold': True,'italic': True,'strikethrough': False
                                            ,'underline': False, 'code': False, 'color': color}
                                            , 'plain_text': mas_menos + encounter['type'], 'href': None })
        return translated_encounter

    def filter_by_deep_level(self, deep_level, is_npc=False):
        """Filter characters by deep level and is_npc, returning 4 random characters."""
        characters = self.get_all_characters()
        filtered_characters = [c for c in characters if c['properties']['deeplevel']['formula']['string'] == deep_level and c['properties']['npc']['checkbox'] == is_npc]
        array_characters = []
        for character in filtered_characters:
            pictures = character['properties']['picture']['files']
            random_picture = random.choice(pictures) if pictures else None
            character_level = character['properties']['level']['number']
            max_xp = self.max_xp
            max_hp = self.max_hp
            max_sanity = self.max_sanity
            for i in range(character_level):
                max_xp *= self.GOLDEN_RATIO
                max_hp *= self.GOLDEN_RATIO
                max_sanity *= self.GOLDEN_RATIO
            array_characters.append({ 
                "id": character['id']
                ,"name": character['properties']['name']['title'][-1]['plain_text']
                ,"status": character['properties']['status']['select']['name']
                ,"picture": random_picture['file']['url']
                ,"level": character_level
                ,"coins": character['properties']['coins']['number']
                ,"xp": character['properties']['xp']['number']
                ,"max_xp": max_xp
                ,"hp": character['properties']['hp']['number']
                ,"max_hp": max_hp
                ,"sanity": character['properties']['sanity']['number']
                ,"max_sanity": max_sanity
                ,"attack": character['properties']['force']['number']
                ,"defense": character['properties']['defense']['number']
                ,"magic": character['properties']['magic']['number']
                ,"inventory": character['properties']['inventory']['multi_select']
                ,"npc": character['properties']['npc']['checkbox']
                ,"deep_level": character['properties']['deeplevel']['formula']['string']
                ,"alter_ego": character['properties']['alter ego']['relation'][0]['id'] if character['properties']['alter ego']['relation'] else None
                ,"respawn": character['properties']['respawn']['number']
            })
        return array_characters if is_npc else random.sample(array_characters, min(4, len(array_characters)))
    
    def create_adventure(self, character_id, final_enemies, xp_reward, coin_reward, description):
        today_date = datetime.now()
        end_date = today_date + timedelta(days=2) 
        data = {
            "parent": { "database_id": NOTION_DBID_ADVEN },
            "icon": {
                "emoji": "🏰"
            },
            "properties": {
                "name": {
                    "title": [
                        {"text": {
                            "content": "ADVENTURE | " + str(random.randint(1, 666))  # TODO: generate with groq
                        }}
                    ]
                },
                "due": { 
                    "date": {
                        'start': end_date.strftime('%Y-%m-%d')
                    }
                },
                "xpRwd": { "number": xp_reward },
                "coinRwd": { "number": coin_reward },
                "desc": { "rich_text": [{"text": {"content": description}}] }, 
                "who": { "relation": [{"id": character_id}] },
                "vs": {"relation": final_enemies},
                "resultlog": { "rich_text": CREATED_LOG  },
                "path": {"multi_select": [{"name": "encounter"}]}
            }
        }
        if random.randint(0, 4) == 0: # 20%chance
            data['properties']['path']['multi_select'].append("discovery")
        url = f"{self.base_url}/pages"
        response = requests.post(url, headers=self.headers, json=data)  # Use json instead of data
        if response.status_code == 200:  # Check if the request was successful
            adventure_id = response.json()['id']
            return { "adventure_id": adventure_id }
        else:
            print(response.status_code, response.text)  # Debugging: Print the response
            response.raise_for_status()  # Raise an error for bad responses
            return None  # Return None if the request was not successful

    def get_adventure_by_id(self, adventure_id):
        """Retrieve an adventure by its ID."""
        url = f"{self.base_url}/pages/{adventure_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return self.translate_adventure([response.json()] if response.json() else [])[0]
    
    def start_end_dates(self, week_number):
        # Get the current year
        current_year = datetime.now().year
        
        # Calculate the first day of the year
        first_day_of_year = datetime(current_year, 1, 1)
        
        # Calculate the first Monday of the year
        first_monday = first_day_of_year + timedelta(days=(7 - first_day_of_year.weekday()) % 7)
        
        # Calculate the start date (Monday) of the specified week
        start_date = first_monday + timedelta(weeks=week_number - 1)
        
        # Calculate the end date (Sunday) of the specified week
        end_date = start_date + timedelta(days=6)

        # Format dates to yyyy-mm-dd
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        return start_date_str, end_date_str


    def get_challenges_by_week(self, week_number, name_str):
        """Retrieve challenges for a specific week."""
        start_date_str, end_date_str = self.start_end_dates(week_number)
        print(name_str,start_date_str,end_date_str, "w"+str(week_number))
        # Prepare the query for Notion API
        url = f"{self.base_url}/databases/{NOTION_DBID_ADVEN}/query"
        data = {
            "filter": {
                "and": [
                    {
                        "property": "due",
                        "date": {
                            "on_or_after": start_date_str
                        }
                    },
                    {
                        "property": "name",
                        "rich_text": {
                        "contains": "w"+str(week_number)
                        }
                    },
                    {
                        "property": "name",
                        "rich_text": {
                        "contains": name_str
                        }
                    }
                ]
            }
        }
        response = requests.post(url, headers=self.headers, json=data)  # Use json to send data
        response.raise_for_status()
        return self.translate_adventure(response.json().get("results", []) if response.json().get("results", []) else [])
        
    def get_daily_checklist(self, week_number):
        start_date_str, end_date_str = self.start_end_dates(week_number)
        # Prepare the query for Notion API
        url = f"{self.base_url}/databases/{NOTION_DBID_DLYLG}/query"
        data = {
            "filter": {
                "and": [
                    {
                        "property": "cuando",
                        "date": {
                            "on_or_after": start_date_str
                        }
                    },
                    {
                        "property": "cuando",
                        "date": {
                            "on_or_before": end_date_str
                        }
                    }
                ]
            },
            "sorts":[{"property": "cuando", "direction" : "ascending"}]
        }
        response = requests.post(url, headers=self.headers, json=data)  
        if response.status_code == 200: 
            habits_cards_trn = []
            habits_cards = response.json().get("results", [])
            for habit_daily_card in habits_cards:
                achieved = []
                achieved.append("trade" if habit_daily_card['properties']['📈']['checkbox'] is True else None)
                achieved.append("prsnl" if habit_daily_card['properties']['🫀']['checkbox'] is True else None)
                achieved.append("beer" if habit_daily_card['properties']['🍺']['checkbox'] is True else None)
                achieved.append("read" if habit_daily_card['properties']['📚']['checkbox'] is True else None)
                achieved.append("tech" if habit_daily_card['properties']['💻']['checkbox'] is True else None)
                achieved.append("deew" if habit_daily_card['properties']['🍃']['checkbox'] is True else None)
                achieved.append("shower" if habit_daily_card['properties']['🚿']['checkbox'] is True else None)
                achieved.append("social" if habit_daily_card['properties']['🛗']['checkbox'] is True else None)
                achieved.append("cook" if habit_daily_card['properties']['🍚']['checkbox'] is True else None)
                achieved.append("bed" if habit_daily_card['properties']['🛏️']['checkbox'] is True else None)
                achieved.append("meals" if habit_daily_card['properties']['🥣']['number'] == 3 else None)
                achieved.append("bike" if habit_daily_card['properties']['🚲']['checkbox'] is True else None)
                achieved.append("teeth" if habit_daily_card['properties']['🦷']['checkbox'] is True else None)
                achieved.append("outdoors" if habit_daily_card['properties']['🏜️']['checkbox'] is True else None)
                achieved.append("gym" if habit_daily_card['properties']['💪🏼']['checkbox'] is True else None)
                achieved = [item for item in achieved if item is not None]
                habits_cards_trn.append({
                    "id": habit_daily_card['id']
                    ,"cuando": habit_daily_card['properties']['cuando']['date']['start']
                    ,"trade" : habit_daily_card['properties']['📈']['checkbox']
                    ,"prsnl" : habit_daily_card['properties']['🫀']['checkbox']
                    ,"beer" : habit_daily_card['properties']['🍺']['checkbox']
                    ,"read" : habit_daily_card['properties']['📚']['checkbox']
                    ,"tech" : habit_daily_card['properties']['💻']['checkbox']
                    ,"deew" : habit_daily_card['properties']['🍃']['checkbox']
                    ,"shower" : habit_daily_card['properties']['🚿']['checkbox']
                    ,"social" : habit_daily_card['properties']['🛗']['checkbox']
                    ,"cook" : habit_daily_card['properties']['🍚']['checkbox']
                    ,"bed" : habit_daily_card['properties']['🛏️']['checkbox']
                    ,"meals" : habit_daily_card['properties']['🥣']['number']
                    ,"bike" : habit_daily_card['properties']['🚲']['checkbox']
                    ,"teeth" : habit_daily_card['properties']['🦷']['checkbox']
                    ,"outdoors" : habit_daily_card['properties']['🏜️']['checkbox']
                    ,"gym" : habit_daily_card['properties']['💪🏼']['checkbox']
                    ,"achieved": achieved
                })
            return habits_cards_trn
        else:
            print("<x>|",response.status_code, response.text)  
            response.raise_for_status()  
            return []
            
    def translate_adventure(self, adventures):
        array_adventures = []
        #print(adventures)
        for adventure in adventures:
            array_adventures.append({ 
                "id": adventure['id']
                ,"name": adventure['properties']['name']['title'][-1]['plain_text']
                ,"who": adventure['properties']['who']['relation'][0]['id'] if adventure['properties']['who']['relation'] else None
                ,"status": adventure['properties']['status']['status']['name']
                ,"desc": adventure['properties']['desc']['rich_text'][-1]['plain_text'] if adventure['properties']['desc']['rich_text'] else None
                ,"coinRwd": adventure['properties']['coinRwd']['number']
                ,"xpRwd": adventure['properties']['xpRwd']['number']
                ,"timesXweek": adventure['properties']['timesXweek']['rollup']['number']
                ,"vs": adventure['properties']['vs']['relation'] if adventure['properties']['vs']['relation'] else None
                ,"habits": adventure['properties']['habits']['relation'] if adventure['properties']['habits']['relation'] else None
                ,"due": adventure['properties']['due']['date']['start']
                ,"assigned": adventure['properties']['assigned']['people'][0]['id']
                ,"resultlog": adventure['properties']['resultlog']['rich_text']
                ,"path": [path['name'] for path in adventure['properties']['path']['multi_select']] if adventure['properties']['path']['multi_select'] else None
                ,"last_edited_time": str(adventure['last_edited_time']).split('T')[0] if adventure['last_edited_time'] else None
                ,"url": adventure['id']
            })
        return array_adventures
    

    def create_challenge(self, emoji, week_number, how_many_times, character_id, xp_reward, coin_reward, habit):
        today_date = datetime.now()
        end_date = today_date + timedelta(days=6)
        data = {
            "parent": { "database_id": NOTION_DBID_ADVEN },
            "icon": {
                "emoji": emoji
            },
            "properties": {
                "name": {
                    "title": [
                        {"text": {
                            "content": "CHALLENGE | w" + str(week_number) 
                        }}
                    ]
                },
                "due": { 
                    "date": {
                        'start': end_date.strftime('%Y-%m-%d')
                    }
                },
                "xpRwd": { "number": xp_reward },
                "coinRwd": { "number": coin_reward },
                "desc": { "rich_text": [{"text": {"content": 'Do it for {} consecutive days'.format(how_many_times)}}] }, 
                "who": { "relation": [{"id": character_id}] },
                "vs": { "relation": [{"id": character_id}] },
                "path": {"multi_select": [ {"name": '{}timesXw'.format(how_many_times)}]},
                #"assigned": {"people": [self.yogmortuum]},
                "status": {"status": {"name":"created"}},
                "habits": { "relation": [{"id": habit}] },
                "resultlog": { "rich_text": CREATED_LOG  }
            }
        }

        url = f"{self.base_url}/pages"
        response = requests.post(url, headers=self.headers, json=data) 
        if response.status_code == 200: 
            adventure_id = response.json()['id']
            return  self.translate_adventure([response.json()] if response.json() else [])[0]
        else:
            print("-->",response.status_code, response.text)  # Debugging: Print the response
            response.raise_for_status()  # Raise an error for bad responses
            return None  # Return None if the request was not successful    
        

    def get_all_habits(self):
        url = f"{self.base_url}/databases/{NOTION_DBID_HABIT}/query"
        response = requests.post(url, headers=self.headers)
        if response.status_code != 200:  
            print(response.status_code, response.text)  # Debugging: Print the response
            response.raise_for_status()  # Raise an error for bad responses
            return []  # Return None if the request was not successful

        max_xp = self.max_xp

        habits = response.json().get("results", [])  
        translated_habits = []
        for habit in habits:
            habit_level = int(habit['properties']['level']['number'])
            for i in range(habit_level):
                max_xp *= self.GOLDEN_RATIO
            translated_habits.append({
                "id": habit['id']
                ,"emoji": habit['icon']['emoji']
                ,"name": habit['properties']['name']['title'][-1]['plain_text']
                ,"level": habit_level
                ,"xp": habit['properties']['xp']['number']
                ,"max_xp": max_xp
                ,"coins": habit['properties']['coins']['number']
                ,"timesXweek": habit['properties']['timesXweek']['number']
                ,"who": habit['properties']['who']['relation'][0]['id'] if habit['properties']['who']['relation'] else None
            })
        return translated_habits
    
    def get_habits_by_id_or_name(self, habit_id, habit_name):
        habits = self.get_all_habits()
        for habit in habits:
            if habit['id'] == habit_id or habit['name'] == habit_name:
                return habit
        return None

    def persist_habit(self, habit):
        print(habit)

        habit['level'] += 1 if habit['xp'] >= habit['max_xp'] else 0
        datau = {"properties": { "level": {"number": habit['level']}, 
                                    "xp": {"number": habit['xp']}, 
                                    "coins": {"number": habit['coins']}}}
        upd_habit = self.update_character(habit['id'], datau)   
        return upd_habit    