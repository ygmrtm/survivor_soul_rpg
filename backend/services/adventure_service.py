from backend.services.notion_service import NotionService
import random 

class AdventureService:
    GOLDEN_RATIO = 1.618033988749895
    max_chapters = 7
    max_xprwd = 4
    max_coinrwd = 10    

    def create_adventure(self, character_id):
        """Create a new adventure based on specified parameters."""
        notion_service = NotionService()
        
        # Retrieve the character using the character_id
        character = notion_service.get_character_by_id(character_id)
        
        if not character:
            raise ValueError(f"Character with ID {character_id} not found.")
        
        character_level = character['level']
        max_chapters = self.max_chapters
        max_xprwd = self.max_xprwd
        max_coinrwd = self.max_coinrwd
        
        for i in range(character_level):
            max_chapters *= self.GOLDEN_RATIO
            max_xprwd *= self.GOLDEN_RATIO
            max_coinrwd *= self.GOLDEN_RATIO
        
        # Get NPC characters for enemies
        npc_characters = notion_service.filter_by_deep_level(deep_level='l3', is_npc=True)
        filtered_enemies = [c for c in npc_characters if c['status'] == 'alive']
        enemies_to_encounter = random.randint(1, max_chapters)
        final_enemies = random.sample(filtered_enemies, min(enemies_to_encounter, len(filtered_enemies)))
        final_enemies_ids = [{"id":enemy['id']} for enemy in final_enemies]
        xp_reward = random.randint(1, max_xprwd)
        coin_reward = random.randint(1, max_coinrwd)
        description = "dummy desc" #TODO generate with groq

        # Get NPC GODS characters for support and pick only one.
        npc_characters = notion_service.filter_by_deep_level(deep_level='l2', is_npc=True)
        god_support = random.choice(npc_characters) if npc_characters else None

        response = notion_service.create_adventure(character_id, god_support["id"], final_enemies_ids, xp_reward, coin_reward, description)
        return response
    
    def create_challenges(self, week_number):
        notion_service = NotionService()        

    def execute_adventure(self, adventure_id):
        """Run the logic for executing an adventure."""
        # Example logic for executing an adventure
        # You can expand this with actual game logic
        return {
            "adventure_id": adventure_id,
            "status": "completed",
            "reward": {
                "xpRwd": 100,
                "coinRwd": 50
            }
        }

