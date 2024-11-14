import requests
import random 
from config import NOTION_API_KEY, NOTION_DBID_CHARS

class NotionService:
    base_url = "https://api.notion.com/v1"
    GOLDEN_RATIO = 1.618033988749895

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2022-06-28"
        }

    def get_all_characters(self):
        """Fetch all characters from Notion database."""
        url = f"{self.base_url}/databases/{NOTION_DBID_CHARS}/query"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get("results", [])

    def update_character(self, character_id, updates):
        """Update character attributes."""
        url = f"{self.base_url}/pages/{character_id}"
        response = requests.patch(url, headers=self.headers, json=updates)
        response.raise_for_status()
        return response.json()

    def filter_by_deep_level(self, deep_level, is_npc=False):
        """Filter characters by deep level and is_npc, returning 4 random characters."""
        characters = self.get_all_characters()
        print("Got all characters:", len(characters))
        filtered_characters = [c for c in characters if c['properties']['deeplevel']['formula']['string'] == deep_level and c['properties']['npc']['checkbox'] == is_npc]
        array_characters = []
        for character in filtered_characters:
            pictures = character['properties']['picture']['files']
            random_picture = random.choice(pictures) if pictures else None
            character_level = character['properties']['level']['number']
            max_xp = 500
            max_hp = 100
            max_sanity = 60
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