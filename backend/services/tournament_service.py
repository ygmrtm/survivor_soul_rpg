import datetime 
import random

from backend.services.notion_service import NotionService
from backend.services.redis_service import RedisService


class TournamentService:
    GOLDEN_RATIO = 1.618033988749895
    dice_size = 16
    notion_service = NotionService()
    redis_service = RedisService()
    encounter_log = []
    #max_xp = 500
    #max_hp = 100
    #max_sanity = 60    
    #max_prop_limit = 20
    max_xprwd = 4
    max_coinrwd = 10    


    def create_tournament(self, title, description):
        gods = self.notion_service.get_characters_by_deep_level(deep_level='l0', is_npc=True)
        character = gods[0] if len(gods[0]) > 0 else None
        tournament = None
        if character is not None:
            character_level = character['level']
            max_xprwd = self.max_xprwd
            max_coinrwd = self.max_coinrwd
            
            for i in range(character_level):
                max_xprwd *= self.GOLDEN_RATIO
                max_coinrwd *= self.GOLDEN_RATIO
            xp_reward = random.randint(1, max_xprwd)
            coin_reward = random.randint(1, max_coinrwd)      

            tournament = self.notion_service.create_tournament(character_id=character['id']
                                                            , xp_reward=xp_reward, coin_reward=coin_reward
                                                            , title=title , description=description)  
            print("tournament | ", tournament)
        return tournament
    
    def get_by_id(self, tournament_id):
        try:
            adventure = None
            adventure = self.redis_service.get(self.redis_service.get_cache_key("tournaments", tournament_id))
            if not adventure:
                adventure = self.notion_service.get_adventure_by_id(tournament_id)
                hours = abs(datetime.datetime.now() - datetime.datetime.fromisoformat(adventure['due'])).total_seconds() / 3600
                self.redis_service.set_with_expiry(self.redis_service.get_cache_key("tournaments", tournament_id)
                                                    ,adventure, expiry_hours=hours)
            return adventure
        except Exception as e:
            print(f"Failed to fetch get_by_id {tournament_id} ::: {e}")
            raise

    def get_all_open_tournaments(self):
        try:
            tournaments = []
            tournaments = self.notion_service.get_all_open_tournaments()
            for tournament in tournaments:
                tournament_id = tournament['id']
                if not self.redis_service.get(self.redis_service.get_cache_key("tournaments", tournament_id)):
                    hours = abs(datetime.datetime.now() - datetime.datetime.fromisoformat(tournament['due'])).total_seconds() / 3600
                    self.redis_service.set_with_expiry(self.redis_service.get_cache_key("tournaments", tournament_id)
                                                        ,tournament, expiry_hours=hours)
            return tournaments
        except Exception as e:
            print(f"Failed to fetch get_all_open_tournaments ::: {e}")
            raise        

    def evaluate_all_tournaments(self, full_hp=True):
        try:
            tournaments = self.get_all_open_tournaments()
            for tournament in tournaments:
                l3_characters = self.notion_service.get_characters_by_deep_level(deep_level='l3', is_npc=True)        
                l3_characters += self.notion_service.get_characters_by_deep_level(deep_level='l3', is_npc=False)        
                self.encounter_log = []
                whos = []
                print(f"🏟️ {tournament['name']} | {tournament['desc']}")
                if 'l.c.s.' in tournament['path']:
                    whos = self.last_cryptid_stand(l3_characters=l3_characters, full_hp=full_hp)
                elif 'g.v.c.' in tournament['path']:
                    l2_gods = self.notion_service.get_characters_by_deep_level(deep_level='l2', is_npc=True)
                    alive_cryptids = self.redis_service.query_characters('status','alive')
                    l3_cryptids = [c for c in alive_cryptids if c['deep_level'] == 'l3' ]
                    whos = self.gods_v_cryptids(gods=l2_gods, cryptids=l3_cryptids, full_hp=full_hp)
                else:
                    raise ValueError("Invalid tournament path")
                tournament['who'] = None #Forcing to take the Who from Characters Array / Or Root
                tournament['status'] = 'won'
                tournament['encounter_log'] = self.encounter_log
                tournament['top_5'] = whos
                hours = abs(datetime.datetime.now() - datetime.datetime.fromisoformat(tournament['due'])).total_seconds() / 3600
                self.notion_service.persist_adventure(adventure=tournament, characters=whos)
                self.redis_service.set_with_expiry(self.redis_service.get_cache_key("tournaments", tournament['id'])
                                                                        ,tournament, expiry_hours=hours)
            remainOpen = len(self.get_all_open_tournaments())
            return {"tournaments":tournaments, "still_not_executed":remainOpen }
        except Exception as e:
            print(f"Failed to fetch evaluate_all_tournaments ::: {e}")
            raise     

    def last_cryptid_stand(self, l3_characters, full_hp ):
        cemetery = []
        fights = 0
        alive_characters = [c for c in l3_characters if c['status'] == 'alive']
        if full_hp is True:
            alive_characters = [c for c in alive_characters if c['hp'] >= c['max_hp']]
        random.shuffle(alive_characters)
        #print("🔔 Duplicates",self.check_for_duplicates(alive_characters))
        charLead = None
        charReta = None
        for character in alive_characters:
            if charLead is not None:
                charReta = character
                charLead, charDefeated = self.fight(charLead, charReta)
                charLead['hp'] = charLead['max_hp'] # semilla del ermitaño
                fights += 1
                cemetery.append(charDefeated)
            else:
                charLead = character
        self.add_encounter_log(fights, 'fights', f'Tournament fights')
        self.add_encounter_log(len(alive_characters), 'alive'
                            , f"L3 Characters Alive {'w Full HP' if full_hp is True else ''}")
        #for cem in cemetery:
        #    print(f"🪦 {cem['name']} hp:{cem['hp']}")
        # get the last 4 elements of cemetery + lead = TOP 5 characters
        return [charLead] + (cemetery[-4:] if len(cemetery) >= 4 else cemetery)

    def gods_v_cryptids(self, gods=[], cryptids=[], full_hp=False):
        cemetery = { 'gods':[], 'cryptids':[]}
        fights = 0
        god = None
        cry = None
        alive_criptids = [c for c in cryptids if c['status'] == 'alive']
        if full_hp is True:
            alive_criptids = [c for c in alive_criptids if c['hp'] >= c['max_hp']]
        random.shuffle(alive_criptids)
        random.shuffle(gods)
        #print("🔔 Duplicates:",self.check_for_duplicates(alive_criptids),len(alive_criptids))
        #print("🚨 Duplicates:",self.check_for_duplicates(gods),len(gods))
        self.add_encounter_log(max(len(gods), len(alive_criptids)), 'fights', f"Gods:{len(gods)} v Cryptids:{len(alive_criptids)} alive {full_hp}")
        while len(gods) > 0 and len(alive_criptids) > 0 :
            fights += 1
            god = gods.pop(0)
            cry = alive_criptids.pop(0)
            winner, looser, god_or_cry = self.fight_gods(god, cry)
            self.add_encounter_log(fights, '#fight#', f"[{winner['description']}] vs [{looser['description']}]")
            if god_or_cry == 'g':
                gods.append(god)
                cemetery['cryptids'].append(looser)
            else:
                alive_criptids.append(cry)
                cemetery['gods'].append(looser)
        self.add_encounter_log(fights, '+total', f'Tournament fights')
        self.add_encounter_log(fights, '+winner', winner['description'])
        print(f"🪦🚨 size {len(cemetery['gods'])} | {len(gods)} left alive")
        #for cem in cemetery['gods']:
        #    print(f"🪦🚨 {cem['name']} hp:{cem['hp']}")
        print(f"🪦🔔 size {len(cemetery['cryptids'])} | {len(alive_criptids)} left alive")
        #for cem in cemetery['cryptids']:
        #    print(f"🪦🔔 {cem['name']} hp:{cem['hp']}")
        return [winner] \
            + (cemetery['cryptids'][-2:] if len(cemetery['cryptids'][-2:]) >= 2 else cemetery['cryptids']) \
            + (cemetery['gods'][-2:] if len(cemetery['gods'][-2:]) >= 2 else cemetery['gods']) 
    
    def check_for_duplicates(self, characters):
        duplicates = []
        for i in range(len(characters)):
            for j in range(i+1, len(characters)):
                if characters[i]['name'] == characters[j]['name']:
                    duplicates.append(characters[i])
        return duplicates
    
    def fight_gods(self, god, cryptid):
        # print("😇'⚔️🗺️",god['name'], cryptid['name'])
        character_level = max(god['level'], cryptid['level'] )
        god['hp'] = abs(god['hp']) # handle death gods
        max_xprwd = self.max_xprwd
        for i in range(character_level):
            max_xprwd *= self.GOLDEN_RATIO
        xp_reward = random.randint(1, max_xprwd)
        rounds = 0
        while god['hp'] > 0 and cryptid['hp'] > 0:
            rounds += 1
            damage = 0
            # Gods attack
            m_godpts = god['magic'] + random.randint(1, self.dice_size)
            m_cryptidpts = cryptid['magic'] + random.randint(1, self.dice_size)
            p_godpts = god['attack'] + random.randint(1, self.dice_size)
            p_cryptidpts = cryptid['defense'] + random.randint(1, self.dice_size)
            damage = (p_godpts - p_cryptidpts) + (m_godpts - m_cryptidpts)
            if random.randint(0, 2) % 3 != 0 : #aimed attack
                cryptid['hp'] -= damage if damage > 0 else 0
            # Cryptid attack
            m_cryptidpts = cryptid['magic'] + random.randint(1, self.dice_size) 
            m_godpts = god['magic'] + random.randint(1, self.dice_size)
            p_cryptidpts = cryptid['attack'] + random.randint(1, self.dice_size) 
            p_godpts = god['defense'] + random.randint(1, self.dice_size)
            damage = (m_cryptidpts - m_godpts) + (p_cryptidpts - p_godpts)
            if random.randint(0, 2) % 3 != 0 : #aimed attack
                god['hp'] -= damage if damage > 0 else 0
        winner = cryptid if cryptid['hp'] > 0 else god
        looser = cryptid if cryptid['hp'] <= 0 else god
        rounds_rwd = xp_reward if rounds > xp_reward else rounds
        looser['xp'] += (rounds_rwd + xp_reward)
        looser['description'] = f"{looser['name']} | L{looser['level']} | X{looser['xp']} | 🫀{looser['hp']} | 🧠{looser['sanity']}"
        #self.add_encounter_log(points=rounds_rwd, type="xp" , why=f"{winner['name']} defeated {looser['name']} in {rounds} rounds")
        winner['xp'] += (rounds_rwd + xp_reward)
        winner['description'] = f"{winner['name']} | L{winner['level']} | X{winner['xp']} | 🫀{winner['hp']} | 🧠{winner['sanity']}"
        winner['hp'] = winner['max_hp'] # semilla del ermitaño
        god['hp'] = (god['hp']*-1) if god['hp'] > 0 and god['status'] == 'dead' else god['hp'] # handle death gods
        #print(f"w-> {winner['name']} xp:{winner['xp']} hp:{winner['hp']}")
        #print(f"l-> {looser['name']} xp:{looser['xp']} hp:{looser['hp']}")
        return winner, looser, 'c' if cryptid['hp'] > 0 else 'g'
    
    def fight(self, who, enemy):
        character_level = who['level']
        max_xprwd = self.max_xprwd
        for i in range(character_level):
            max_xprwd *= self.GOLDEN_RATIO
        xp_reward = random.randint(1, max_xprwd)
        rounds = 0
        while who['hp'] > 0 and enemy['hp'] > 0:
            rounds += 1
            damage = 0
            if random.randint(0, 1) % 2 == 0: #Magic Attack
                whopts = who['magic'] + random.randint(1, self.dice_size)
                enemypts = enemy['magic'] + random.randint(1, self.dice_size)
            else: #Physical Attack
                whopts = who['attack'] + random.randint(1, self.dice_size)
                enemypts = enemy['defense'] + random.randint(1, self.dice_size)
            damage = whopts - enemypts
            enemy['hp'] += (damage*-1) if random.randint(0, 2) % 3 != 0 else 0 #aimed attack
            if random.randint(0, 1) % 2 == 0: #Magic Defense
                enemypts = enemy['magic'] + random.randint(1, self.dice_size) 
                whopts = who['magic'] + random.randint(1, self.dice_size)
            else: #Physical Defense
                enemypts = enemy['attack'] + random.randint(1, self.dice_size) 
                whopts = who['defense'] + random.randint(1, self.dice_size)
            damage = enemypts - whopts
            who['hp'] += (damage*-1) if random.randint(0, 2) % 3 != 0 else 0 #aimed attack
        winner = who if who['hp'] > 0 else enemy
        looser = who if who['hp'] < 0 else enemy
        rounds_rwd = xp_reward if rounds > xp_reward else rounds
        looser['xp'] += (rounds_rwd + xp_reward)
        looser['description'] = f"{looser['name']} | L{looser['level']} | X{looser['xp']} | 🫀{looser['hp']} | 🧠{looser['sanity']}"
        #self.add_encounter_log(points=rounds_rwd, type="xp", why=f"{winner['name']} defeated {looser['name']} in {rounds} rounds")
        winner['xp'] += (rounds_rwd + xp_reward)
        winner['description'] = f"{winner['name']} | L{winner['level']} | X{winner['xp']} | 🫀{winner['hp']} | 🧠{winner['sanity']}"
        #print(f"-> {winner['name']} xp:{winner['xp']} hp:{winner['hp']}")
        return winner, looser 
    
    def add_encounter_log(self, points, type, why):
        # print("add_encounter_log",points, type, why)
        self.encounter_log.append({
            "time": datetime.datetime.today().isoformat(),
            "points": points,
            "type": str(type).upper() if type else "",
            "why": why
        })
        return points    