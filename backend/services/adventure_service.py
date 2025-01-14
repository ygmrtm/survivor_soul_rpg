from datetime import  datetime, timedelta
from backend.services import notion_service
from backend.services.notion_service import NotionService
from backend.services.coding_service import CodingService
from backend.services.bike_service import BikingService
from backend.services.stencil_service import StencilService
from backend.services.epics_service import EpicsService
from backend.services.todoist_service import TodoistService

from config import NOTION_DBID_CODIN, NOTION_DBID_BIKES, NOTION_DBID_STENC, NOTION_DBID_EPICS
from config import TODOIST_PID_INB, TODOIST_PID_CAL

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

    def create_adventure(self, character_id, underworld=False, notion_service=None):
        """Create a new adventure based on specified parameters."""
        notion_service = NotionService() if not notion_service else notion_service
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
        xp_reward = random.randint(1, max_xprwd)
        coin_reward = random.randint(1, max_coinrwd)
        description = "dummy desc"
        #print(final_enemies,"\n\n")
        if underworld is False:
            npc_characters = notion_service.get_characters_by_deep_level(deep_level='l3', is_npc=True)
            filtered_enemies = [c for c in npc_characters if c['status'] == 'alive']
            enemies_to_encounter = random.randint(1, max_chapters)
            final_enemies = random.sample(filtered_enemies, min(enemies_to_encounter, len(filtered_enemies)))
            final_enemies_ids = [{"id":enemy['id']} for enemy in final_enemies]
            description = "Adventure to die for..." 
            response = notion_service.create_adventure(character_id, final_enemies_ids, xp_reward, coin_reward, description)
        else:
            npc_gods = notion_service.get_characters_by_deep_level(deep_level='l2', is_npc=True)
            filtered_death_gods = [c for c in npc_gods if c['status'] == 'dead']
            description = "Underworld Training 101"
            response = notion_service.create_adventure(character_id, [{"id":random.choice(filtered_death_gods)['id']}], xp_reward *-1, coin_reward=0, description=description)
        return response
    
    def create_challenges(self, week_number, year_number):
        notion_service = NotionService()   
        challenges_all = notion_service.get_challenges_by_week(week_number, year_number, "CHALLENGE") 
        challenges = [challenge for challenge in challenges_all if challenge['status'] in ('created','accepted','on going')]
        if len(challenges) <= 0:
            print("no challenges found for weeek ", f"w{week_number:02}")
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
        
    def evaluate_consecutivedays_challenges(self, week_number, year_number):
        notion_service = NotionService()   
        ### by Consecutive days Challenges
        challenges_all = notion_service.get_challenges_by_week(week_number, year_number, "CHALLENGE") 
        challenges = [challenge for challenge in challenges_all if challenge['status'] in ('created','accepted','on going')]
        if len(challenges) <= 0:
            print("no challenges found for weeek ", week_number)
        for challenge in challenges:
            dlylog_array = []
            self.encounter_log = []
            notion_service = NotionService()
            habit_id = challenge['habits'][0]
            habit = notion_service.get_habit_by_id(habit_id['id'])
            who = notion_service.get_character_by_id(habit['who'])
            path_array = challenge['path']
            xTimesWeek = next((item for item in path_array if item[0].isdigit() and 1 <= int(item[0]) <= 7), None)
            daily_checklist = notion_service.get_daily_checklist(week_number, year_number)    
            consecutive = max_consecutive = 0
            for dly_card in daily_checklist:
                if habit['name'] in dly_card['achieved']:
                    habit['xp'] += self.add_encounter_log(10, 'xp', dly_card['cuando'] + ' | ' + habit['name'] )
                    who['xp'] += self.add_encounter_log(10, 'xp', dly_card['cuando'] + ' | ' + who['name'] )
                    who['sanity'] += self.add_encounter_log(10, 'sanity', dly_card['cuando'] + ' | ' + who['name'] )
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
        return challenges
    
    def evaluate_weekhabits_challenges(self, week_number, year_number):
        notion_service = NotionService()
        ### by Week Habits
        challenges_all = notion_service.get_challenges_by_week(week_number, year_number, "HABIT")
        challenges = [challenge for challenge in challenges_all if challenge['status'] in ('accepted','on going')]
        if len(challenges) <= 0:
            print("no habit challenges found for weeek ", week_number)
        
        for challenge in challenges:
            dlylog_array = []
            self.encounter_log = []
            notion_service = NotionService()
            habit_id = challenge['habits'][0]
            habit = notion_service.get_habit_by_id(habit_id['id'])
            who = notion_service.get_character_by_id(habit['who'])
            path_array = challenge['path']
            xTimesWeek = next((item for item in path_array if item[0].isdigit() and 1 <= int(item[0]) <= 7), None)
            daily_checklist = notion_service.get_daily_checklist(week_number, year_number)    
            total_got = 0
            for dly_card in daily_checklist:
                if habit['name'] in dly_card['achieved']:
                    habit['xp'] += self.add_encounter_log(10, 'xp', dly_card['cuando'] + ' | ' + habit['name'] )
                    who['xp'] += self.add_encounter_log(10, 'xp', dly_card['cuando'] + ' | ' + who['name'] )
                    who['sanity'] += self.add_encounter_log(10, 'sanity', dly_card['cuando'] + ' | ' + who['name'] )
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
                npc_characters = notion_service.get_characters_by_deep_level(deep_level='l2', is_npc=True)
                high_gods = [c for c in npc_characters if c['status'] == 'high']
                god_winner = random.choice(high_gods) if high_gods else None
                #print("❎❎❎❎",god_winner,len(high_gods))
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

    def evaluate_expired_challenges(self,week_number, year_number):
        notion_service = NotionService()
        ### by Week Habits
        challenges_all = notion_service.get_due_challenges_by_week(week_number, year_number, 1 )
        due_challenges = [challenge for challenge in challenges_all if challenge['status'] in ('accepted','on going','created','missed')]
        won_challenges = [challenge for challenge in challenges_all if challenge['status'] in ('won')]
        print("{} due challenges found ".format(len(due_challenges)))
        print("{} won challenges found ".format(len(won_challenges)))
        upd_challenges = []
        for challenge in due_challenges:
            days_off = abs((datetime.strptime(challenge['alive_range']['end'], '%Y-%m-%d') 
                    - datetime.strptime(challenge['due'], '%Y-%m-%d')).days)        
            print(challenge['name'], challenge['status'], challenge['xpRwd'], challenge['coinRwd'])
            self.encounter_log = []
            notion_service = NotionService()
            who = None
            pool_whos = []
            for habit in challenge['habits']:
                habit_obj = notion_service.get_habit_by_id(habit['id'])
                habit_obj['xp'] += self.add_encounter_log(challenge['xpRwd']*-1,"xp"
                                                ,"Failed challenge for {}".format(habit_obj['name'] ))
                habit_obj['xp'] += self.add_encounter_log(days_off*-1,"xp"
                                                ,"Failed challenge for {} w {} days off".format(habit_obj['name'], days_off ))
                notion_service.persist_habit(habit_obj)
                who = notion_service.get_character_by_id(habit_obj['who'])
                who['xp'] += self.add_encounter_log(challenge['xpRwd']*-1,"xp"
                                                    ,"got failure for {}".format(who['name'] ))
                who['xp'] += self.add_encounter_log(days_off*-1,"xp"
                                                    ,"got failure for {} w {} days off".format(who['name'], days_off))
                who['sanity'] += self.add_encounter_log(challenge['xpRwd']*-1,"sanity"
                                                        ,"got failure for {}".format(who['name'] ))
            if who['id'] not in [character['id'] for character in pool_whos]:
                pool_whos.append(who)
            prev_status = challenge['status']
            self.add_encounter_log(self.GOLDEN_RATIO, "status", 'old status [{}]'.format(prev_status))
            challenge['status'] = 'lost'
            challenge['encounter_log'] = self.encounter_log
            upd_adventure, upd_character = notion_service.persist_adventure(adventure=challenge, characters=pool_whos)
            upd_challenges.append({ 'adventure_id':upd_adventure['id']
                                , 'who_id':upd_character['id']
                                , 'challenge_name':challenge['name']
                                , 'status':challenge['status'] 
                                , 'status_old':prev_status })
        
        for challenge in won_challenges:
            print(challenge['name'], challenge['status'], challenge['xpRwd'], challenge['coinRwd'])
            days_alive = abs((datetime.strptime(challenge['alive_range']['end'], '%Y-%m-%d') 
                    - datetime.strptime(challenge['alive_range']['start'], '%Y-%m-%d')).days)
            self.encounter_log = []
            notion_service = NotionService()
            who = None
            pool_whos = []
            for habit in challenge['habits']:
                habit_obj = notion_service.get_habit_by_id(habit['id'])
                habit_obj['xp'] += self.add_encounter_log(challenge['xpRwd'],"xp"
                                                        ,"Won challenge for {}".format(habit_obj['name'] ))
                habit_obj['xp'] += self.add_encounter_log(days_alive,"xp"
                                                        ,"Won challenge for {} w {} days alive".format(habit_obj['name'], days_alive ))
                notion_service.persist_habit(habit_obj)
                who = notion_service.get_character_by_id(habit_obj['who'])
                who['xp'] += self.add_encounter_log(challenge['xpRwd'],"xp"
                                                    ,"got victory for {}".format(who['name'] ))
                who['xp'] += self.add_encounter_log(days_alive,"xp"
                                                    ,"got victory for {} w {} alive".format(who['name'], days_alive ))
                who['sanity'] += self.add_encounter_log(challenge['xpRwd'],"sanity"
                                                    ,"got victory for {}".format(who['name'] ))
            if who['id'] not in [character['id'] for character in pool_whos]:
                pool_whos.append(who)
            prev_status = challenge['status']
            self.add_encounter_log(0, "status", 'old status [{}]'.format(prev_status))
            challenge['status'] = 'Archived'
            challenge['encounter_log'] = self.encounter_log
            upd_adventure, upd_character = notion_service.persist_adventure(adventure=challenge, characters=pool_whos)
            upd_challenges.append({ 'adventure_id':upd_adventure['id']
                                , 'who_id':upd_character['id']
                                , 'challenge_name':challenge['name']
                                , 'status':challenge['status'] 
                                , 'status_old':prev_status })
        return upd_challenges
    
    def evaluate_challenges_due_soon(self, lookforward):
        notion_service = NotionService()
        today_str = datetime.today().strftime('%Y-%m-%d')
        end_date = datetime.today() + timedelta(days=lookforward)
        end_date_str = end_date.strftime('%Y-%m-%d')
        challenges_array = []
        for dbid in [{"id":NOTION_DBID_CODIN,"notion_char":"c"}
                    , {"id":NOTION_DBID_BIKES,"notion_char":"b"}
                    , {"id":NOTION_DBID_STENC,"notion_char":"s"}
                    , {"id":NOTION_DBID_EPICS,"notion_char":"e"}]:
            results = notion_service.get_due_soon_challenges(end_date_str, dbid['id'])
            print(f"🔎🔎🔎 {dbid['notion_char']}:{len(results)} before {end_date}")
            if dbid['notion_char'] == 'c':
                coding_service = CodingService()
                challenges_array.extend(coding_service.translate_coding_tasks(results))
            elif dbid['notion_char'] == 'b':
                bike_service = BikingService()
                challenges_array.extend(bike_service.translate_biking_tasks(results))
            elif dbid['notion_char'] == 's':
                stencil_service = StencilService()
                challenges_array.extend(stencil_service.translate_stencil_tasks(results))
            elif dbid['notion_char'] == 'e':
                epics_service = EpicsService()
                challenges_array.extend(epics_service.translate_epics_tasks(results))
            else:
                print(f"❌❌|WTF? {dbid['notion_char']}? as notion_char wrong parameter")
            break #TODO: quitar esta madre
        #reorder based on due property
        reorder_challenge = sorted(challenges_array, key=lambda x: x['due'])
        todoist_service = TodoistService()
        tasks = []
        for challenge in reorder_challenge:
            seven_days = datetime.today() + timedelta(days=7)
            priority = 1
            heading = '*PROXIMAMENTE|*'
            status = challenge['status']
            daysoff = abs((datetime.strptime(challenge['due'], '%Y-%m-%d') - datetime.strptime(today_str, '%Y-%m-%d')).days)
            if challenge['due'] < today_str:
                priority = 4
                heading = '*VENCIDO|*'
                description = f'Ya se te pasó por *{daysoff}* días y aún está en _{status}_'
            elif challenge['due'] <= seven_days.strftime('%Y-%m-%d'):
                priority = 3
                description = f'Within *7 Days!* And Be Kind, Rewind!'
            else:
                priority = 2
                description = f'*{daysoff} Days!* is close, try to start'
            print(priority, challenge['name'], challenge['due'])
            due_date = challenge['due'] if challenge['due'] < today_str else today_str
            tasks.append(todoist_service.add_task(TODOIST_PID_INB, { "content": heading + challenge['name']
                                                                    , "due_date": due_date
                                                                    , "priority": priority
                                                                    , "description": description
                                                                    , "section_id": None, "labels": None}))
            if challenge['due'] >= today_str:
                tasks.append(todoist_service.add_task(TODOIST_PID_CAL, { "content": challenge['name']
                                                                        , "due_date": challenge['due']
                                                                        , "priority": 1
                                                                        , "description": f'was *deadlined⌛️* on {today_str}'
                                                                        , "section_id": None, "labels": None}))
        return {'challenges': reorder_challenge, 'tasks_created': tasks}
    
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
                high_gods = notion_service.get_characters_by_property('status', 'high')
                if len(high_gods) == 0:
                    npc_characters = notion_service.get_characters_by_deep_level(deep_level='l2', is_npc=True)
                    high_gods = [c for c in npc_characters if c['status'] == 'high']
                god_support = random.choice(high_gods) if high_gods else None
                self.add_encounter_log(god_support['level'], "level",'powered⚡️by⚡️{}'.format(god_support['name']))
                for vs in adventure['vs']:
                    enemies.append(notion_service.get_character_by_id(vs['id']))
                if self.execute_encounter(who, enemies, god_support) is True:
                    who['xp'] += self.add_encounter_log(adventure['xpRwd'],"xp","Adventure XP earned")
                    god_support['xp'] += adventure['xpRwd']
                    god_support['sanity'] += adventure['xpRwd']
                    how_much = (random.randint(1, 50) / 100)
                    send_coins = how_much * adventure['coinRwd']
                    keep_coins = adventure['coinRwd'] - send_coins
                    who['coins'] += self.add_encounter_log(keep_coins,"coins","Adventure 💵 earned (out of {})".format(adventure['coinRwd']))
                    self.add_encounter_log(send_coins, "coins", '🎉 Thanks for the {}% donation [{}/{}]'.format(how_much * 100, send_coins, keep_coins))
                    self.distribute_tribute(who['alter_ego'], send_coins) 
                    adventure['status'] = 'won'
                    # logic for random creation of underworld for dead enemy
                    if random.randint(0, 2) % 3 == 0:
                        random_enemy = random.choice(enemies)
                        if random_enemy['hp'] < 0:
                            self.create_adventure(random_enemy['id'], underworld=True)
                else:
                    new_adventure = self.create_adventure(who['id'], underworld=True)
                    self.add_encounter_log(who['hp'], "hp", '‼️You lost the Adventure‼️')
                    new_adv = notion_service.get_adventure_by_id(new_adventure['adventure_id'])
                    self.add_encounter_log(0,'new',new_adv['name'] + ' | ' +new_adv['desc'])
                    adventure['status'] = 'lost'
            if "discovery" in adventure['path']:
                real_characters = notion_service.get_characters_by_deep_level(deep_level='l0', is_npc=True) + notion_service.get_characters_by_deep_level(deep_level='l1', is_npc=True)
                total_taken = 0
                for character in real_characters:
                    rand_pct = random.randint(1, 25) / 100
                    taken = round(character['coins'] * rand_pct)
                    character['coins'] -= taken
                    total_taken += taken
                    enemies.append(character)
                    self.add_encounter_log(taken*-1,'coins','{} off {}%'.format(character['name'],rand_pct*100))
                who['coins'] += self.add_encounter_log(total_taken,"coins","You have found 💰💰💰 of real 🌎")
            enemies.append(who)
            adventure['encounter_log'] = self.encounter_log
            notion_service.persist_adventure(adventure=adventure, characters=enemies)
        return {
            "adventure_id": adventure_id,
            "status": adventure['status'],
            "who_name": who['name'] if who['name'] else adventure['who'],
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
            damage = 0
            if random.randint(0, 1) % 2 == 0: #Magic Attack
                whopts = who['magic'] + god['magic'] + random.randint(1, self.dice_size)
                enemypts = enemy['magic'] + random.randint(1, self.dice_size)
            else: #Physical Attack
                whopts = who['attack'] + god['attack'] + random.randint(1, self.dice_size)
                enemypts = enemy['defense'] + random.randint(1, self.dice_size)
            damage = whopts - enemypts
            if random.randint(0, 2) % 3 != 0: #aimed attack
                enemy['hp'] += self.add_encounter_log(damage*-1 if damage > 0 else 0, "hp", 'R{} | You aimed your attack.'.format(rounds))
            else:
                self.add_encounter_log(damage*-1 if damage > 0 else 0, "hp", 'R{} | You missed your attack.'.format(rounds))
            if random.randint(0, 1) % 2 == 0: #Magic Defense
                enemypts = enemy['magic'] + random.randint(1, self.dice_size) + (enemy['magic'] if random.randint(0, 3) % 4 == 0 else 0 )
                whopts = who['magic'] + god['magic'] + random.randint(1, self.dice_size)
            else: #Physical Defense
                enemypts = enemy['attack'] + random.randint(1, self.dice_size) 
                whopts = who['defense'] + god['defense'] + random.randint(1, self.dice_size)
            damage = enemypts - whopts
            #print(damage, enemy['name'])
            if random.randint(0, 2) % 3 != 0: #aimed defense
                who['hp'] += self.add_encounter_log(damage*-1 if damage > 0 else 0, "hp", 'R{} | Enemy aimed the attack.'.format(rounds))
            else:
                self.add_encounter_log(damage*-1 , "hp", 'R{} | Enemy missed the attack.'.format(rounds))
        if who['hp'] <= 0:
                self.add_encounter_log(who['hp'], "hp", 'You have been defeated by the enemy.')
                enemy['xp'] += self.steal_property(loser=who, winner=enemy)
                return False
        if enemy['hp'] <= 0:
                self.add_encounter_log(who['hp'], "hp", 'You have defeated the enemy. ({}HP)'.format(enemy['hp']))
                who['xp'] += self.steal_property(loser=enemy, winner=who)
                return True
        return False

    def fight_w_death(self, who, enemy, xpReward):
        rounds = 0
        was_too_much = False
        self.add_encounter_log(0,"","Encountered with {}.".format(str(enemy['name']).upper()))
        while who['hp'] <= 0 and not was_too_much:
            rounds += 1
            versus = ''
            if random.randint(0, 1) % 2 == 0: #Magic Defense
                damage = enemy['magic'] + random.randint(1, self.dice_size) - who['magic'] - random.randint(1, self.dice_size)
                versus = '🪄:{}vs{}={}'.format(enemy['magic'], who['magic'], damage)
            else: #Physical Defense
                damage = enemy['attack'] + random.randint(1, self.dice_size) - who['defense'] - random.randint(1, self.dice_size)
                versus = '🛡️:{}vs{}={}'.format(enemy['attack'], who['defense'], damage)
            if damage > 0: 
                who['hp'] += self.add_encounter_log(damage, "hp", 'R{} | Enemy aimed {}'.format(rounds, versus))
                enemy['hp'] -= damage
                who['xp'] += self.add_encounter_log(xpReward, "xp", '{} got '.format(who['name']) )
                enemy['xp'] += self.add_encounter_log(xpReward, "xp", '{} got '.format(enemy['name']) )
                lucky_exchange = random.randint(0, 4) % 4
                if lucky_exchange == 0:
                    who['magic'] += self.add_encounter_log(enemy['magic'] * 0.1, 'magic', '🍀{}🍀'.format(who['name']))
                    enemy['magic'] += self.add_encounter_log(who['magic'] * 0.1, 'magic', '🍀{}🍀'.format(enemy['name']))
                elif lucky_exchange == 1:
                    who['attack'] += self.add_encounter_log(enemy['attack'] * 0.1, 'attack', '🍀{}🍀'.format(who['name']))
                    enemy['attack'] += self.add_encounter_log(who['attack'] * 0.1, 'attack', '🍀{}🍀'.format(enemy['name']))
                elif lucky_exchange == 2:
                    who['defense'] += self.add_encounter_log(enemy['defense'] * 0.1, 'defense', '🍀{}🍀'.format(who['name']))
                    enemy['defense'] += self.add_encounter_log(who['defense'] * 0.1, 'defense', '🍀{}🍀'.format(enemy['name']))
            was_too_much = rounds >= 100
        return True

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
        transfer = round(percentage * loser[property_value])
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
        upd_character = None
        try:
            if alter_ego['alter_ego']:
                how_much = (random.randint(1, 50) / 100)
                send_coins = how_much * coins
                keep_coins = coins - send_coins
                self.add_encounter_log(send_coins, "coins", '🎉 Thanks for the {}% donation [{}/{}] | {}'.format(how_much * 100, send_coins, keep_coins, alter_ego['name']))
                self.distribute_tribute(alter_ego['alter_ego'], send_coins)
            alter_ego['coins'] += self.add_encounter_log(keep_coins,"coins","⚡️{}⚡️{}⚡️ tribute 💵 earned w/o doing a 💩".format(alter_ego['deep_level'],alter_ego['name']))
            alter_ego['xp'] += 10
            alter_ego['level'] += 1 if alter_ego['xp'] >= alter_ego['max_xp'] else 0
            datau = {"properties": { "coins": {"number": alter_ego['coins']} 
                                    , "xp": {"number": alter_ego['xp']}  
                                    , "level": {"number": alter_ego['level']} }  }
            upd_character = notion_service.update_character(alter_ego, datau)
        except Exception as e:
            print("Error distributing tribute:", e.__traceback__)
        return upd_character

    def create_underworld_4_deadpeople(self):
        notion_service = NotionService() 
        characters_dead = notion_service.get_characters_by_property('status', 'dead')
        l3_characters = [c for c in characters_dead if c['deep_level'] == 'l3']  
        if len(l3_characters) <= 0:
            l3_characters = notion_service.get_characters_by_deep_level(deep_level='l3', is_npc=False) 
            l3_characters += notion_service.get_characters_by_deep_level(deep_level='l3', is_npc=True)
        filtered_characters = [c for c in l3_characters if c['status'] == 'dead']  
        dead_people_count = len(filtered_characters)
        filtered_characters =  [c for c in filtered_characters if c['pending_reborn'] is None]   
        to_execute = 0
        if len(filtered_characters) <= 5:
            to_execute = len(filtered_characters)
        else:
            to_execute = random.randint(1, int(len(filtered_characters) * self.percentage_habits))
        sample_characters = random.sample(filtered_characters, min( to_execute, len(filtered_characters)))
        done = 1
        return_array = []
        for character in sample_characters:
            print("💀 underworld for "+character['name'],' | {}/{} [{}]'.format(done, len(sample_characters), len(filtered_characters)))
            adventure = self.create_adventure(character['id'], underworld=True, notion_service=notion_service )
            return_array.append({"adventure_id": adventure['adventure_id']
                                , "character_id": character['id']
                                , "character_name": character['name']})
            #time.sleep(random.randint(1, 5))
            done += 1
        return return_array, dead_people_count
    
    def execute_underworld(self):
        notion_service = NotionService() 
        return_array = []
        all_adventures = notion_service.get_underworld_adventures()
        if len(all_adventures) <= 0:
            print("no underworld adventures")
            return return_array
        to_execute = 0
        if len(all_adventures) <= 5:
            to_execute = len(all_adventures)
        else:
            to_execute = random.randint(1, int(len(all_adventures) * self.percentage_habits))
        sample_adventures = random.sample(all_adventures, min(to_execute, len(all_adventures)))
        done = 1
        dead_gods_pool = []
        for deaadventure in sample_adventures:
            self.encounter_log = []
            enemy = None
            who = notion_service.get_character_by_id(deaadventure['who'])
            print("underworld exec "+deaadventure['name']+"|"+who['name'],'| {}/{} [{}]'.format(done, len(sample_adventures), len(all_adventures)))
            for vs in deaadventure['vs']:
                if vs['id'].replace('-','') in dead_gods_pool:
                    dead_gods_pool = []
                enemy = notion_service.get_character_by_id(vs['id'])
                dead_gods_pool.append(enemy['id'])
            if self.fight_w_death(who, enemy, abs(deaadventure['xpRwd'])) is True:
                # alternative wins for the 🧟 
                who['respawn'] += self.add_encounter_log(1, "respawn", 'It🧟is🧟alive w{}'.format(who['hp']))
                who['hp'] += self.add_encounter_log(who['hours_recovered'], "hp", 'hours recovered as')
                properties = ['magic', 'attack', 'defense']
                total = 0
                prev_value = 100000000
                minor_prop = ''
                for prop in properties:
                    value = who[prop]
                    total += value
                    if value < prev_value:
                        minor_prop = prop
                        prev_value = value
                average_properties = total / len(properties)
                who[minor_prop] += self.add_encounter_log(average_properties, minor_prop, 'Engaging the weakest property')
                deaadventure['status'] = 'won'
                deaadventure['encounter_log'] = self.encounter_log
                notion_service.persist_adventure(adventure=deaadventure, characters=[who,enemy])
                time.sleep(random.randint(1, 5))
            return_array.append({"adventure_id": deaadventure['id'], "character_id": who['id'], "character_name": who['name'], "deadgod_name": enemy['name'],"adventure_status": deaadventure['status']})
            done += 1
        return return_array

    def awake_characters(self):
        notion_service = NotionService() 
        characters = notion_service.get_characters_by_property('status', 'rest')
        characters += notion_service.get_characters_by_property('status', 'dying')
        l3_characters = [c for c in characters if c['deep_level'] == 'l3']  
        if len(l3_characters) <= 0:
            l3_characters = notion_service.get_characters_by_deep_level(deep_level='l3', is_npc=False) 
            l3_characters += notion_service.get_characters_by_deep_level(deep_level='l3', is_npc=True)
        filtered_characters = [c for c in l3_characters if c['status'] == 'rest' or c['status'] == 'dying']
        return_array = []
        for character in filtered_characters:
            pct_before = character['hp'] / character['max_hp']
            pct_after = (character['hp'] + character['hours_recovered']) / character['max_hp']
            if pct_after > 0.3:
                character['hp'] += character['hours_recovered']
                character['status'] = 'alive'
                datau = {"properties": { "hp": {"number": character['hp']},"status": {"select": {"name":character['status']} } }}
                upd_character = notion_service.update_character(character, datau)
                return_array.append({ "character_id": character['id'], "character_name": character['name'], "character_hp": character['hp']})
                print(character['hours_recovered'],character['name'],'{}->{} awakening'.format(pct_before,pct_after))
        return return_array
    
    def apply_punishment(self):
        notion_service = NotionService() 
        return_array = []
        all_adventures = notion_service.get_punishment_adventures()
        if len(all_adventures) <= 0:
            print("no punishment adventures")
            return return_array
        for adventure in all_adventures:
            self.encounter_log = []
            character = notion_service.get_character_by_id(adventure['who'])
            character['xp'] += self.add_encounter_log(adventure['xpRwd'], 'xp', '{} has decreased by'.format(character['name']))
            habit_id = adventure['habits'][0]
            habit = notion_service.get_habit_by_id(habit_id['id'])
            habit['xp'] += self.add_encounter_log(adventure['xpRwd'], 'xp', '{} has decreased by'.format(habit['name']))
            adventure['status'] = 'lost'
            adventure['encounter_log'] = self.encounter_log
            notion_service.persist_habit(habit)
            notion_service.persist_adventure(adventure=adventure, characters=[character])
            return_array.append({"adventure_id": adventure['id'], "character_id": character['id'], "character_name": character['name'],"adventure_status": adventure['status']})
        return return_array