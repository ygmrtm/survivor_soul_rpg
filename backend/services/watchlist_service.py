from datetime import datetime, timedelta
from operator import is_not
import requests
import random 
from flask import jsonify
from backend.services.redis_service import RedisService
from config import NOTION_API_KEY, NOTION_DBID_WATCH

class WatchlistService:
    base_url = "https://api.notion.com/v1"
    expiry_hours = 8
    year_start = 1920
    year_range = 20
    size_for_loaded_suggested = 2

    _instance = None

    def __new__(cls):
        """Override __new__ to implement Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(WatchlistService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize a WatchlistService instance with headers for API requests.

        Sets up the authorization headers using the NOTION_API_KEY and
        initializes a cache for storing watchlist data.
        """
        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            'Content-Type': 'application/json'
        }
        self.redis_service = RedisService()

    def healthcheck(self):
        """
        Check the health status of the Watchlist service.

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
            # Test API Connection by fetching the watchlist database
            response = requests.get(f"{self.base_url}/databases/{NOTION_DBID_WATCH}", headers=self.headers)
            response.raise_for_status()  # Raise an error for bad responses
            # If we can fetch databases, the API is working
            health_status['status'] = 'healthy'
            health_status['api_connected'] = True
            health_status['message'] = '✅ Watchlist service is functioning normally'
        except requests.exceptions.HTTPError as http_err:
            health_status['message'] = f"❌ HTTP error occurred: {str(http_err)}"
            if response.status_code == 401:
                health_status['message'] = "❌ Authentication failed: Invalid API token"
            elif response.status_code == 404:
                health_status['message'] = "❌ Notion API endpoint not found"
        except Exception as e:
            health_status['message'] = f"❌ Watchlist service error: {str(e)}"

        return health_status

    def get_watchlist(self):
        """Retrieve the complete watchlist from Notion API or cache."""
        # Try to get from cache first
        cache_key = self.redis_service.get_cache_key('watchlist', 'all')
        cached_watchlist = self.redis_service.get(cache_key)
        if cached_watchlist is not None:
            print("Using ALL cached watchlist:", len(cached_watchlist))
            return cached_watchlist
        # If not in cache, fetch from Notion
        url = f"{self.base_url}/databases/{NOTION_DBID_WATCH}/query"
        all_watchlist = []
        has_more = True
        start_cursor = None
        while has_more:
            payload = {}
            if start_cursor:
                payload['start_cursor'] = start_cursor
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            all_watchlist.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
        # Cache the results
        translated_list = self.translate_watchlist(all_watchlist)
        self.redis_service.set_with_expiry(cache_key, translated_list, expiry_hours=self.expiry_hours * 3 )
        self.redis_service.set_with_expiry(self.redis_service.get_cache_key('watchlist', 'all_raw'), all_watchlist, expiry_hours=self.expiry_hours * 3 )
        print("Fetched and cached ALL watchlist:", len(translated_list))
        return translated_list

    def get_watchlist_by_year(self, year_from, year_to):
        """Filter watchlist by year range."""
        watchlist = self.get_watchlist()
        return_watchlist = []
        for movie in watchlist:
            if movie['año'] >= year_from and movie['año'] <= year_to:
                return_watchlist.append(movie)
        return return_watchlist

    def get_watchlist_by_estado(self, estado):
        """Filter watchlist by status."""
        watchlist = self.get_watchlist()
        return_watchlist = []
        for movie in watchlist:
            if movie['estado'] == estado and movie['semana_sugerida'] is None:
                return_watchlist.append(movie)
        return return_watchlist

    def translate_watchlist(self, watchlist=[]):
        """Translate raw Notion API watchlist data to a standardized format."""
        try:
            return_watchlist = []
            for movie in watchlist:
                titulo = movie['properties']['Original Title']['title'][-1]['plain_text']
                titulo += "("+movie['properties']['Title']['rich_text'][-1]['plain_text']+")" if movie['properties']['Title']['rich_text'][-1]['plain_text'] != movie['properties']['Original Title']['title'][-1]['plain_text'] else ""
                return_watchlist.append({
                "notion_id": movie['id'].replace('-',''),
                "imdb_id": movie['properties']['Const']['rich_text'][-1]['plain_text'] if movie['properties']['Const']['rich_text'] else None,
                "titulo": titulo,
                "tipo": movie['properties']['Title Type']['select']['name'],
                "calificacion": movie['properties']['IMDb Rating']['number'],
                "generos": movie['properties']['Genres']['rich_text'][-1]['plain_text'] if movie['properties']['Genres']['rich_text'] else None,
                "url": movie['properties']['URL']['url'],
                "estreno": movie['properties']['Release Date']['date']['start'].split('T')[0] if movie['properties']['Release Date']['date']['start'] else None,
                "estado": movie['properties']['Status']['status']['name'],
                "streaming": movie['properties']['Available in Streaming?']['checkbox'],
                "vista": movie['properties']['Watched']['checkbox'],
                "año": movie['properties']['Year']['number'],
                "directores": movie['properties']['Directors']['rich_text'][-1]['plain_text'] if movie['properties']['Directors']['rich_text'] else None,
                "minutos": movie['properties']['Runtime (mins)']['number'],
                "semana_sugerida": movie['properties']['Your Rating']['rich_text'][-1]['plain_text'] if movie['properties']['Your Rating']['rich_text'] else None
                })
            return return_watchlist
        except Exception as e:
            print("😓 Damn it i can't translate watchlist:", e)
            raise

    def get_random_watchlist(self, tamano):
        """Get a random selection from the watchlist."""
        checked_watchlist = self.get_watchlist_by_estado('checked')
        loaded_watchlist = self.get_watchlist_by_estado('loaded')
        cache_key = self.redis_service.get_cache_key('watchlist', f'suggested{tamano}')
        return_watchlist = self.redis_service.get(cache_key) if self.redis_service.get(cache_key) else [] 
        priority = 0
        while len(return_watchlist) < tamano:
            for year in range(self.year_start, datetime.now().year, 20):
                if priority == 0:
                    checked_streaming_watchlist = [movie for movie in checked_watchlist if movie['streaming'] and movie['año'] >= year and movie['año'] <= (year + self.year_range)]
                    if len(checked_streaming_watchlist) > 0:
                        return_watchlist.append(random.choice(checked_streaming_watchlist))
                elif priority == 1:
                    checked_notstreaming_watchlist = [movie for movie in checked_watchlist if not(movie['streaming']) and movie['año'] >= year and movie['año'] <= (year + self.year_range)]
                    if len(checked_notstreaming_watchlist) > 0:
                        return_watchlist.append(random.choice(checked_notstreaming_watchlist))
                elif priority == 2:
                    loaded_watchlist_todo = [movie for movie in loaded_watchlist if movie['año'] >= year and movie['año'] <= (year + self.year_range)]
                    if len(loaded_watchlist_todo) > 0:
                        return_watchlist.append(random.sample(loaded_watchlist_todo, self.size_for_loaded_suggested if len(loaded_watchlist_todo) >= self.size_for_loaded_suggested else len(loaded_watchlist_todo)))
                #print(f"🎬 Getting random watchlist for year {year} to {year + self.year_range} | {priority} | {len(return_watchlist)}")
            priority += 1 if priority < 2 else 0
        return return_watchlist[:tamano]

    def persist_suggested_watchlist(self, watchlist, week):
        #print(f'got {len(watchlist)} for week {week}')
        for movie in watchlist:
            cache_key = self.redis_service.get_cache_key('watchlist:suggested', movie['imdb_id'])
            if not(self.redis_service.exists(cache_key)):
                movie['semana_sugerida'] = (movie['semana_sugerida'] if movie['semana_sugerida'] else '') + ' | w' + str(week) 
                #persist in Notion
                datau = { "icon" : { "emoji" : "🎞️" },
                    "properties": { "Your Rating": { "rich_text": [{"text": {"content": movie['semana_sugerida']}}] },}}
                self.update_movie(movie['notion_id'], datau)
                #persist in Redis
                self.redis_service.set_with_expiry(cache_key, movie, expiry_hours=self.expiry_hours * 3 * 7)
        cache_key = self.redis_service.get_cache_key('watchlist', f'suggested{len(watchlist)}')
        self.redis_service.set_with_expiry(cache_key, watchlist, expiry_hours=self.expiry_hours * 3 * 7)
        return watchlist


    def update_movie(self, movie_notion_id, updates):
        """Update character attributes."""
        url = f"{self.base_url}/pages/{movie_notion_id}"
        response = requests.patch(url, headers=self.headers, json=updates)
        if response.status_code == 200: 
            return response.json()
        else:
            print("❌❌","update_movie",response.status_code, response.text) 
            response.raise_for_status()  
