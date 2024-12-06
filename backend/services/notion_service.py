import requests
import random 
import json
from datetime import datetime, timedelta
from config import NOTION_API_KEY, NOTION_DBID_CHARS, NOTION_DBID_ADVEN, NOTION_DBID_HABIT, CREATED_LOG

class NotionService:
    base_url = "https://api.notion.com/v1"
    GOLDEN_RATIO = 1.618033988749895
    max_xp = 500
    max_hp = 100
    max_sanity = 60    
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
        response.raise_for_status()
        return response.json()

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
        return response.json()
    
    def get_challenges_by_week(self, week_number):
        """Retrieve challenges for a specific week."""
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
                        "contains": "CHALLENGE"
                        }
                    }
                ]
            }
        }
        print("challenge",start_date_str,end_date_str, "w"+str(week_number))
        response = requests.post(url, headers=self.headers, json=data)  # Use json to send data
        response.raise_for_status()
        return self.translate_adventure(response.json().get("results", []) if response.json().get("results", []) else [])
        
        
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

        habits = response.json().get("results", [])  
        translated_habits = []
        for habit in habits:
            translated_habits.append({
                "id": habit['id']
                ,"emoji": habit['icon']['emoji']
                ,"name": habit['properties']['name']['title'][-1]['plain_text']
                ,"level": habit['properties']['level']['number']
                ,"xp": habit['properties']['xp']['number']
                ,"coins": habit['properties']['coins']['number']
                ,"timesXweek": habit['properties']['timesXweek']['number']
                ,"who": habit['properties']['who']['relation'][0]['id'] if habit['properties']['who']['relation'] else None
            })
        return translated_habits
