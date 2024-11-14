class AdventureService:
    def create_adventure(self, name, difficulty):
        """Create a new adventure based on specified parameters."""
        # Generate a mock adventure data, to be expanded with game logic
        return {
            "name": name,
            "difficulty": difficulty,
            "status": "Not Started"
        }

    def execute_adventure(self, adventure_id):
        """Run the logic for executing an adventure."""
        # Example logic for executing an adventure
        return {
            "adventure_id": adventure_id,
            "status": "Completed",
            "reward": {
                "xp": 100,
                "coins": 50
            }
        }

    def create_challenge(self, name, reward):
        """Create a new challenge with a given reward."""
        return {
            "name": name,
            "reward": reward,
            "status": "Pending"
        }
