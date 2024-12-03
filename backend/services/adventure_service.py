class AdventureService:
    
    """
    Create a new adventure with the specified name and difficulty.

    Args:
    name (str): The name of the adventure.
    difficulty (str): The difficulty level of the adventure.

    Returns:
    dict: A dictionary containing the adventure details, including
            its name, difficulty, and initial status.
    """
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
            "status": "completed",
            "reward": {
                "xpRwd": 100,
                "coinRwd": 50
            }
        }

    """
    Create a new challenge with the specified name and reward.

    Args:
    name (str): The name of the challenge.
    reward (any): The reward associated with the challenge.

    Returns:
    dict: A dictionary containing the challenge details, including
            its name, reward, and initial status.
    """
def create_challenge(self, name, reward):
        """Create a new challenge with a given reward."""
        return {
            "name": name,
            "reward": reward,
            "status": "Pending"
        }
