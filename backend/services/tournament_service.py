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
            xp_reward = random.randint(1, round(max_xprwd))
            coin_reward = random.randint(1, round(max_coinrwd))      

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
                elif 'r.v.w.' in tournament['path']:
                    root = self.notion_service.get_characters_by_deep_level(deep_level='l0', is_npc=True)[0]
                    l2_gods = self.notion_service.get_characters_by_deep_level(deep_level='l2', is_npc=True)
                    sorted_items = sorted(l2_gods, key=lambda x: (x['level'], x['xp']))
                    the_top_ten = sorted_items[-10:]
                    the_last_six = sorted_items[:6]
                    sample_gods = random.sample(the_top_ten, min( 6, len(the_top_ten))) + [random.choice(the_last_six)]
                    alive_cryptids = self.redis_service.query_characters('status','alive')
                    l3_cryptids = [c for c in alive_cryptids if c['deep_level'] == 'l3' ]
                    whos = self.root_gods_v_cryptids(root=root, gods=sample_gods, cryptids=l3_cryptids)
                    #for x in whos:
                    #    print(x['name'],x['xp'],x['hp'])
                else:
                    raise ValueError("Invalid tournament path")
                whos[0]['xp'] += self.add_encounter_log(tournament['xpRwd'], 'xp',f"{whos[0]['name']} won tournament reward")
                whos[0]['coins'] += self.add_encounter_log(tournament['coinRwd'], 'coins',f"{whos[0]['name']} won tournament reward")
                tournament['who'] = None #Forcing to take the Who from Characters Array / Or Root
                tournament['status'] = 'won'
                tournament['encounter_log'] = self.encounter_log
                tournament['top_5'] = whos
                hours = abs(datetime.datetime.now() - datetime.datetime.fromisoformat(tournament['due'])).total_seconds() / 3600
                #print(self.encounter_log)
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
    
    def root_gods_v_cryptids(self, root=None, gods=[], cryptids=[]):
        need_update = []
        teams_fighted = 0
        random.shuffle(cryptids)
        teamup_members = self.redis_service.get(self.redis_service.get_cache_key('num83r5','teamup_members'))
        teamup_members = 2 if not teamup_members else teamup_members
        self.add_encounter_log(0, 'fights', f"Root+Gods:{len(gods)} v Cryptids:{len(cryptids)} alive")
        total_reward = 0
        while len(gods) > 0 and len(cryptids) > 0 :
            team = []
            teams_fighted += 1
            if teamup_members < len(cryptids):
                for i in range(teamup_members):
                    team.append(cryptids.pop(0))
            else:
                team = cryptids
            god = gods.pop(0)
            self.add_encounter_log(teams_fighted,"#fight#",f"{root['name']} and {god['name']}|{god['hp']}🫀 vs [{len(team)}:cryptids]")
            winner, rounds_rwd, gods_bleed, untouchable_c = self.fight_root(root, god, team)
            total_reward += rounds_rwd
            self.add_encounter_log(rounds_rwd, '#reward#', f"added to the pot [{total_reward}]")
            if winner == 'root':
                gods.append(god)
                if gods_bleed is False:
                    teamup_members += 1 
                    self.add_encounter_log(teamup_members, 'TM', 'Team Members Level Up')
            else:
                which_one = random.randint(0, 2) % 3
                if which_one == 0:
                    root['attack'] += (god['attack'] * 0.4)
                elif which_one == 1:
                    root['defense'] += (god['defense'] * 0.4)
                elif which_one == 2:
                    root['magic'] += (god['magic'] * 0.4)
                god['xp'] += rounds_rwd
                for cry in team:
                    cry['xp'] += rounds_rwd
                need_update.append(god)
                need_update.extend(team)
                if untouchable_c is True:
                    teamup_members -= (0 if teamup_members <= 1 else 1)  
                    self.add_encounter_log(teamup_members, 'TM', 'Team Members Lowering Down')
            cryptids.extend([c for c in team if c['hp'] > 0 ])
        self.add_encounter_log(teams_fighted, '+total+', f'Teams fought Root w Gods')
        if len(gods) <= 0: # Winners the Cryptids then 1:1 with root
            self.add_encounter_log(self.GOLDEN_RATIO, '1:1', f"{len(cryptids)} Cryptids vs Root|{root['hp']}🫀")
            while len(cryptids) > 0 and root['hp'] >= 0:
                cryp = cryptids.pop(0)
                winner, looser = self.fight(root, cryp)
            need_update.append(looser)
        else:
            winner = root
        winner['xp'] += total_reward
        self.add_encounter_log(total_reward, 'winner', f"final pot got by {winner['name'].upper()}|{winner['hp']}🫀 ")
        for dude in need_update:
            dude['xp'] += (total_reward / len(need_update))
        self.redis_service.set_without_expiry(self.redis_service.get_cache_key('num83r5','teamup_members'),teamup_members)
        return [winner] + need_update


    def check_for_duplicates(self, characters):
        duplicates = []
        for i in range(len(characters)):
            for j in range(i+1, len(characters)):
                if characters[i]['name'] == characters[j]['name']:
                    duplicates.append(characters[i])
        return duplicates
    
    def fight_root(self,root, god, team):
        # print("🌳 ",root['name'],god['name'], len(team),team[0]['name'])
        character_level = min(god['level'], root['level'] )
        god['hp'] = abs(god['hp']) # handle death gods
        max_xprwd = self.max_xprwd
        for i in range(character_level):
            max_xprwd *= self.GOLDEN_RATIO
        xp_reward = random.randint(1, round(max_xprwd))
        rounds = 0
        gods_bleed = False
        untouchable_c = True
        while god['hp'] > 0 and len(team) > 0:
            rounds += 1
            damage = 0
            # Cryptid attack
            m_cryptidpts = sum(c['magic'] + random.randint(1, self.dice_size) for c in team)
            m_godpts = root['magic'] + god['magic'] + random.randint(1, self.dice_size)
            p_cryptidpts = sum(c['attack'] + random.randint(1, self.dice_size) for c in team)
            p_godpts = root['defense'] + god['defense'] + random.randint(1, self.dice_size)
            damage = (m_cryptidpts - m_godpts) + (p_cryptidpts - p_godpts)
            if random.randint(0, 2) % 3 != 0 : #aimed attack
                god['hp'] -= damage if damage > 0 else 0
                gods_bleed = True
            # Gods attack
            m_godpts = root['magic'] + god['magic'] + random.randint(1, self.dice_size)
            m_cryptidpts = sum(c['magic'] + random.randint(1, self.dice_size) for c in team)
            p_godpts = root['attack'] + god['attack'] + random.randint(1, self.dice_size)
            p_cryptidpts = sum(c['defense'] + random.randint(1, self.dice_size) for c in team)
            damage = (p_godpts - p_cryptidpts) + (m_godpts - m_cryptidpts)
            if random.randint(0, 2) % 3 != 0 and damage > 0: #aimed attack
                untouchable_c = False
                for cry in team:
                    cry['hp'] -= (damage / len(team))
                    if cry['hp'] < 0:
                        team.remove(cry)
        rounds_rwd = xp_reward if rounds > xp_reward else rounds
        winner = 'team' if god['hp'] <= 0 else 'root'
        god['hp'] = (god['hp']*-1) if god['hp'] > 0 and god['status'] == 'dead' else god['hp'] # handle death gods
        return winner, rounds_rwd, gods_bleed, untouchable_c

    def fight_gods(self, god, cryptid):
        # print("😇'⚔️🗺️",god['name'], cryptid['name'])
        character_level = max(god['level'], cryptid['level'] )
        god['hp'] = abs(god['hp']) # handle death gods
        max_xprwd = self.max_xprwd
        for i in range(character_level):
            max_xprwd *= self.GOLDEN_RATIO
        xp_reward = random.randint(1, round(max_xprwd))
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
        xp_reward = random.randint(1, round(max_xprwd))
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