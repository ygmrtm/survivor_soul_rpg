import datetime 
import random

from backend.services.notion_service import NotionService
from backend.services.redis_service import RedisService


class TournamentService:
    GOLDEN_RATIO = 1.618033988749895
    dice_size = 360
    encounter_log = []
    max_xprwd = 4
    max_coinrwd = 10    
    total_rounds = 500
    expirity_tournament_hours = 12
    percentage_lost = 0.2
    _instance = None

    def __new__(cls):
        """Override __new__ to implement Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(TournamentService, cls).__new__(cls)
        return cls._instance    

    def __init__(self):
        self.notion_service = NotionService()
        self.redis_service = RedisService()


    def create_tournament(self, title, description):
        gods = self.notion_service.get_characters_by_deep_level_npc_source(deep_level='l0', is_npc=True)
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

            tournament = self.notion_service.create_tournament(character_id=character['notionid']
                                                            , xp_reward=xp_reward, coin_reward=coin_reward
                                                            , title=title , description=description)  
            print("tournament for root | ", tournament)
        return tournament
    
    def get_by_id(self, tournament_id, prefix_save_ifnot='adventure'):
        try:
            tournament_id = tournament_id.replace('-','')
            adventure = None
            adventure = self.redis_service.get(prefix_save_ifnot + tournament_id)
            if not adventure:
                adventure = self.notion_service.get_adventure_by_id(tournament_id)
                adventure['id'] = tournament_id
                self.redis_service.set_with_expiry(self.redis_service.get_cache_key(prefix_save_ifnot, tournament_id),adventure, expiry_hours=self.expirity_tournament_hours)
            return adventure
        except Exception as e:
            print(f"Failed to fetch get_by_id {tournament_id} ::: {e}")
            raise

    def count_n_get_by_status(self, status):
        try:
            return self.notion_service.count_n_get_by_status_source(status=status, prefix='tournaments')
        except Exception as e:
            print(f"Failed to fetch count_n_get_by_status ::: {e}")
            raise        

    def evaluate_tournament_by_id(self, tournament_id=None, tournament_obj=None, full_hp=True):
        try:
            tournament = None
            if tournament_id:
                tournament = self.get_by_id(tournament_id)
            elif tournament_obj:
                tournament = tournament_obj
                tournament_id = tournament_obj['id']
            else:
                raise ValueError("🚨 No Tournament ID Provided") 
            if tournament['status'] not in ['created','accepted']:
                return {"tournament":tournament, "message_back":f"🚨 Tournament {tournament_id} is in wrong status {tournament['status']}" }
            self.encounter_log = []
            whos = []
            l3_characters = self.notion_service.get_characters_by_deep_level_status_source(deep_level='l3', status="alive")        
            l2_gods = self.notion_service.get_characters_by_deep_level_npc_source(deep_level='l2', is_npc=True)
            print(f"{tournament['path']} 🏟️ {tournament['name']} 🏟️  {tournament['desc']} 🏟️  {tournament['xpRwd']} reward")
            if 'l.c.s.' in tournament['path']:
                whos = self.last_cryptid_stand(l3_characters=l3_characters, full_hp=full_hp)
                if whos[0] is None:
                    print(f"{tournament['path']} 🏟️ 2nd try now without full power")
                    whos = self.last_cryptid_stand(l3_characters=l3_characters, full_hp = not(full_hp))
            elif 'g.v.c.' in tournament['path']:
                whos = self.gods_v_cryptids(gods=l2_gods, cryptids=l3_characters, full_hp=full_hp)
                if whos[0] is None:
                    print(f"{tournament['path']} 🏟️ 2nd try now without full power")
                    whos = self.gods_v_cryptids(gods=l2_gods, cryptids=l3_characters, full_hp=not(full_hp))
            elif 'r.v.w.' in tournament['path']:
                root = self.notion_service.get_characters_by_deep_level_npc_source(deep_level='l0', is_npc=True)
                sorted_items = sorted(l2_gods, key=lambda x: (x['level'], x['xp']))
                the_top_ten = sorted_items[-10:]
                the_last_six = sorted_items[:6]
                sample_gods = random.sample(the_top_ten, min( 6, len(the_top_ten))) + [random.choice(the_last_six)]
                whos = self.root_gods_v_cryptids(root=root[0], gods=sample_gods, cryptids=l3_characters)
            else:
                raise ValueError("🚨 Invalid tournament path")
            if len(whos) > 1 and whos[0]['description'] != "dummy":
                winners = ''
                for who in whos:
                    who['xp'] += self.add_encounter_log(tournament['xpRwd'], 'xp',f"{who['name']} won tournament reward")
                    who['coins'] += self.add_encounter_log(tournament['coinRwd'], 'coins',f"{who['name']} won tournament reward")
                    self.redis_service.zincrby(self.redis_service.get_cache_key('sets','boardleaders','xp')
                        , tournament['xpRwd']
                        , self.redis_service.get_cache_key('cryptids',who['notionid']))
                    winners += (who['name'] + '| ')
                tournament['who'] = None #Forcing to take the Who from Characters Array / Or Root
                tournament['status'] = 'won'
                tournament['encounter_log'] = self.encounter_log
                tournament['top_5'] = whos
                self.notion_service.persist_adventure(adventure=tournament, characters=whos, prefix='tournaments')
                message_back = f"{tournament['id']} EXECUTED AS {tournament['status']} WINNERS >> {winners} GOT AS REWARD {tournament['xpRwd']} ${tournament['coinRwd']}"
            else:
                message_back = f"NO WINNER"
                
            return {"tournament":tournament, "message_back":message_back }

        except Exception as e:
            print(f"Failed to fetch evaluate_tournaments_by_id {tournament_id} ::: {e}")
            raise    
    
    def evaluate_tournaments_by_status(self, full_hp=True, status='created', limit=10):
        try:
            count, tournaments = self.count_n_get_by_status(status=status)
            if count <= 0:
                return {"tournaments":None, "still_not_executed":0, "actually_executed":0, "message":"Nothing to execute here, there're no Tournaments for "+status}

            actually_executed = 0
            executed_but_lost = 0
            over_percentage = False
            for tournament in tournaments:

                self.encounter_log = []
                response = self.evaluate_tournament_by_id(tournament_obj=tournament, full_hp=full_hp)
                actually_executed += 1
                executed_but_lost += (1 if tournament['status'] != 'won' else 0)
                pct_lost = executed_but_lost/limit
                over_percentage = pct_lost >= self.percentage_lost
                #print(f"{tournament['status']} 🏟️ {tournament['desc']} 🏟️ | {response['message_back']}")
                if actually_executed >= limit or over_percentage:
                    print(f'🚨 {pct_lost} exceeds the threshold {self.percentage_lost} for Lost Tournaments' if over_percentage else '')
                    break

            remainOpen = count - actually_executed + executed_but_lost
            return {"tournaments":tournaments, "still_not_executed":remainOpen, "actually_executed":actually_executed, "message":'done'}

        except Exception as e:
            print(f"Failed to fetch evaluate_all_tournaments ::: {e}")
            raise     

    def last_cryptid_stand(self, l3_characters, full_hp ):
        cemetery = []
        fights = 0
        alive_characters = [c for c in l3_characters if c['status'] == 'alive']
        if full_hp is True:
            full_alive_characters = [c for c in alive_characters if c['hp'] >= c['max_hp']]
            #print(f'🔋 {len(full_alive_characters)} from {len(alive_characters)}')
            alive_characters = full_alive_characters
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
        return [charLead] + (cemetery[-10:] if len(cemetery) >= 10 else cemetery)

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
        winner = { "description": "dummy"}
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
        print(f"gods | 💀 {len(cemetery['gods'])} | {len(gods)} left alive {'🏆' if len(gods)>0 else ''}")
        print(f"cryp | 💀 {len(cemetery['cryptids'])} | {len(alive_criptids)} left alive{'🏆' if len(alive_criptids)>0 else ''}")
        return [winner] \
            + (cemetery['cryptids'][-10:] if len(cemetery['cryptids'][-10:]) >= 10 else cemetery['cryptids']) \
            + (cemetery['gods'][-5:] if len(cemetery['gods'][-5:]) >= 5 else cemetery['gods']) 
    
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
            which_one = random.randint(0, 2) % 3
            if winner == 'root':
                if gods_bleed is False:
                    teamup_members += 1 
                    self.add_encounter_log(teamup_members, 'u⬆️p', 'Team Members Level 🆙')
                if which_one == 0:
                    god['attack'] += (god['attack'] * 0.4)
                elif which_one == 1:
                    god['defense'] += (god['defense'] * 0.4)
                elif which_one == 2:
                    god['magic'] += (god['magic'] * 0.4)
                gods.append(god)
            else:
                if untouchable_c is True:
                    teamup_members -= (0 if teamup_members <= 1 else 1)  
                    self.add_encounter_log(teamup_members, 'do⬇️wn', 'Team Members level lowering Down')
                if which_one == 0:
                    root['attack'] += (god['attack'] * 0.4)
                elif which_one == 1:
                    root['defense'] += (god['defense'] * 0.4)
                elif which_one == 2:
                    root['magic'] += (god['magic'] * 0.4)
                god['xp'] += rounds_rwd
                for cry in team:
                    which_one = random.randint(0, 2) % 3
                    cry['xp'] += rounds_rwd
                    if which_one == 0:
                        cry['attack'] += (god['attack'] * 0.4)
                    elif which_one == 1:
                        cry['defense'] += (god['defense'] * 0.4)
                    elif which_one == 2:
                        cry['magic'] += (god['magic'] * 0.4)                
                need_update.append(god)
                need_update.extend(team)
            cryptids.extend([c for c in team if c['hp'] > 0 ]) ## bringing back survivors
        self.add_encounter_log(teams_fighted, '+total+', f'Teams fought Root w Gods')
        if len(gods) > 0:
            need_update.append(root)
            need_update.extend(gods)
        else:  # Winners the Cryptids then 1:1 with root
            self.add_encounter_log(self.GOLDEN_RATIO, '1:1', f"{len(cryptids)} Cryptids vs Root|{root['hp']}🫀")
            looser = root
            winner = cryptids[0] if len(cryptids) > 0 else root
            while len(cryptids) > 0 and root['hp'] >= 0:
                cryp = cryptids.pop(0)
                winner, looser = self.fight(root, cryp)
            # Handle edge case where loop doesn't execute
            if winner is None or looser is None:
                if len(cryptids) == 0:
                    winner = root
                    looser = root
                elif root['hp'] < 0:
                    winner = cryptids[0] if len(cryptids) > 0 else root
                    looser = root
            need_update.append(winner)
            # Only append looser if it's different from winner to avoid duplicates
            if looser is not winner:
                need_update.append(looser)
            self.add_encounter_log(root['hp'], 'HP', f"Root 🫀")
            self.add_encounter_log(len(cryptids), 'SIZE', f"Cryptid Survivors")
            self.add_encounter_log(winner['hp'], '🫀', f"Winner {winner['name'].upper()}")
            self.add_encounter_log(looser['hp'], '🫀', f"Looser {looser['name'].upper()}")
        for dude in need_update:
            piece_of_pie = (total_reward / len(need_update))
            dude['xp'] += piece_of_pie
            dude['sanity'] += ( self.GOLDEN_RATIO * dude['sanity'] )
            self.add_encounter_log(piece_of_pie, 'winner', f"{dude['name'].upper()}|{dude['hp']}🫀 ")

        self.redis_service.set_without_expiry(self.redis_service.get_cache_key('num83r5','teamup_members'),teamup_members)
        return need_update


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
        was_too_much = False
        while god['hp'] > 0 and len(team) > 0 and not was_too_much:
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
            was_too_much = rounds >= self.total_rounds
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
        was_too_much = False
        while god['hp'] > 0 and cryptid['hp'] > 0 and not was_too_much:
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
            was_too_much = rounds >= self.total_rounds
        winner = looser = None
        if was_too_much: 
            winner = god
            looser = cryptid
        else:
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
        was_too_much = False
        while who['hp'] > 0 and enemy['hp'] > 0 and not was_too_much:
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
            was_too_much = rounds >= self.total_rounds
        winner = looser = None
        if was_too_much: 
            winner = enemy
            looser = who
        else:
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