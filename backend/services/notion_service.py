import requests
import random 
from datetime import datetime, timedelta
from config import NOTION_API_KEY, NOTION_DBID_CHARS, NOTION_DBID_ADVEN

class NotionService:
    base_url = "https://api.notion.com/v1"
    GOLDEN_RATIO = 1.618033988749895
    max_xp = 500
    max_hp = 100
    max_sanity = 60    

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            'Content-Type': 'application/json'
        }
        self._cached_characters = None  # Initialize cache

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
    
    def create_adventure(self, character_id, god_support, final_enemies, xp_reward, coin_reward, description):
        today_date = datetime.now()
        end_date = today_date + timedelta(days=2) 

        """Create a new adventure based on specified parameters."""
        data = {
            "parent": { "database_id": NOTION_DBID_ADVEN },
            "icon": {
                "emoji": "🏰"
            },
            "properties": {
                "name": {
                    "title": [
                        {"text": {
                            "content": "ADVENTURE|" + str(random.randint(1, 666))  # TODO: generate with groq
                        }}
                    ]
                },
                "due": { 
                    "date": {
                        'start': today_date.strftime('%Y-%m-%d'),  
                        'end': end_date.strftime('%Y-%m-%d'), 
                        'time_zone': None
                    }
                },
                "xpRwd": { "number": xp_reward },
                "coinRwd": { "number": coin_reward },
                "desc": { "rich_text": [{"text": {"content": description}}] }, 
                "who": { "relation": [{"id": character_id}] },
                "vs": {"relation": final_enemies},
                "resultlog": { "rich_text": [{"text": {"content": god_support}}] },
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

