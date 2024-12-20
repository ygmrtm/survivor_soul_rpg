from datetime import date, datetime
from backend.services import notion_service
from backend.services.notion_service import NotionService
import random 
import time

class AdventureService:
    GOLDEN_RATIO = 1.618033988749895
    max_chapters = 7
    max_xprwd = 4
    max_coinrwd = 10    
    percentage_habits = 0.5 # for challenges how many habits to pick
    encounter_log = []
    dice_size = 16

    def create_adventure(self, character_id, underworld=False):
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
        npc_gods = notion_service.filter_by_deep_level(deep_level='l2', is_npc=True)
        filtered_enemies = [c for c in npc_characters if c['status'] == 'alive']
        filtered_death_gods = [c for c in npc_gods if c['status'] == 'dead']
        enemies_to_encounter = random.randint(1, max_chapters)
        final_enemies = random.sample(filtered_enemies, min(enemies_to_encounter, len(filtered_enemies)))
        final_enemies_ids = [{"id":enemy['id']} for enemy in final_enemies]
        xp_reward = random.randint(1, max_xprwd)
        coin_reward = random.randint(1, max_coinrwd)
        description = "dummy desc" #TODO generate with groq
        if underworld is False:
            response = notion_service.create_adventure(character_id, final_enemies_ids, xp_reward, coin_reward, description)
        else:
            response = notion_service.create_adventure(character_id, [{"id":random.choice(filtered_death_gods)['id']}], xp_reward *-1, coin_reward=0, description="Underworld Training 101")
        return response
    
    def create_challenges(self, week_number):
        notion_service = NotionService()   
        challenges_all = notion_service.get_challenges_by_week(week_number, "CHALLENGE") 
        challenges = [challenge for challenge in challenges_all if challenge['status'] in ('created','accepted','on going')]
        if len(challenges) <= 0:
            print("no challenges found for weeek ", week_number)
            habits = notion_service.get_all_habits()
            how_many_challenges = random.randint(1,int(len(habits) * self.percentage_habits))
            sample_habits = random.sample(habits, min(how_many_challenges, len(habits)))
            for habit in sample_habits:
                habit_level = habit['level']
                max_xprwd = self.max_xprwd
                max_coinrwd = self.max_coinrwd
                for i in range(habit_level):
                    max_xprwd *= self.GOLDEN_RATIO
                    max_coinrwd *= self.GOLDEN_RATIO
                xp_reward = random.randint(1, max_xprwd)
                coin_reward = random.randint(1, max_coinrwd)                
                how_many_times = random.randint(1, 7)
                challenge = notion_service.create_challenge(habit['emoji'], week_number, how_many_times, habit['who'], xp_reward, coin_reward, habit['id'])
                challenges.append(challenge)
        return challenges
        
    def evaluate_challenges(self, week_number):
        notion_service = NotionService()   
        ### by Consecutive days Challenges
        challenges_all = notion_service.get_challenges_by_week(week_number, "CHALLENGE") 
        challenges = [challenge for challenge in challenges_all if challenge['status'] in ('created','accepted','on going')]
        if len(challenges) <= 0:
            print("no challenges found for weeek ", week_number)
        for challenge in challenges:
            dlylog_array = []
            self.encounter_log = []
            notion_service = NotionService()
            habit_id = challenge['habits'][0]
            habit = notion_service.get_habits_by_id_or_name(habit_id['id'], None)
            who = notion_service.get_character_by_id(habit['who'])
            path_array = challenge['path']
            xTimesWeek = next((item for item in path_array if item[0].isdigit() and 1 <= int(item[0]) <= 7), None)
            daily_checklist = notion_service.get_daily_checklist(week_number)    
            consecutive = max_consecutive = 0
            for dly_card in daily_checklist:
                if habit['name'] in dly_card['achieved']:
                    habit['xp'] += self.add_encounter_log(1, 'xp', dly_card['cuando'] + ' | ' + habit['name'] )
                    who['xp'] += self.add_encounter_log(1, 'xp', dly_card['cuando'] + ' | ' + who['name'] )
                    who['sanity'] += self.add_encounter_log(1, 'sanity', dly_card['cuando'] + ' | ' + who['name'] )
                    consecutive += 1
                    max_consecutive = max(max_consecutive, consecutive)
                    dlylog_array.append({"id":dly_card['id']})
                else:
                    consecutive = 0
            if max_consecutive >= int(xTimesWeek[:1]):
                challenge['status'] = 'won'
                habit['xp'] += self.add_encounter_log(challenge['xpRwd'],"xp","Won challenge by {}/{} consecutive times | {}".format(max_consecutive, xTimesWeek[:1], habit['name'] ))
                who['xp'] += self.add_encounter_log(challenge['xpRwd'],"xp","Thanks to {}, {} got up".format(habit['name'], who['name'] ))
                who['sanity'] += self.add_encounter_log(challenge['xpRwd'],"sanity","Thanks to {}, {} got up".format(habit['name'], who['name'] ))
                how_much = (random.randint(1, 50) / 100)
                send_coins = how_much * challenge['coinRwd']
                keep_coins = challenge['coinRwd'] - send_coins
                who['coins'] += self.add_encounter_log(keep_coins,"coins","Challenge 💵 earned (out of {})".format(challenge['coinRwd']))
                self.add_encounter_log(send_coins, "coins", '🎉 Thanks for the {}% donation [{}/{}]'.format(how_much * 100, send_coins, keep_coins))
                self.distribute_tribute(who['alter_ego'], send_coins) 
            else:
                challenge['status'] = 'lost'
                habit['xp'] += self.add_encounter_log(challenge['xpRwd']*-1,"xp","Failed challenge {} just getting miserable {}/{} times | {}".format(xTimesWeek, max_consecutive, xTimesWeek[:1], habit['name'] ))
                who['xp'] += self.add_encounter_log(challenge['xpRwd']*-1,"xp","Due to {} got failure in {}".format(who['name'] , habit['name'] ))
                who['sanity'] += self.add_encounter_log(challenge['xpRwd']*-1,"sanity","Due to {} got failure in {}".format(who['name'] , habit['name'] ))
            challenge['encounter_log'] = self.encounter_log
            challenge['dlylog'] = dlylog_array
            notion_service.persist_habit(habit)
            notion_service.persist_adventure(adventure=challenge, characters=[who])

        ### by Week Habits
        challenges_all = notion_service.get_challenges_by_week(week_number, "HABIT")
        challenges = [challenge for challenge in challenges_all if challenge['status'] in ('accepted','on going')]
        if len(challenges) <= 0:
            print("no habit challenges found for weeek ", week_number)
        
        for challenge in challenges:
            dlylog_array = []
            self.encounter_log = []
            notion_service = NotionService()
            habit_id = challenge['habits'][0]
            habit = notion_service.get_habits_by_id_or_name(habit_id['id'], None)
            who = notion_service.get_character_by_id(habit['who'])
            path_array = challenge['path']
            xTimesWeek = next((item for item in path_array if item[0].isdigit() and 1 <= int(item[0]) <= 7), None)
            daily_checklist = notion_service.get_daily_checklist(week_number)    
            total_got = 0
            for dly_card in daily_checklist:
                if habit['name'] in dly_card['achieved']:
                    habit['xp'] += self.add_encounter_log(1, 'xp', dly_card['cuando'] + ' | ' + habit['name'] )
                    who['xp'] += self.add_encounter_log(1, 'xp', dly_card['cuando'] + ' | ' + who['name'] )
                    who['sanity'] += self.add_encounter_log(1, 'sanity', dly_card['cuando'] + ' | ' + who['name'] )
                    dlylog_array.append({"id":dly_card['id']})
                    total_got += 1
            if total_got >= int(xTimesWeek[:1]):
                challenge['status'] = 'won'
                habit['xp'] += self.add_encounter_log(challenge['xpRwd'],"xp","Won Week Habit challenge by {}/{} | {}".format(total_got, xTimesWeek[:1], habit['name'] ))
                who['xp'] += self.add_encounter_log(challenge['xpRwd'],"xp","Thanks to {}, {} got up".format(habit['name'], who['name'] ))
                who['sanity'] += self.add_encounter_log(challenge['xpRwd'],"sanity","Thanks to {}, {} got up".format(habit['name'], who['name'] ))
                how_much = (random.randint(1, 50) / 100)
                send_coins = how_much * challenge['coinRwd']
                keep_coins = challenge['coinRwd'] - send_coins
                who['coins'] += self.add_encounter_log(keep_coins,"coins","Challenge 💵 earned (out of {})".format(challenge['coinRwd']))
                self.add_encounter_log(send_coins, "coins", '🎉 Thanks for the {}% donation [{}/{}]'.format(how_much * 100, send_coins, keep_coins))
                self.distribute_tribute(who['alter_ego'], send_coins) 
            else:
                challenge['status'] = 'lost'
                habit['xp'] += self.add_encounter_log(challenge['xpRwd']*-1,"xp","Failed habit week challenge {} just getting miserable {}/{} | {}".format(xTimesWeek, total_got, xTimesWeek[:1], habit['name'] ))
                who['xp'] += self.add_encounter_log(challenge['xpRwd']*-1,"xp","Due to {} got failure in {}".format(who['name'] , habit['name'] ))
                who['sanity'] += self.add_encounter_log(challenge['xpRwd']*-1,"sanity","Due to {} got failure in {}".format(who['name'] , habit['name'] ))
            notion_service.persist_habit(habit)
            gods_winner = []
            if "encounter" in path_array:
                npc_characters = notion_service.filter_by_deep_level(deep_level='l2', is_npc=True)
                high_gods = [c for c in npc_characters if c['status'] == 'high']
                god_winner = random.choice(high_gods) if high_gods else None
                god_winner['xp'] += self.add_encounter_log(challenge['xpRwd'],"xp",'winner ⚡️{}⚡️'.format(god_winner['name']))
                properties = ['magic', 'attack', 'defense']
                total = 0
                for prop in properties:
                    total += god_winner[prop]
                average_properties = total / len(properties)
                random_prop = random.choice(properties)
                god_winner[random_prop] += self.add_encounter_log(average_properties, random_prop, 'winner ⚡️{}⚡️'.format(god_winner['name']))
                gods_winner.append(god_winner)
            gods_winner.append(who)
            challenge['encounter_log'] = self.encounter_log
            challenge['dlylog'] = dlylog_array
            notion_service.persist_adventure(adventure=challenge, characters=gods_winner)

        return challenges
        
    def execute_adventure(self, adventure_id):
        """Run the logic for executing an adventure."""
        notion_service = NotionService()
        self.encounter_log = []
        adventure = notion_service.get_adventure_by_id(adventure_id)
        status = adventure['status']
        if status in ('created', 'accepted', 'on going'):
            enemies = []
            who = notion_service.get_character_by_id(adventure['who'])
            if datetime.strptime(adventure['due'], "%Y-%m-%d") < datetime.today():
                delta = datetime.strptime(adventure['due'], "%Y-%m-%d") - datetime.today()
                self.add_encounter_log(0,"","Missed adventure by {} days".format(delta.days * -1))
                adventure['status'] = 'missed'
            elif "encounter" in adventure['path']:
                # Get NPC GODS characters for support and pick only one.
                npc_characters = notion_service.filter_by_deep_level(deep_level='l2', is_npc=True)
                high_gods = [c for c in npc_characters if c['status'] == 'high']
                god_support = random.choice(high_gods) if high_gods else None
                self.add_encounter_log(god_support['level'], "level",'powered⚡️by⚡️{}'.format(god_support['name']))
                for vs in adventure['vs']:
                    enemies.append(notion_service.get_character_by_id(vs['id']))
                if self.execute_encounter(who, enemies, god_support) is True:
                    who['xp'] += self.add_encounter_log(adventure['xpRwd'],"xp","Adventure XP earned")
                    how_much = (random.randint(1, 50) / 100)
                    send_coins = how_much * adventure['coinRwd']
                    keep_coins = adventure['coinRwd'] - send_coins
                    who['coins'] += self.add_encounter_log(keep_coins,"coins","Adventure 💵 earned (out of {})".format(adventure['coinRwd']))
                    self.add_encounter_log(send_coins, "coins", '🎉 Thanks for the {}% donation [{}/{}]'.format(how_much * 100, send_coins, keep_coins))
                    self.distribute_tribute(who['alter_ego'], send_coins) 
                    adventure['status'] = 'won'
                else:
                    #TODO: undead adventure
                    new_adventure = self.create_adventure(who['id'], underworld=True)
                    self.add_encounter_log(0, "", 'You lost the Adventure')
                    adventure['status'] = 'lost'
            enemies.append(who)
            adventure['encounter_log'] = self.encounter_log
            notion_service.persist_adventure(adventure=adventure, characters=enemies)
        return {
            "adventure_id": adventure_id,
            "status": adventure['status'],
            "reward": {
                "xpRwd": adventure['xpRwd'],
                "coinRwd": adventure['coinRwd']
            }
        }

    def execute_encounter(self, who, enemies, god_suuport):
        if not enemies:
            raise ValueError(f"Not enemies found for adventure.")
        fights = 0
        while who['hp'] >= 0 and fights < len(enemies):
            for enemy in enemies:
                self.add_encounter_log(0,"","Encountered with {}.".format(str(enemy['name']).upper()))
                if self.negotiate(who, enemy) is False:
                    self.fight(who, enemy, god_suuport)
                fights += 1
        if who['hp'] <= 0:
            self.add_encounter_log(who['hp'], "hp", 'You have been defeated in {} encounters.'.format(fights))
            return False
        return True

    def negotiate (self, who, enemy)-> bool:
        sanity = who['sanity'] + random.randint(1, self.dice_size)  - enemy['sanity'] - random.randint(1, self.dice_size)
        magic = who['magic'] + random.randint(1, self.dice_size)  - enemy['magic'] - random.randint(1, self.dice_size)
        if sanity > 0 and magic > 0:
            who['xp'] += self.add_encounter_log(random.randint(1,5), "xp", "You successfully negotiated with the enemy.")
            return True
        if sanity < 0 and magic < 0:
            who['sanity'] += self.add_encounter_log(-2, "sanity", "You failed the negotiations.")
            return False
        if random.randint(0,9) % 2 == 0:
            new_sanity = round((who['sanity'] + enemy['sanity']) / 2) 
            new_magic = round((who['magic'] + enemy['magic']) / 2) 
            self.add_encounter_log(0, "", 'You have been Cursed w {} sanity'.format(new_sanity))
            self.add_encounter_log(0, "", 'You have been Cursed w {} magic'.format(new_magic))
            who['sanity'] = enemy['sanity'] = new_sanity
            who['magic'] = enemy['magic'] = new_magic
            return False     
        else:
            return self.negotiate(who, enemy)


    def fight(self, who, enemy, god) -> bool:
        rounds = 0
        while who['hp'] > 0 and enemy['hp'] > 0:
            rounds += 1
            if random.randint(0, 1) % 2 == 0: #Magic Attack
                damage = who['magic'] + god['magic'] + random.randint(1, self.dice_size) - enemy['magic'] - random.randint(1, self.dice_size)
            else: #Physical Attack
                damage = who['attack'] + god['attack'] + random.randint(1, self.dice_size) - enemy['defense'] - random.randint(1, self.dice_size)
            if random.randint(0, 2) % 3 != 0: #aimed attack
                enemy['hp'] += self.add_encounter_log(damage*-1 if damage > 0 else 0, "hp", 'R{} | You aimed your attack.'.format(rounds))
            else:
                self.add_encounter_log(damage*-1 if damage > 0 else 0, "hp", 'R{} | You missed your attack.'.format(rounds))
            if random.randint(0, 1) % 2 == 0: #Magic Defense
                damage = enemy['magic'] + random.randint(1, self.dice_size) - who['magic'] - god['magic'] - random.randint(1, self.dice_size)
            else: #Physical Defense
                damage = enemy['attack'] + random.randint(1, self.dice_size) - who['defense'] - god['defense'] - random.randint(1, self.dice_size)
            if random.randint(0, 2) % 3 != 0: #aimed defense
                who['hp'] += self.add_encounter_log(damage*-1 if damage > 0 else 0, "hp", 'R{} | Enemy aimed the attack.'.format(rounds))
            else:
                self.add_encounter_log(damage*-1 if damage > 0 else 0, "hp", 'R{} | Enemy missed the attack.'.format(rounds))
        if who['hp'] <= 0:
                self.add_encounter_log(who['hp'], "hp", 'You have been defeated by the enemy.')
                enemy['xp'] += self.steal_property(loser=who, winner=enemy)
                return False
        if enemy['hp'] <= 0:
                self.add_encounter_log(who['hp'], "hp", 'You have defeated the enemy. ({}HP)'.format(enemy['hp']))
                who['xp'] += self.steal_property(loser=enemy, winner=who)
                return True
        return False

    def add_encounter_log(self, points, type, why):
        self.encounter_log.append({
            "time": time.time(),
            "points": points,
            "type": str(type).upper() if type else "",
            "why": why
        })
        return points

    def steal_property(self, loser, winner):
        percentage = random.randint(1, 100) / 100
        property_value = random.choice(['coins', 'defense', 'attack', 'magic'])
        transfer = percentage * loser[property_value]
        winner[property_value] += transfer
        loser[property_value] -= transfer

        self.add_encounter_log(transfer, property_value, '{} stole {} from {}.'.format(winner['name'], transfer, loser['name']))
        experience_won = self.add_encounter_log(random.randint(1, 10), 'xp', 'UP!')
        return experience_won

    def distribute_tribute(self, who_id, coins ):
        notion_service = NotionService()
        alter_ego = notion_service.get_character_by_id(who_id)
        how_much = send_coins = 0
        keep_coins = coins
        if alter_ego['alter_ego']:
            how_much = (random.randint(1, 50) / 100)
            send_coins = how_much * coins
            keep_coins = coins - send_coins
            self.add_encounter_log(send_coins, "coins", '🎉 Thanks for the {}% donation [{}/{}] | {}'.format(how_much * 100, send_coins, keep_coins, alter_ego['name']))
            self.distribute_tribute(alter_ego['alter_ego'], send_coins)
        alter_ego['coins'] += self.add_encounter_log(keep_coins,"coins","⚡️{}⚡️{}⚡️ tribute 💵 earned w/o doing a 💩".format(alter_ego['deep_level'],alter_ego['name']))
        datau = {"properties": { "coins": {"number": alter_ego['coins']} }}
        upd_character = notion_service.update_character(alter_ego['id'], datau)
        return upd_character