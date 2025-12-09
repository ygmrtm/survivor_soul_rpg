from operator import is_not
import requests
import random 
from flask import jsonify
from backend.services.redis_service import RedisService
from datetime import datetime, timedelta
from config import NOTION_API_KEY, NOTION_DBID_CHARS, NOTION_DBID_ADVEN,NOTION_DBID_DLYLG, CREATED_LOG, CLOSED_LOG, WON_LOG, LOST_LOG, MISSED_LOG
from config import NOTION_DBID_HABIT, NOTION_DBID_ABILI


class NotionService:
    base_url = "https://api.notion.com/v1"
    GOLDEN_RATIO = 1.618033988749895
    max_xp = 500
    max_hp = 100
    max_sanity = 60    
    max_prop_limit = 15
    lines_per_paragraph = 90
    expiry_hours = 8
    expiry_minutes = 15 / 60
    tour_days_vigencia = 7
    yogmortuum = {"id": "31179ebf-9b11-4247-9af3-318657d81f1d"}

    _instance = None

    def __new__(cls):
        """Override __new__ to implement Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(NotionService, cls).__new__(cls)
        return cls._instance    

    def __init__(self):
        """
        Initialize a NotionService instance with headers for API requests.

        Sets up the authorization headers using the NOTION_API_KEY and
        initializes a cache for storing character data.
        """
        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            'Content-Type': 'application/json'
        }
        self.redis_service = RedisService()
        # print(self.healthcheck())

    def healthcheck(self):
        """
        Check the health status of the Notion service.
        
        Returns:
            dict: A dictionary containing the health status information
                {
                    'status': str ('healthy' or 'unhealthy'),
                    'message': str (status message or error details),
                    'api_connected': bool (True if API is accessible)
                }
        """
        health_status = {
            'status': 'unhealthy',
            'message': '',
            'api_connected': False
        }

        try:
            # Test API Connection by fetching the list of databases
            response = requests.get(f"{self.base_url}/databases/{NOTION_DBID_HABIT}", headers=self.headers)
            response.raise_for_status()  # Raise an error for bad responses
            # If we can fetch databases, the API is working
            health_status['status'] = 'healthy'
            health_status['api_connected'] = True
            health_status['message'] = '✅ Notion service is functioning normally'
        except requests.exceptions.HTTPError as http_err:
            health_status['message'] = f"❌ HTTP error occurred: {str(http_err)}"
            if response.status_code == 401:
                health_status['message'] = "❌ Authentication failed: Invalid API token"
            elif response.status_code == 404:
                health_status['message'] = "❌ Notion API endpoint not found"
        except Exception as e:
            health_status['message'] = f"❌ Notion service error: {str(e)}"

        return health_status
    
    def get_all_raw_characters(self):
        # Try to get from cache first
        cache_key = self.redis_service.get_cache_key('characters', 'all')
        cached_characters = self.redis_service.get(cache_key)
        if cached_characters is not None:
            print("Using ALL cached characters:", len(cached_characters))
            return cached_characters
        # If not in cache, fetch from Notion
        url = f"{self.base_url}/databases/{NOTION_DBID_CHARS}/query"
        all_characters = []
        has_more = True
        start_cursor = None
        while has_more:
            payload = {}
            if start_cursor:
                payload['start_cursor'] = start_cursor
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            all_characters.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
        # Cache the results
        self.redis_service.set_with_expiry(cache_key, all_characters, expiry_hours=self.expiry_hours)
        print("Fetched and cached ALL characters:", len(all_characters))
        return all_characters

    def count_dead_people(self, deep_level):
        """Count the number of dead people in the database."""
        url = f"{self.base_url}/databases/{NOTION_DBID_CHARS}/query"
        headcount = 0
        try:
            self.redis_service.get(self.redis_service.get_cache_key('loaded_characters_level',f'{deep_level}nonpc'))
            characters = self.get_characters_by_deep_level(deep_level, is_npc=False)
            characters = self.get_characters_by_deep_level(deep_level, is_npc=True)
            dead_people = self.redis_service.query_characters('status', 'dead')
            by_level_dp = [c for c in dead_people if c['deep_level'] == deep_level]
            headcount = len(by_level_dp)
            if headcount <= 0:
                data_filter = {
                    "filter": {
                        "and": [
                            {"property": "deeplevel", "formula": {"string": {"equals": deep_level}}},
                            {"property": "status", "select": {"equals": 'dead'}},
                        ]
                    }
                }
                has_more = True
                start_cursor = None

                while has_more:
                    if start_cursor:
                        data_filter['start_cursor'] = start_cursor
                    response = requests.post(url, headers=self.headers, json=data_filter)
                    response.raise_for_status()  # Raise an error for bad responses
                    data = response.json()
                    # Extend the characters list with the results from this page
                    headcount += len(data.get('results', []))
                    # Check if there are more pages
                    has_more = data.get("has_more", False)
                    start_cursor = data.get("next_cursor")  
                print(f"☠️ counted {headcount} from source")
            self.redis_service.set_with_expiry(self.redis_service.get_cache_key('loaded_characters_level:countdeadpeople',deep_level)
                                        , headcount, self.expiry_hours)
        except Exception as e:
            print(f"Failed to count dead people: {e}")
            response.raise_for_status()  # Raise an error for bad responses
        return headcount

    def count_people_pills(self, deep_level):
        """Count the number of people with pills in the database."""
        url = f"{self.base_url}/databases/{NOTION_DBID_CHARS}/query"
        headcount = 0
        try:
            characters = self.redis_service.get(self.redis_service.get_cache_key('loaded_characters_level:pillcompleterray',f"{deep_level}"))
            if not characters:
                characters = []
                data_filter = {
                    "filter": {
                        "and": [
                            {"property": "deeplevel", "formula": {"string": {"equals": deep_level}}},
                            {"property": "status", "select": {"does_not_equal": 'alive'}},
                            { "or" : [{"property": "inventory", "multi_select": {"contains": "blue.pill"}},
                                {"property": "inventory", "multi_select": {"contains": "red.pill"}},
                                {"property": "inventory", "multi_select": {"contains": "yellow.pill"}},
                                {"property": "inventory", "multi_select": {"contains": "green.pill"}},
                                {"property": "inventory", "multi_select": {"contains": "orange.pill"}},
                                {"property": "inventory", "multi_select": {"contains": "purple.pill"}},
                                {"property": "inventory", "multi_select": {"contains": "gray.pill"}},
                                {"property": "inventory", "multi_select": {"contains": "brown.pill"}},
                                ]},
                        ]
                    }
                }
                has_more = True
                start_cursor = None
                while has_more:
                    if start_cursor:
                        data_filter['start_cursor'] = start_cursor
                    response = requests.post(url, headers=self.headers, json=data_filter)
                    response.raise_for_status()  # Raise an error for bad responses
                    data = response.json()
                    # Extend the characters list with the results from this page
                    characters.extend(self.translate_characters(data.get('results', [])))
                    # Check if there are more pages
                    has_more = data.get("has_more", False)
                    start_cursor = data.get("next_cursor")  
                    print(f"Fetched {len(data.get('results', []))} characters, total so far: {len(characters)}")
                for character in characters:
                    cache_key = self.redis_service.get_cache_key('characters', character['id'])
                    if not self.redis_service.exists(cache_key):
                        self.redis_service.set_with_expiry(cache_key, character, self.expiry_hours)
            self.redis_service.set_with_expiry(self.redis_service.get_cache_key('loaded_characters_level:pillcompleterray',f"{deep_level}")
                                            , characters, self.expiry_minutes)
            headcount = len(characters)
            print(f"💊 counted {headcount}")
            self.redis_service.set_with_expiry(self.redis_service.get_cache_key('loaded_characters_level:pillcompleterray:headcount',deep_level)
                                        , headcount, self.expiry_minutes)
        except Exception as e:
            print(f"Failed to count pill people: {e}")
            response.raise_for_status()  # Raise an error for bad responses
        return headcount
    
    def get_character_by_id(self, character_id):
        """Retrieve a character by its ID from the cached characters."""
        # print("👁️‍🗨️ ",character_id)
        character_id_replaced = character_id.replace('-','')
        character = None
        try:
            cache_key = self.redis_service.get_cache_key('characters', character_id_replaced)
            character = self.redis_service.get(cache_key)
            if character is None:
                print(f"👁️‍🗨️ not in cache [{character_id}], going to the source")
                url = f"{self.base_url}/pages/{character_id}"
                response = requests.get(url, headers=self.headers)
                #print(":::",response.json())
                character = self.translate_characters([response.json()] if response.json() else [])[0]
                self.redis_service.set_with_expiry(cache_key, character, expiry_hours=self.expiry_hours)
        except Exception as e:
            print("Failed to fetch character:", e)
            response.raise_for_status()  # Raise an error for bad responses
        return character
    
    def get_characters_by_property(self, property, value):
        try:
            return self.redis_service.query_characters(property, value)                
        except Exception as e:
            print(f"Failed to fetch characters by properties {property} = {value}: {e}")
            raise

    def get_characters_by_deep_level(self, deep_level, is_npc=False):
        """Filter characters by deep level and is_npc, returning all matching characters."""
        url = f"{self.base_url}/databases/{NOTION_DBID_CHARS}/query"
        characters = []
        try:
            npc = '' if is_npc is True else 'no'
            are_cached_chars = self.redis_service.exists(self.redis_service.get_cache_key('loaded_characters_level' 
                                                                                , f"{deep_level}{npc}npc"))
            if are_cached_chars:
                characters = self.redis_service.get(self.redis_service.get_cache_key('loaded_characters_level:completerray',f"{deep_level}"))
                if not characters:
                    characters = []
                    print(f"Using cached characters for deep level {deep_level}")
                    characters_by_level = self.redis_service.query_characters('deep_level', deep_level)
                    # filter characters based on is_npc
                    for character in characters_by_level:
                        if character['npc'] == is_npc:
                            characters.append(character)
                #else:
                #    print(f"Using complete cached array for deep level {deep_level}")
            else:    
                data_filter = {
                    "filter": {
                        "and": [
                            {"property": "deeplevel", "formula": {"string": {"equals": deep_level}}},
                            {"property": "npc", "checkbox": {"equals": is_npc}}
                        ]
                    }
                }
                has_more = True
                start_cursor = None
                while has_more:
                    if start_cursor:
                        data_filter['start_cursor'] = start_cursor
                    response = requests.post(url, headers=self.headers, json=data_filter)
                    response.raise_for_status()  # Raise an error for bad responses
                    data = response.json()
                    # Extend the characters list with the results from this page
                    characters.extend(self.translate_characters(data.get('results', [])))
                    # Check if there are more pages
                    has_more = data.get("has_more", False)
                    start_cursor = data.get("next_cursor")  
                    print(f"Fetched {len(data.get('results', []))} {deep_level} characters, total so far: {len(characters)}")
                # Cache the characters if needed
                self.redis_service.set_with_expiry(self.redis_service.get_cache_key('loaded_characters_level', f"{deep_level}{npc}npc")
                                                , data_filter, self.expiry_hours)
                for character in characters:
                    cache_key = self.redis_service.get_cache_key('characters', character['id'])
                    if not self.redis_service.exists(cache_key):
                        self.redis_service.set_with_expiry(cache_key, character, self.expiry_hours)
            self.redis_service.set_with_expiry(self.redis_service.get_cache_key('loaded_characters_level:completerray',f"{deep_level}")
                                            , characters, self.expiry_hours)
        except Exception as e:
            print(f"Failed to fetch characters by deep level {deep_level}: {e}")
            response.raise_for_status()  # Raise an error for bad responses
        return characters if is_npc else random.sample(characters, min(4, len(characters)))

    def apply_all_pills(self, deep_level, pill_color):
        by_pill_color = []
        response_json = {'message': ''}
        try:
            cached_chars_count = self.redis_service.exists(self.redis_service.get_cache_key('loaded_characters_level:pillcompleterray:headcount' 
                                                                                , f"{deep_level}"))
            if cached_chars_count > 0:
                characters = self.redis_service.get(self.redis_service.get_cache_key('loaded_characters_level:pillcompleterray',f"{deep_level}"))                
                for c in characters:
                    inventory = c['inventory']
                    for i in inventory:
                        if f'{pill_color}.pill' == i['name']:
                            by_pill_color.append(c)
                if len(by_pill_color) > 0:
                    #print(f"Using complete cached array for deep level {deep_level} | {len(by_pill_color)} characters")
                    for character in by_pill_color:
                        cache_key = self.redis_service.get_cache_key('loaded_characters_level:pillcompleterray:characterpillprocessed', character['id'])
                        character = character if not self.redis_service.exists(cache_key) else self.redis_service.get(cache_key)
                        results = self.apply_all_pills_by_character(character, pill_color)
                        response_json[pill_color] = results
                        response_json['message'] += f' | SUCCESS: {pill_color} have been applied : ' + character['name']
                        self.redis_service.set_with_expiry(cache_key, character, self.expiry_minutes)
                        self.redis_service.set_with_expiry(self.redis_service.get_cache_key('loaded_characters_level:pillcompleterray:headcount' 
                                                                                , f"{deep_level}")
                                                                                , cached_chars_count-1
                                                                                , self.expiry_minutes)


                else:
                    response_json['message'] = f'ERROR: No Characters (with {pill_color}💊s) has been found'
            else:
                response_json['message'] = 'ERROR: No full array cached | Characters (with 💊s) array mssing'
        except Exception as e:
            print(f"Failed to fetch characters by deep level {deep_level} and pill collor {pill_color}: {e}")
            response_json['message'] = f"Failed to fetch characters by deep level {deep_level} and pill collor {pill_color}: {e}"
        return response_json 

    def apply_all_pills_by_character(self, character, pill_color):
        #print(pill_color, character['name'])
        if pill_color == "yellow":
            character['sanity'] = character['max_sanity']
        elif pill_color == "blue":
            max_prop_limit = self.max_prop_limit
            character_level = character['level']
            for i in range(character_level):
                max_prop_limit *= self.GOLDEN_RATIO            
            print(f'Max property Limit {max_prop_limit} for Level {character_level}')
            character['defense'] = max_prop_limit
            character['attack'] = max_prop_limit
            character['magic'] = max_prop_limit
        elif pill_color == "green" or pill_color == "red":
            character['hp'] = character['max_hp']
            character['status'] = 'alive'
            character['respawn'] += 1
            if pill_color == "green":
                character['level'] += 1
        elif pill_color == "red":
            character['hp'] = character['max_hp']
            character['status'] = 'alive'
            character['respawn'] += 1
        elif pill_color == "orange":
            #TODO: implement orange pill
            print("🔔 Still under implementation", pill_color)
        elif pill_color == "purple":
            #TODO: implement purple pill
            print("🔔 Still under implementation", pill_color)
        elif pill_color == "gray":
            #TODO: implement gray pill
            print("🔔 Still under implementation", pill_color)
        elif pill_color == "brown":
            #TODO: implement brown pill
            print("🔔 Still under implementation", pill_color)
        for item in character['inventory']:
            if item['name'] == pill_color + '.pill':
                character['inventory'].remove(item)
                break
        datau = {"properties": { "level": {"number": character['level']}, 
                                "hp": {"number": round(character['hp'])}, 
                                "xp": {"number": round(character['xp'])}, 
                                "respawn": {"number": character['respawn']}, 
                                "sanity": {"number": round(character['sanity'])}, 
                                "force": {"number": round(character['attack'])}, 
                                "defense": {"number": round(character['defense'])}, 
                                "coins": {"number": round(character['coins'])}, 
                                "magic": {"number": round(character['magic'])} ,
                                "status": {"select": {"name":character['status']} },
                                "inventory": { "multi_select": character['inventory']}
                                }}
        #print(datau)
        upd_character = self.update_character(character, datau)
        return {'notion_character' : upd_character, "rpg_character": character}

    def translate_characters(self, characters=[]):
        try:
            return_characters = []
            for character in characters:
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
                description = f"{character['properties']['name']['title'][-1]['plain_text']} | L{character['properties']['level']['number']} | X{character['properties']['xp']['number']} | 🫀{character['properties']['hp']['number']} | 🧠{character['properties']['sanity']['number']}"
                return_characters.append({ 
                "id": character['id'].replace('-','')
                ,"name": character['properties']['name']['title'][-1]['plain_text']
                ,"status": character['properties']['status']['select']['name']
                ,"picture": random_picture['file']['url']
                ,"level": character['properties']['level']['number']
                ,"coins": character['properties']['coins']['number']
                ,"xp": character['properties']['xp']['number']
                ,"max_xp": round(max_xp)
                ,"hp": character['properties']['hp']['number']
                ,"max_hp": round(max_hp)
                ,"sanity": character['properties']['sanity']['number']
                ,"max_sanity": round(max_sanity)
                ,"attack": character['properties']['force']['number']
                ,"defense": character['properties']['defense']['number']
                ,"magic": character['properties']['magic']['number']
                ,"inventory": character['properties']['inventory']['multi_select']
                ,"npc": character['properties']['npc']['checkbox']
                ,"deep_level": character['properties']['deeplevel']['formula']['string']
                ,"alter_ego": character['properties']['alter ego']['relation'][0]['id'].replace('-','') if character['properties']['alter ego']['relation'] else None
                ,"alter_subego": character['properties']['alter subego']['relation'] if character['properties']['alter ego'] else None
                ,"respawn": character['properties']['respawn']['number'] if character['properties']['respawn']['number'] else 0
                ,"pending_reborn": character['properties']['pendingToReborn']['formula']['string']
                ,"hours_recovered": character['properties']['hours_recovered']['formula']['number']
                ,"description": description
                })
            return return_characters
        except Exception as e:
            print("😓 Damn it i can't translate characters:", e)
            raise
    
    def update_character(self, character, updates):
        """Update character attributes."""
        character_id = character['id']
        url = f"{self.base_url}/pages/{character_id}"
        response = requests.patch(url, headers=self.headers, json=updates)
        if response.status_code == 200:  # Check if the request was successful
            self.redis_service.set_with_expiry(self.redis_service.get_cache_key('characters',character_id), character, self.expiry_hours)
            self.redis_service.delete(self.redis_service.get_cache_key('loaded_characters_level:completerray',character['deep_level']))
            self.redis_service.delete(self.redis_service.get_cache_key('loaded_characters_level:countdeadpeople',character['deep_level']))
            return response.json()
        else:
            print("❌❌","update_character",response.status_code, response.text) 
            response.raise_for_status()  # Raise an error for bad responses

    def update_adventure(self, adventure_id, updates):
        """Update character attributes."""
        url = f"{self.base_url}/pages/{adventure_id}"
        response = requests.patch(url, headers=self.headers, json=updates)
        if response.status_code == 200:  # Check if the request was successful
            return response.json()
        else:
            print("❌❌","update_adventure",response.status_code, response.text) 
            response.raise_for_status()  # Raise an error for bad responses
        

    def persist_adventure(self, adventure, characters):
        #print(self.translate_encounter_log(adventure['encounter_log']))
        self.add_blocks(adventure['id'], 'paragraph', self.translate_encounter_log(adventure['encounter_log']))
        RESULT_LOG = adventure['resultlog'] + CLOSED_LOG + (WON_LOG if adventure['status'] == 'won' else MISSED_LOG if adventure['status'] == 'missed' else LOST_LOG)
        datau = {
            "properties": { "status": {"status": {"name":adventure['status']}},
                            "resultlog": { "rich_text": RESULT_LOG  } }
        }  
        if 'dlylog' in adventure.keys():
            datau['properties']['dlylog'] = { "relation": adventure['dlylog']  }
        if adventure['who'] is None or adventure['vs'] is None: #for orphans adventures
            rest_of_chars = []
            root = None
            if len(characters) > 0:
                root = characters[0]
                rest_of_chars = characters[-(len(characters)-1):] 
            else:
                roots = self.get_characters_by_deep_level(deep_level='l0', is_npc=True)
                root = roots[0] if len(roots[0]) > 0 else None
                rest_of_chars = [root]
            datau['properties']['who'] = { "relation": [{"id": root['id']}] }
            datau['properties']['vs'] = { "relation": [{"id": c['id']} for c in rest_of_chars] }
        upd_adventure = self.update_adventure(adventure['id'], datau)

        ''' 
        All logic for validating the Character before pushing the changes 
        '''
        upd_character = None
        for character in characters if characters else []:
            character['level'] += 1 if character['xp'] >= character['max_xp'] else 0
            character['hp'] = character['hp'] if character['hp'] < character['max_hp'] else character['max_hp']
            character['sanity'] = character['sanity'] if character['sanity'] < character['max_sanity'] else character['max_sanity']
            pct = character['hp'] / character['max_hp']
            if character['hp'] <= 0:
                character['status'] = 'dead'  
            elif pct <= 0.15:
                character['status'] = 'dying' 
            elif pct<=0.3 :
                character['status'] = 'rest'
            elif character['status'] == 'high':
                character['status'] = 'high'
            else:
                character['status'] = 'alive'
            character['xp'] += 500 if character['hp'] <= 0 else 0
            max_prop_limit = self.max_prop_limit
            for i in range(character['level']):
                max_prop_limit *= self.GOLDEN_RATIO
            character['defense'] = character['defense'] if character['defense'] <= max_prop_limit else round(max_prop_limit)
            character['attack'] = character['attack'] if character['attack'] <= max_prop_limit else round(max_prop_limit)
            character['magic'] = character['magic'] if character['magic'] <= max_prop_limit else round(max_prop_limit)
            if random.randint(0, 9) == 0: 
                pill_name = ['yellow','blue','green','red','orange','purple','gray','brown']
                i = random.randint(0, len(pill_name) - 1)
                pill_dict = { 'name': pill_name[i] + '.pill', "color": pill_name[i] }
                #print("++💊 ",character['name'],pill_dict)
                character['inventory'].append(pill_dict)

            datau = {"properties": { "level": {"number": character['level']}, 
                                    "hp": {"number": round(character['hp'])}, 
                                    "xp": {"number": round(character['xp'])}, 
                                    "respawn": {"number": character['respawn']}, 
                                    "sanity": {"number": round(character['sanity'])}, 
                                    "force": {"number": round(character['attack'])}, 
                                    "defense": {"number": round(character['defense'])}, 
                                    "coins": {"number": round(character['coins'])}, 
                                    "magic": {"number": round(character['magic'])} ,
                                    "status": {"select": {"name":character['status']} },
                                    "inventory": { "multi_select": character['inventory']}
                                }}
            upd_character = self.update_character(character, datau)
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
                if block_type == 'callout':
                    block_data['callout']['icon'] = { 'emoji': '🎖️'}
                para_data = {
                    "children": [block_data]
                }
                response = requests.patch(url, headers=self.headers, json=para_data)
                if response.status_code != 200:
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

    def translate_execution_log(self, execution_log):
        execution_log_translated = []
        colors = ['green','blue','red','orange','purple','yellow','gray','brown']
        onetime = True
        for execution in execution_log:
            execution_log_translated.append({'type': 'text','text': {'content': '\n' + str(execution),'link': None}
                                        , 'annotations': {'bold': onetime,'italic': False,'strikethrough': False
                                        , 'underline': onetime, 'code': False
                                        , 'color': random.choice(colors) + ('' if onetime else '_background') }
                                        , 'plain_text': '\n' + str(execution), 'href': None })
            onetime = False
        return execution_log_translated

    def create_adventure(self, character_id, final_enemies, xp_reward, coin_reward, description):
        today_date = datetime.now()
        end_date = today_date + timedelta(days=2) 
        data = {
            "parent": { "database_id": NOTION_DBID_ADVEN },
            "icon": {
                "emoji": "🏰" if xp_reward > 0 else "🏴‍☠️"
            },
            "properties": {
                "name": {
                    "title": [
                        {"text": {
                            "content": ("DE" if xp_reward <=0 else "") + ("ADVENTURE | " + str(random.randint(1, 666)))
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
            data['properties']['path']['multi_select'].append({"name":"discovery"}) 
        url = f"{self.base_url}/pages"
        response = requests.post(url, headers=self.headers, json=data)  # Use json instead of data
        if response.status_code == 200:  # Check if the request was successful
            adventure_id = response.json()['id']
            return { "adventure_id": adventure_id }
        else:
            print("❌❌","create_adventure",response.status_code, response.text) 
            response.raise_for_status()  # Raise an error for bad responses
            return None  # Return None if the request was not successful

    def get_adventure_by_id(self, adventure_id):
        """Retrieve an adventure by its ID."""
        url = f"{self.base_url}/pages/{adventure_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return self.translate_adventure([response.json()] if response.json() else [])[0]
    
    def start_end_dates(self, week_number, year_number=None):
        """
        Calculate the start and end dates for a given week number and year.
        Uses ISO week date standard (weeks start on Monday and end on Sunday).
        
        Args:
            week_number (int): The ISO week number (1-53)
            year_number (int, optional): The year. Defaults to current year if None.
        
        Returns:
            tuple: (start_date_str, end_date_str) in 'YYYY-MM-DD' format
        """
        try:
            # Convert to integers
            week_number = int(week_number)
            if year_number is None:
                year_number = datetime.now().year
            else:
                year_number = int(year_number)

            # Create a date object for the specified week and year
            # %G: ISO year number
            # %V: ISO week number
            # %u: Weekday (1-7, 1=Monday)
            temp_date = datetime.strptime(f'{year_number}-W{week_number:02d}-1', '%G-W%V-%u')
            
            # Calculate start date (Monday) and end date (Sunday)
            start_date = temp_date
            end_date = temp_date + timedelta(days=6)

            # Handle year boundary cases
            if start_date.year != year_number:
                # If the week starts in previous year, adjust the date
                if week_number == 1:
                    temp_date = datetime.strptime(f'{year_number}-W01-1', '%G-W%V-%u')
                    start_date = temp_date
                    end_date = temp_date + timedelta(days=6)
                # If it's the last week of the year
                elif week_number > 51:
                    temp_date = datetime.strptime(f'{year_number}-W{week_number:02d}-1', '%G-W%V-%u')
                    start_date = temp_date
                    end_date = temp_date + timedelta(days=6)

            return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

        except ValueError as e:
            print(f"Error calculating dates for week {week_number}, year {year_number}: {str(e)}")
            # Return the first and last day of the given year as fallback
            fallback_start = datetime(year_number, 1, 1)
            fallback_end = datetime(year_number, 12, 31)
            return fallback_start.strftime('%Y-%m-%d'), fallback_end.strftime('%Y-%m-%d')


    def get_challenges_by_week(self, week_number, year_number, name_str):
        """Retrieve challenges for a specific week."""
        start_date_str, end_date_str = self.start_end_dates(week_number, year_number)
        print(name_str,start_date_str,end_date_str, f"w{week_number:02}")
        # Prepare the query for Notion API
        url = f"{self.base_url}/databases/{NOTION_DBID_ADVEN}/query"
        data = {
            "filter": {
                "and": [
                    { "property": "due", "date": { "on_or_after": start_date_str}},
                    { "property": "name", "rich_text": { "contains": f"w{week_number:02}" } },
                    { "property": "name", "rich_text": { "contains": name_str}}
                ]
            }
        }
        response = requests.post(url, headers=self.headers, json=data)  # Use json to send data
        if response.status_code == 200: 
            return self.translate_adventure(response.json().get("results", []) if response.json().get("results", []) else [])
        else:
            print("❌❌","get_challenges_by_week",response.status_code, response.text)  
            response.raise_for_status() 
        return None

    def get_challenges_longeststreak(self, before_when):
        """Retrieve challenges for a specific week."""
        # Prepare the query for Notion API
        url = f"{self.base_url}/databases/{NOTION_DBID_ADVEN}/query"
        data = {
            "filter": {
                "and": [
                    { "property": "path", "multi_select": {"contains": "breakstreak"} },
                    { "property": "status", "status": { "equals": "accepted"} },
                    { "property": "due", "date": { "on_or_before": before_when}}
                ]
            }
        }
        response = requests.post(url, headers=self.headers, json=data)  # Use json to send data
        if response.status_code == 200: 
            return self.translate_adventure(response.json().get("results", []) if response.json().get("results", []) else [])
        else:
            print("❌❌","get_challenges_longeststreak",response.status_code, response.text)  
            response.raise_for_status() 
        return None

    def get_challenges_due_by_week(self, week_number, year_number, extra_weeks):
        print( week_number, year_number, extra_weeks)
        _, end_date_str = self.start_end_dates(week_number, year_number)
        week_number_back = week_number - extra_weeks
        year_number_back = year_number - 1 if week_number_back <= 0 else year_number
        week_number_back = 52 if week_number_back <= 0 else week_number_back
        start_date_str,_ = self.start_end_dates(week_number_back, year_number_back)

        print("{}🗓️{} | w{}➡️w{} | nameContains CHALLENGE".format(start_date_str,end_date_str
                                ,str(week_number_back),str(week_number)))

        # Prepare the query for Notion API
        url = f"{self.base_url}/databases/{NOTION_DBID_ADVEN}/query"
        data = {
            "filter": {
                "and": [
                    { "property": "due", "date": { "on_or_after": start_date_str}},
                    {"property": "due", "date": { "before": end_date_str }},
                    {"property": "name", "rich_text": { "contains": 'CHALLENGE' }}
                ]
            }
        }
        response = requests.post(url, headers=self.headers, json=data)  # Use json to send data
        if response.status_code == 200: 
            return self.translate_adventure(response.json().get("results", []) if response.json().get("results", []) else [])
        else:
            print("❌❌","get_challenges_due_by_week",response.status_code, response.text)  
            response.raise_for_status() 
        return None
    
    def get_due_soon_challenges(self, to_date, notion_dbid):
        end_date_str = to_date#datetime.strptime(to_date, '%Y-%m-%d')
        results = []
        # Prepare the query for Notion API
        url = f"{self.base_url}/databases/{notion_dbid}/query"
        data = {
            "filter": {
                "and": [
                    {"property": "due", "date": { "on_or_before": end_date_str }}
                    ,{ "and": [ 
                        { "property": "status", "status": { "does_not_equal": "Done"} }
                        ,{ "property": "status", "status": { "does_not_equal": "Archived"} }
                    ]}
                ]
            },
            "sorts":[{"property": "due", "direction" : "ascending"}]
        }
        response = requests.post(url, headers=self.headers, json=data) 
        if response.status_code == 200: 
            results = response.json().get("results", [])
        else:
            print("❌❌","get_due_soon_challenges",response.status_code, response.text)  
            response.raise_for_status() 
        return results
    
    def get_not_planned_yet(self, notion_dbid):
        results = []
        # Prepare the query for Notion API
        url = f"{self.base_url}/databases/{notion_dbid}/query"
        data = {
            "filter": {
                "and": [
                    {"property": "due", "date": { "is_empty": True }}
                    ,{ "and": [ 
                        { "property": "status", "status": { "does_not_equal": "Done"} }
                        ,{ "property": "status", "status": { "does_not_equal": "Archived"} }
                    ]}
                ]
            },
            "sorts":[{"property": "due", "direction" : "ascending"}]
        }
        response = requests.post(url, headers=self.headers, json=data) 
        if response.status_code == 200: 
            results = response.json().get("results", [])
        else:
            print("❌❌","get_not_planned_yet",response.status_code, response.text)  
            response.raise_for_status() 
        return results            

    def get_daily_checklist(self, week_number, year_number, start_date=None , end_date=None):
        if not start_date or not end_date:
            start_date_str, end_date_str = self.start_end_dates(week_number, year_number)
        else:
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
        # Prepare the query for Notion API
        url = f"{self.base_url}/databases/{NOTION_DBID_DLYLG}/query"
        data_filter = {
            "filter": {
                "and": [
                    { "property": "cuando", "date": { "on_or_after": start_date_str } }
                    ,{ "property": "cuando", "date": { "on_or_before": end_date_str } }
                ]
            },
            "sorts":[{"property": "cuando", "direction" : "ascending"}]
        }

        has_more = True
        start_cursor = None
        habits_cards_trn = []
        while has_more:
            if start_cursor:
                data_filter['start_cursor'] = start_cursor
            response = requests.post(url, headers=self.headers, json=data_filter)
            data = response.json()
            if response.status_code == 200: 
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
                    achieved.append("meals" if habit_daily_card['properties']['🥣']['number'] >= 2 else None)
                    achieved.append("bike" if habit_daily_card['properties']['🚲']['checkbox'] is True else None)
                    achieved.append("teeth" if habit_daily_card['properties']['🦷']['checkbox'] is True else None)
                    achieved.append("outdoors" if habit_daily_card['properties']['🏜️']['checkbox'] is True else None)
                    achieved.append("gym" if habit_daily_card['properties']['💪🏼']['checkbox'] is True else None)
                    achieved.append("movies" if habit_daily_card['properties']['🍿']['checkbox'] is True else None)
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
                        ,"mealsb" : habit_daily_card['properties']['🥣']['number'] >= 2
                        ,"bike" : habit_daily_card['properties']['🚲']['checkbox']
                        ,"teeth" : habit_daily_card['properties']['🦷']['checkbox']
                        ,"movies" : habit_daily_card['properties']['🍿']['checkbox']
                        ,"outdoors" : habit_daily_card['properties']['🏜️']['checkbox']
                        ,"gym" : habit_daily_card['properties']['💪🏼']['checkbox']
                        ,"achieved": achieved
                    })
            else:
                print("<x>|",response.status_code, response.text)  
                response.raise_for_status()  
                return []
            # Check if there are more pages
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")  
            print(f"Fetched {len(data.get('results', []))} daily cards, total so far: {len(habits_cards_trn)}")
        return habits_cards_trn

            
    dlychcklst_map = {
        '[c]od[e]' : ['tech']
        ,'[i]llustratio[n]' : ['prsnl']
        ,'[p]ersonal growt[h]' : ['gym','outdoors','teeth','bike','meals','bed','cook','social','shower','deew','beer','prsnl']
        ,'[r]eading & comic[s]' : ['read','movies']
        ,'[s]treet ar[t]' : ['outdoors','prsnl']
        ,'[t]rading crypt[o]' : ['trade']
        ,'[w]rittin[g]' : ['read','prsnl']
    }

    def translate_adventure(self, adventures):
        array_adventures = []
        #print(adventures)
        try:
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
                    ,"due": adventure['properties']['due']['date']['start'].split('T')[0]
                    ,"assigned": adventure['properties']['assigned']['people'][0]['id']
                    ,"resultlog": adventure['properties']['resultlog']['rich_text']
                    ,"path": [path['name'] for path in adventure['properties']['path']['multi_select']] if adventure['properties']['path']['multi_select'] else None
                    ,"last_edited_time": str(adventure['last_edited_time']).split('T')[0] if adventure['last_edited_time'] else None
                    ,"url": adventure['id']
                    ,"alive_range":{ "start": adventure['properties']['dateRangeAlive']['formula']['date']['start'].split('T')[0]
                                    , "end": adventure['properties']['dateRangeAlive']['formula']['date']['end'].split('T')[0]}

                })
        except Exception as e:
            print("XXXX translate_adventure ",e) 
        return array_adventures
    

    def create_challenge(self, emoji, week_number, how_many_times, character_id, xp_reward, coin_reward, habit_id):
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
                            "content": "CHALLENGE | " + f"w{week_number:02}"
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
                "habits": { "relation": [{"id": habit_id}] },
                "resultlog": { "rich_text": CREATED_LOG  }
            }
        }

        url = f"{self.base_url}/pages"
        response = requests.post(url, headers=self.headers, json=data) 
        if response.status_code == 200: 
            adventure_id = response.json()['id']
            return  self.translate_adventure([response.json()] if response.json() else [])[0]
        else:
            print("❌❌","create_challenge",response.status_code, response.text)  
            response.raise_for_status() 
            return None  

    def create_challenge_break_the_streak(self, props):
        # today_date = datetime.now() + timedelta(days=1)
        end_date = datetime.now() + timedelta(days=props['how_many_times'])
        data = {
            "parent": { "database_id": NOTION_DBID_ADVEN },
            "icon": {
                "emoji": props['emoji']
            },
            "properties": {
                "name": { "title": [ {"text": { "content": f"Break ⛓️‍💥 Streak | {props['name']}"  }} ] },
                "due": {  "date": { 'start': end_date.strftime('%Y-%m-%d') } },
                "xpRwd": { "number": props['xp_reward'] },
                "coinRwd": { "number": props['coin_reward'] },
                "desc": { "rich_text": [{"text": {"content": f"Do it for {props['how_many_times']} consecutive days to break current {props['current']} days"}}] }, 
                "who": { "relation": [{"id": props['character_id']}] },
                "vs": { "relation": [{"id": props['character_id']}] },
                "path": {"multi_select": [ {"name":"breakstreak"},{"name": '{}timesXw'.format(props['how_many_times'])}]},
                "status": {"status": {"name":"created"}},
                "habits": { "relation": [{"id": props['habit_id']}] },
                "resultlog": { "rich_text": CREATED_LOG  }
            }
        }
        url = f"{self.base_url}/pages"
        response = requests.post(url, headers=self.headers, json=data) 
        if response.status_code == 200: 
            return  self.translate_adventure([response.json()] if response.json() else [])[0]
        else:
            print("❌❌","create_challenge",response.status_code, response.text)  
            response.raise_for_status() 
            return None  

    def get_underworld_adventures(self):
        # Prepare the query for Notion API
        url = f"{self.base_url}/databases/{NOTION_DBID_ADVEN}/query"
        data_filter = {
            "filter": {
                "and": [
                    {
                        "property": "name",
                        "rich_text": {
                        "contains": "DEADVENTURE"
                        }
                    },
                    {
                        "property": "status",
                        "status": { "equals": "created"}
                    }
                ]
            }
        }
        has_more = True
        start_cursor = None
        adventures = []
        while has_more:
            if start_cursor:
                data_filter['start_cursor'] = start_cursor
            response = requests.post(url, headers=self.headers, json=data_filter)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            # Extend the characters list with the results from this page
            adventures.extend(self.translate_adventure(data.get("results", []) if data.get("results", []) else []))
            # Check if there are more pages
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")  
            print(f"Fetched {len(data.get('results', []))} deadventures, total so far: {len(adventures)}")
        
        return adventures
        
    def get_punishment_adventures(self):
        # Prepare the query for Notion API
        url = f"{self.base_url}/databases/{NOTION_DBID_ADVEN}/query"
        data = {
            "filter": {
                "and": [
                    {  "property": "path", "multi_select": {"contains": "punishment"} }
                    ,{ "property": "status", "status": { "equals": "accepted"} }
                ]
            }
        }
        response = requests.post(url, headers=self.headers, json=data)  # Use json to send data
        if response.status_code == 200: 
            return self.translate_adventure(response.json().get("results", []) if response.json().get("results", []) else [])
        else:
            print("-->",response.status_code, response.text)  # Debugging: Print the response
            response.raise_for_status()  # Raise an error for bad responses        

    def get_all_habits(self):
        url = f"{self.base_url}/databases/{NOTION_DBID_HABIT}/query"
        response = requests.post(url, headers=self.headers)
        if response.status_code != 200:  
            print("❌❌","get_all_habits",response.status_code, response.text) 
            response.raise_for_status()  
        habits = response.json().get("results", [])  
        translated_habits = []
        for habit in habits:
            translated = self.translate_habit(habit)
            translated_habits.append(translated)
            cache_key = self.redis_service.get_cache_key('habits', translated['id'])
            self.redis_service.set_with_expiry(cache_key, translated, self.expiry_hours)
        return translated_habits
    
    def translate_habit(self, habit):
        habit_level = int(habit['properties']['level']['number'])
        max_xp = self.max_xp
        for i in range(habit_level):
            max_xp *= self.GOLDEN_RATIO
        return {
            "id": habit['id'].replace('-','')
            ,"emoji": habit['icon']['emoji']
            ,"name": habit['properties']['name']['title'][-1]['plain_text']
            ,"level": habit_level
            ,"xp": habit['properties']['xp']['number']
            ,"max_xp": max_xp
            ,"coins": habit['properties']['coins']['number']
            ,"timesXweek": habit['properties']['timesXweek']['number']
            ,"who": habit['properties']['who']['relation'][0]['id'] if habit['properties']['who']['relation'] else None
        }

    def get_habit_by_id(self, habit_id):
        habit_id_replaced = habit_id.replace('-','')
        habit = None
        try:
            cache_key = self.redis_service.get_cache_key('habits', habit_id_replaced)
            habit = self.redis_service.get(cache_key)
            if habit is None:
                print(f"🕯️ not in cache [{habit_id}], going to the source")
                url = f"{self.base_url}/pages/{habit_id}"
                response = requests.get(url, headers=self.headers)
                habit = self.translate_habit(response.json() if response.json() else None)
                self.redis_service.set_with_expiry(cache_key, habit, expiry_hours=self.expiry_hours)
        except Exception as e:
            print("Failed to fetch habit:", e)
            response.raise_for_status() 
        return habit    

    def persist_habit(self, habit):
        habit['level'] += 1 if habit['xp'] >= habit['max_xp'] else 0
        datau = {"properties": { "level": {"number": habit['level']}, 
                                    "xp": {"number": habit['xp']}, 
                                    "coins": {"number": habit['coins']}}}
        upd_habit = self.update_adventure(habit['id'], datau)   
        cache_key = self.redis_service.get_cache_key('habits', habit['id'])
        self.redis_service.set_with_expiry(cache_key, habit, expiry_hours=self.expiry_hours)
        return upd_habit  
    
    def get_habits_by_property(self, property, value):
        try:
            return self.redis_service.query_habits(property, value)                
        except Exception as e:
            print(f"Failed to fetch habits by properties {property} = {value}: {e}")
            raise

    def get_all_abilities(self):
        url = f"{self.base_url}/databases/{NOTION_DBID_ABILI}/query"
        response = requests.post(url, headers=self.headers)
        if response.status_code != 200:  
            response.raise_for_status()  
        abilities = response.json().get("results", [])  
        translated_abilities = []
        for ability in abilities:
            translated = self.translate_ability(ability)
            translated_abilities.append(translated)
            cache_key = self.redis_service.get_cache_key('abilities', translated['id'])
            self.redis_service.set_with_expiry(cache_key, translated, self.expiry_hours)
        return translated_abilities

    def translate_ability(self, ability):
        max_xp = self.max_xp
        ability_level = int(ability['properties']['level']['number'])
        for i in range(ability_level):
            max_xp *= self.GOLDEN_RATIO
        return {
            "id": ability['id'].replace('-','')
            ,"name": ability['properties']['name']['title'][-1]['plain_text']
            ,"level": ability_level
            ,"xp": ability['properties']['xp']['number']
            ,"max_xp": max_xp
            ,"coins": ability['properties']['coins']['number']
        }

    def get_ability_by_id(self, ability_id):
        ability_id_replaced = ability_id.replace('-','')
        ability = None
        try:
            cache_key = self.redis_service.get_cache_key('abilities', ability_id_replaced)
            ability = self.redis_service.get(cache_key)
            if ability is None:
                print(f"🪩 not in cache [{ability_id}], going to the source")
                url = f"{self.base_url}/pages/{ability_id}"
                response = requests.get(url, headers=self.headers)
                ability = self.translate_ability(response.json() if response.json() else None)
                self.redis_service.set_with_expiry(cache_key, ability, expiry_hours=self.expiry_hours)
        except Exception as e:
            print("Failed to fetch ability:", e)
            response.raise_for_status() 
        return ability    


    def persist_ability(self, ability):
        ability['level'] += 1 if ability['xp'] >= ability['max_xp'] else 0
        datau = {"properties": { "level": {"number": ability['level']}, 
                                    "xp": {"number": ability['xp']}, 
                                    "coins": {"number": ability['coins']}}}
        if 'dlylog' in ability.keys():
            datau['properties']['dlylog'] = { "relation": ability['dlylog']  }
        
        upd_ability = self.update_adventure(ability['id'], datau)   
        cache_key = self.redis_service.get_cache_key('abilities', ability['id'])
        self.redis_service.set_with_expiry(cache_key, ability, expiry_hours=self.expiry_hours)
        return upd_ability                
    
    def get_all_open_tournaments(self):
        end_date = datetime.now() + timedelta(days = self.tour_days_vigencia) 
        end_date_str = end_date.strftime('%Y-%m-%d')
        url = f"{self.base_url}/databases/{NOTION_DBID_ADVEN}/query"
        data = {
            "filter": {
                "and": [
                    { "property": "path", "multi_select": {"contains": "tournament"} }
                    ,{ "property": "status", "status": { "equals": "created"} }
                    ,{ "property": "due", "date": { "on_or_before": end_date_str } }                    
                ]
            }
        }
        response = requests.post(url, headers=self.headers, json=data)  # Use json to send data
        if response.status_code == 200: 
            return self.translate_adventure(response.json().get("results", []) if response.json().get("results", []) else [])
        else:
            print("-->",response.status_code, response.text)  # Debugging: Print the response
            response.raise_for_status()  # Raise an error for bad responses        

    def create_tournament(self, character_id, xp_reward, coin_reward, title , description):
        today_date = datetime.now()
        end_date = today_date + timedelta(days = self.tour_days_vigencia) 
        data = {
            "parent": { "database_id": NOTION_DBID_ADVEN },
            "icon": {
                "emoji": "🏟️"
            },
            "properties": {
                "name": {
                    "title": [
                        {"text": { "content": title }}
                    ]
                },
                "due": { 
                    "date": { 'start': end_date.strftime('%Y-%m-%d') }
                },
                "xpRwd": { "number": xp_reward },
                "coinRwd": { "number": coin_reward },
                "desc": { "rich_text": [{"text": {"content": description}}] }, 
                "who": { "relation": [{"id": character_id}] },
                "vs": {"relation": [{"id": character_id}]},
                "resultlog": { "rich_text": CREATED_LOG  },
                "path": {"multi_select": [{"name": "tournament"}]}
            }
        }
        url = f"{self.base_url}/pages"
        response = requests.post(url, headers=self.headers, json=data)  
        if response.status_code == 200: 
            return self.translate_adventure([response.json()] if response.json() else [])[0]
        else:
            print("❌❌","create_tournament",response.status_code, response.text) 
            response.raise_for_status() 
            return None 





            