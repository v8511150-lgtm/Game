import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class CardsCarnageDatabase:
    """
    SQLite Database for Cards Carnage: Basketball Card Creator
    Handles persistent storage of all game data
    """
    
    def __init__(self, db_name: str = "cards_carnage.db"):
        self.db_name = db_name
        self.connection = None
        self.initialize_database()
    
    def initialize_database(self):
        """Create all necessary tables if they don't exist"""
        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        
        # Players Table (for player cards)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_cards (
                card_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                positions TEXT NOT NULL,
                image_url TEXT,
                overall INTEGER NOT NULL,
                attributes TEXT NOT NULL,
                card_design TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_custom BOOLEAN DEFAULT 1
            )
        ''')
        
        # Teams Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT NOT NULL UNIQUE,
                team_type TEXT DEFAULT 'custom',
                pg_players TEXT NOT NULL,
                sg_players TEXT NOT NULL,
                sf_players TEXT NOT NULL,
                pf_players TEXT NOT NULL,
                c_players TEXT NOT NULL,
                overall_rating REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User Progress Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
                level INTEGER DEFAULT 1,
                total_xp INTEGER DEFAULT 0,
                money INTEGER DEFAULT 50000,
                gems INTEGER DEFAULT 0,
                total_cards_created INTEGER DEFAULT 0,
                total_teams_created INTEGER DEFAULT 0,
                challenges_completed INTEGER DEFAULT 0,
                tournaments_completed INTEGER DEFAULT 0,
                games_won INTEGER DEFAULT 0,
                games_lost INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Boosts Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS boosts (
                boost_id INTEGER PRIMARY KEY AUTOINCREMENT,
                boost_type TEXT NOT NULL,
                rarity TEXT NOT NULL,
                attribute_boost TEXT,
                boost_value INTEGER,
                games_remaining INTEGER,
                applied_to_card_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Auction House Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auction_house (
                listing_id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL,
                seller_name TEXT NOT NULL,
                price INTEGER NOT NULL,
                is_snipe BOOLEAN DEFAULT 0,
                discount_percent REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                sold BOOLEAN DEFAULT 0,
                FOREIGN KEY(card_id) REFERENCES player_cards(card_id)
            )
        ''')
        
        # Challenge History Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS challenge_history (
                challenge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_name TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                reward_money INTEGER,
                reward_xp INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tournament History Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tournament_history (
                tournament_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_name TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                rounds INTEGER,
                final_rank INTEGER,
                reward_cards TEXT,
                reward_money INTEGER,
                reward_xp INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                won BOOLEAN DEFAULT 0
            )
        ''')
        
        # Game Simulation History Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_history (
                game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                carnage_team_id INTEGER,
                ai_team_id INTEGER,
                carnage_score INTEGER,
                ai_score INTEGER,
                winner TEXT,
                game_type TEXT DEFAULT 'regular',
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(carnage_team_id) REFERENCES teams(team_id),
                FOREIGN KEY(ai_team_id) REFERENCES teams(team_id)
            )
        ''')
        
        # Achievements Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                achievement_name TEXT NOT NULL UNIQUE,
                description TEXT,
                reward_gems INTEGER DEFAULT 0,
                unlocked BOOLEAN DEFAULT 0,
                unlocked_at TIMESTAMP
            )
        ''')
        
        self.connection.commit()
        print("✅ Database initialized successfully!")
    
    # ==================== PLAYER CARD OPERATIONS ====================
    
    def add_player_card(self, player_name: str, positions: List[str], attributes: Dict,
                       card_design: str, image_url: str = None, is_custom: bool = True) -> int:
        """Add a new player card to the database"""
        cursor = self.connection.cursor()
        attributes_json = json.dumps(attributes)
        positions_json = json.dumps(positions)
        overall = attributes.get('overall', 75)
        
        cursor.execute('''
            INSERT INTO player_cards 
            (player_name, positions, image_url, overall, attributes, card_design, is_custom)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (player_name, positions_json, image_url, overall, attributes_json, card_design, is_custom))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_player_card(self, card_id: int) -> Optional[Dict]:
        """Retrieve a specific player card"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM player_cards WHERE card_id = ?', (card_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                'card_id': row['card_id'],
                'player_name': row['player_name'],
                'positions': json.loads(row['positions']),
                'image_url': row['image_url'],
                'overall': row['overall'],
                'attributes': json.loads(row['attributes']),
                'card_design': row['card_design'],
                'created_at': row['created_at'],
                'is_custom': row['is_custom']
            }
        return None
    
    def get_all_player_cards(self) -> List[Dict]:
        """Retrieve all player cards"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM player_cards ORDER BY created_at DESC')
        cards = []
        
        for row in cursor.fetchall():
            cards.append({
                'card_id': row['card_id'],
                'player_name': row['player_name'],
                'positions': json.loads(row['positions']),
                'image_url': row['image_url'],
                'overall': row['overall'],
                'attributes': json.loads(row['attributes']),
                'card_design': row['card_design'],
                'created_at': row['created_at'],
                'is_custom': row['is_custom']
            })
        
        return cards
    
    def delete_player_card(self, card_id: int) -> bool:
        """Delete a player card"""
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM player_cards WHERE card_id = ?', (card_id,))
        self.connection.commit()
        return cursor.rowcount > 0
    
    # ==================== TEAM OPERATIONS ====================
    
    def add_team(self, team_name: str, pg_players: List[int], sg_players: List[int],
                 sf_players: List[int], pf_players: List[int], c_players: List[int],
                 team_type: str = 'custom') -> int:
        """Add a new team to the database"""
        cursor = self.connection.cursor()
        
        cursor.execute('''
            INSERT INTO teams 
            (team_name, team_type, pg_players, sg_players, sf_players, pf_players, c_players)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (team_name, team_type, 
              json.dumps(pg_players), json.dumps(sg_players), json.dumps(sf_players),
              json.dumps(pf_players), json.dumps(c_players)))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_team(self, team_id: int) -> Optional[Dict]:
        """Retrieve a specific team"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM teams WHERE team_id = ?', (team_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                'team_id': row['team_id'],
                'team_name': row['team_name'],
                'team_type': row['team_type'],
                'pg_players': json.loads(row['pg_players']),
                'sg_players': json.loads(row['sg_players']),
                'sf_players': json.loads(row['sf_players']),
                'pf_players': json.loads(row['pf_players']),
                'c_players': json.loads(row['c_players']),
                'overall_rating': row['overall_rating'],
                'created_at': row['created_at']
            }
        return None
    
    def get_all_teams(self, team_type: str = None) -> List[Dict]:
        """Retrieve all teams, optionally filtered by type"""
        cursor = self.connection.cursor()
        
        if team_type:
            cursor.execute('SELECT * FROM teams WHERE team_type = ? ORDER BY created_at DESC', (team_type,))
        else:
            cursor.execute('SELECT * FROM teams ORDER BY created_at DESC')
        
        teams = []
        for row in cursor.fetchall():
            teams.append({
                'team_id': row['team_id'],
                'team_name': row['team_name'],
                'team_type': row['team_type'],
                'pg_players': json.loads(row['pg_players']),
                'sg_players': json.loads(row['sg_players']),
                'sf_players': json.loads(row['sf_players']),
                'pf_players': json.loads(row['pf_players']),
                'c_players': json.loads(row['c_players']),
                'overall_rating': row['overall_rating'],
                'created_at': row['created_at']
            })
        
        return teams
    
    def get_carnage_team(self) -> Optional[Dict]:
        """Retrieve the Carnage team (main team)"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM teams WHERE team_type = ?', ('carnage',))
        row = cursor.fetchone()
        
        if row:
            return {
                'team_id': row['team_id'],
                'team_name': row['team_name'],
                'team_type': row['team_type'],
                'pg_players': json.loads(row['pg_players']),
                'sg_players': json.loads(row['sg_players']),
                'sf_players': json.loads(row['sf_players']),
                'pf_players': json.loads(row['pf_players']),
                'c_players': json.loads(row['c_players']),
                'overall_rating': row['overall_rating'],
                'created_at': row['created_at']
            }
        return None
    
    def update_team(self, team_id: int, pg_players: List[int] = None, sg_players: List[int] = None,
                    sf_players: List[int] = None, pf_players: List[int] = None, 
                    c_players: List[int] = None, overall_rating: float = None) -> bool:
        """Update a team's players or rating"""
        cursor = self.connection.cursor()
        
        updates = []
        params = []
        
        if pg_players is not None:
            updates.append('pg_players = ?')
            params.append(json.dumps(pg_players))
        if sg_players is not None:
            updates.append('sg_players = ?')
            params.append(json.dumps(sg_players))
        if sf_players is not None:
            updates.append('sf_players = ?')
            params.append(json.dumps(sf_players))
        if pf_players is not None:
            updates.append('pf_players = ?')
            params.append(json.dumps(pf_players))
        if c_players is not None:
            updates.append('c_players = ?')
            params.append(json.dumps(c_players))
        if overall_rating is not None:
            updates.append('overall_rating = ?')
            params.append(overall_rating)
        
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(team_id)
        
        query = f"UPDATE teams SET {', '.join(updates)} WHERE team_id = ?"
        cursor.execute(query, params)
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def delete_team(self, team_id: int) -> bool:
        """Delete a team"""
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM teams WHERE team_id = ?', (team_id,))
        self.connection.commit()
        return cursor.rowcount > 0
    
    # ==================== USER PROGRESS OPERATIONS ====================
    
    def initialize_user_progress(self) -> int:
        """Create or get user progress record"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT progress_id FROM user_progress LIMIT 1')
        row = cursor.fetchone()
        
        if row:
            return row['progress_id']
        
        cursor.execute('INSERT INTO user_progress DEFAULT VALUES')
        self.connection.commit()
        return cursor.lastrowid
    
    def get_user_progress(self) -> Dict:
        """Get current user progress"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM user_progress LIMIT 1')
        row = cursor.fetchone()
        
        if row:
            return {
                'progress_id': row['progress_id'],
                'level': row['level'],
                'total_xp': row['total_xp'],
                'money': row['money'],
                'gems': row['gems'],
                'total_cards_created': row['total_cards_created'],
                'total_teams_created': row['total_teams_created'],
                'challenges_completed': row['challenges_completed'],
                'tournaments_completed': row['tournaments_completed'],
                'games_won': row['games_won'],
                'games_lost': row['games_lost']
            }
        return None
    
    def update_user_progress(self, level: int = None, total_xp: int = None, money: int = None,
                            gems: int = None, total_cards_created: int = None,
                            total_teams_created: int = None, challenges_completed: int = None,
                            tournaments_completed: int = None, games_won: int = None,
                            games_lost: int = None) -> bool:
        """Update user progress"""
        cursor = self.connection.cursor()
        
        updates = []
        params = []
        
        if level is not None:
            updates.append('level = ?')
            params.append(level)
        if total_xp is not None:
            updates.append('total_xp = ?')
            params.append(total_xp)
        if money is not None:
            updates.append('money = ?')
            params.append(money)
        if gems is not None:
            updates.append('gems = ?')
            params.append(gems)
        if total_cards_created is not None:
            updates.append('total_cards_created = ?')
            params.append(total_cards_created)
        if total_teams_created is not None:
            updates.append('total_teams_created = ?')
            params.append(total_teams_created)
        if challenges_completed is not None:
            updates.append('challenges_completed = ?')
            params.append(challenges_completed)
        if tournaments_completed is not None:
            updates.append('tournaments_completed = ?')
            params.append(tournaments_completed)
        if games_won is not None:
            updates.append('games_won = ?')
            params.append(games_won)
        if games_lost is not None:
            updates.append('games_lost = ?')
            params.append(games_lost)
        
        if not updates:
            return False
        
        updates.append('updated_at = CURRENT_TIMESTAMP')
        query = f"UPDATE user_progress SET {', '.join(updates)}"
        cursor.execute(query, params)
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def add_xp(self, xp_amount: int) -> Dict:
        """Add XP and return updated progress"""
        progress = self.get_user_progress()
        new_xp = progress['total_xp'] + xp_amount
        self.update_user_progress(total_xp=new_xp)
        return self.get_user_progress()
    
    def add_money(self, money_amount: int) -> int:
        """Add money and return new balance"""
        progress = self.get_user_progress()
        new_money = progress['money'] + money_amount
        self.update_user_progress(money=new_money)
        return new_money
    
    def add_gems(self, gem_amount: int) -> int:
        """Add gems and return new balance"""
        progress = self.get_user_progress()
        new_gems = progress['gems'] + gem_amount
        self.update_user_progress(gems=new_gems)
        return new_gems
    
    # ==================== AUCTION HOUSE OPERATIONS ====================
    
    def add_listing(self, card_id: int, seller_name: str, price: int, is_snipe: bool = False,
                   discount_percent: float = 0) -> int:
        """Add a card to auction house"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO auction_house 
            (card_id, seller_name, price, is_snipe, discount_percent)
            VALUES (?, ?, ?, ?, ?)
        ''', (card_id, seller_name, price, is_snipe, discount_percent))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_auction_listings(self, limit: int = 20, unsold_only: bool = True) -> List[Dict]:
        """Get active auction house listings"""
        cursor = self.connection.cursor()
        
        if unsold_only:
            cursor.execute('''
                SELECT * FROM auction_house 
                WHERE sold = 0 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        else:
            cursor.execute('''
                SELECT * FROM auction_house 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        listings = []
        for row in cursor.fetchall():
            listings.append({
                'listing_id': row['listing_id'],
                'card_id': row['card_id'],
                'seller_name': row['seller_name'],
                'price': row['price'],
                'is_snipe': row['is_snipe'],
                'discount_percent': row['discount_percent'],
                'created_at': row['created_at'],
                'sold': row['sold']
            })
        
        return listings
    
    def buy_listing(self, listing_id: int) -> bool:
        """Mark a listing as sold"""
        cursor = self.connection.cursor()
        cursor.execute('UPDATE auction_house SET sold = 1 WHERE listing_id = ?', (listing_id,))
        self.connection.commit()
        return cursor.rowcount > 0
    
    # ==================== CHALLENGE OPERATIONS ====================
    
    def add_challenge_completion(self, challenge_name: str, difficulty: str,
                                reward_money: int, reward_xp: int, success: bool = True) -> int:
        """Record a completed challenge"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO challenge_history 
            (challenge_name, difficulty, reward_money, reward_xp, success)
            VALUES (?, ?, ?, ?, ?)
        ''', (challenge_name, difficulty, reward_money, reward_xp, success))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_challenge_history(self, limit: int = 50) -> List[Dict]:
        """Get challenge history"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM challenge_history 
            ORDER BY completed_at DESC 
            LIMIT ?
        ''', (limit,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'challenge_id': row['challenge_id'],
                'challenge_name': row['challenge_name'],
                'difficulty': row['difficulty'],
                'reward_money': row['reward_money'],
                'reward_xp': row['reward_xp'],
                'completed_at': row['completed_at'],
                'success': row['success']
            })
        
        return history
    
    # ==================== TOURNAMENT OPERATIONS ====================
    
    def add_tournament_completion(self, tournament_name: str, difficulty: str, rounds: int,
                                 final_rank: int, reward_money: int, reward_xp: int,
                                 reward_cards: List[int], won: bool = False) -> int:
        """Record a completed tournament"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO tournament_history 
            (tournament_name, difficulty, rounds, final_rank, reward_cards, reward_money, reward_xp, won)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tournament_name, difficulty, rounds, final_rank,
              json.dumps(reward_cards), reward_money, reward_xp, won))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_tournament_history(self, limit: int = 50) -> List[Dict]:
        """Get tournament history"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM tournament_history 
            ORDER BY completed_at DESC 
            LIMIT ?
        ''', (limit,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'tournament_id': row['tournament_id'],
                'tournament_name': row['tournament_name'],
                'difficulty': row['difficulty'],
                'rounds': row['rounds'],
                'final_rank': row['final_rank'],
                'reward_cards': json.loads(row['reward_cards']),
                'reward_money': row['reward_money'],
                'reward_xp': row['reward_xp'],
                'completed_at': row['completed_at'],
                'won': row['won']
            })
        
        return history
    
    # ==================== GAME HISTORY OPERATIONS ====================
    
    def add_game(self, carnage_team_id: int, ai_team_id: int, carnage_score: int,
                ai_score: int, winner: str, game_type: str = 'regular') -> int:
        """Record a simulated game"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO game_history 
            (carnage_team_id, ai_team_id, carnage_score, ai_score, winner, game_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (carnage_team_id, ai_team_id, carnage_score, ai_score, winner, game_type))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_game_history(self, limit: int = 50) -> List[Dict]:
        """Get game history"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM game_history 
            ORDER BY played_at DESC 
            LIMIT ?
        ''', (limit,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'game_id': row['game_id'],
                'carnage_team_id': row['carnage_team_id'],
                'ai_team_id': row['ai_team_id'],
                'carnage_score': row['carnage_score'],
                'ai_score': row['ai_score'],
                'winner': row['winner'],
                'game_type': row['game_type'],
                'played_at': row['played_at']
            })
        
        return history
    
    # ==================== ACHIEVEMENT OPERATIONS ====================
    
    def initialize_achievements(self):
        """Add all achievements to database"""
        achievements = [
            ("First Card", "Create your first player card", 10),
            ("Card Collector", "Create 10 player cards", 25),
            ("Master Creator", "Create 50 player cards", 100),
            ("Team Builder", "Create your first team", 15),
            ("Dynasty", "Create 10 teams", 50),
            ("Money Maker", "Earn $50,000", 30),
            ("Pack Opener", "Open 10 packs", 20),
            ("Auction Master", "Buy 5 cards from auction house", 40),
            ("Challenge Complete", "Complete 10 challenges", 35),
            ("Tournament Winner", "Win a tournament", 75),
            ("Game Winner", "Win 10 games against AI", 50),
            ("Level 10", "Reach level 10", 100),
            ("Level 25", "Reach level 25", 200),
            ("Snipe Master", "Snipe 3 deals in auction house", 60)
        ]
        
        cursor = self.connection.cursor()
        for name, description, gems in achievements:
            cursor.execute('''
                INSERT OR IGNORE INTO achievements 
                (achievement_name, description, reward_gems)
                VALUES (?, ?, ?)
            ''', (name, description, gems))
        
        self.connection.commit()
    
    def unlock_achievement(self, achievement_name: str) -> bool:
        """Unlock an achievement"""
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE achievements 
            SET unlocked = 1, unlocked_at = CURRENT_TIMESTAMP 
            WHERE achievement_name = ?
        ''', (achievement_name,))
        self.connection.commit()
        return cursor.rowcount > 0
    
    def get_achievements(self) -> List[Dict]:
        """Get all achievements"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM achievements')
        
        achievements = []
        for row in cursor.fetchall():
            achievements.append({
                'achievement_id': row['achievement_id'],
                'achievement_name': row['achievement_name'],
                'description': row['description'],
                'reward_gems': row['reward_gems'],
                'unlocked': row['unlocked'],
                'unlocked_at': row['unlocked_at']
            })
        
        return achievements
    
    # ==================== BOOST OPERATIONS ====================
    
    def add_boost(self, boost_type: str, rarity: str, attribute_boost: str = None,
                 boost_value: int = None, games_remaining: int = 3) -> int:
        """Add a new boost"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO boosts 
            (boost_type, rarity, attribute_boost, boost_value, games_remaining)
            VALUES (?, ?, ?, ?, ?)
        ''', (boost_type, rarity, attribute_boost, boost_value, games_remaining))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def apply_boost_to_card(self, boost_id: int, card_id: int) -> bool:
        """Apply a boost to a card"""
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE boosts 
            SET applied_to_card_id = ? 
            WHERE boost_id = ?
        ''', (card_id, boost_id))
        
        self.connection.commit()
        return cursor.rowcount > 0
    
    def get_boosts_for_card(self, card_id: int) -> List[Dict]:
        """Get all boosts applied to a card"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM boosts 
            WHERE applied_to_card_id = ? 
            ORDER BY created_at DESC
        ''', (card_id,))
        
        boosts = []
        for row in cursor.fetchall():
            boosts.append({
                'boost_id': row['boost_id'],
                'boost_type': row['boost_type'],
                'rarity': row['rarity'],
                'attribute_boost': row['attribute_boost'],
                'boost_value': row['boost_value'],
                'games_remaining': row['games_remaining']
            })
        
        return boosts
    
    # ==================== UTILITY OPERATIONS ====================
    
    def get_database_stats(self) -> Dict:
        """Get overall database statistics"""
        cursor = self.connection.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM player_cards')
        total_cards = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM teams')
        total_teams = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM auction_house WHERE sold = 0')
        active_listings = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM challenge_history')
        total_challenges = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM game_history')
        total_games = cursor.fetchone()['count']
        
        progress = self.get_user_progress()
        
        return {
            'total_cards': total_cards,
            'total_teams': total_teams,
            'active_listings': active_listings,
            'total_challenges_completed': total_challenges,
            'total_games_played': total_games,
            'user_level': progress['level'],
            'user_money': progress['money'],
            'user_gems': progress['gems'],
            'user_xp': progress['total_xp']
        }
    
    def export_save_file(self, filename: str = "save.json") -> bool:
        """Export all game data to a JSON file"""
        try:
            save_data = {
                'cards': self.get_all_player_cards(),
                'teams': self.get_all_teams(),
                'progress': self.get_user_progress(),
                'achievements': self.get_achievements(),
                'auction_listings': self.get_auction_listings(limit=100, unsold_only=False),
                'challenge_history': self.get_challenge_history(),
                'tournament_history': self.get_tournament_history(),
                'game_history': self.get_game_history(),
                'exported_at': datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=4)
            
            return True
        except Exception as e:
            print(f"❌ Error exporting save file: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Initialize database
    db = CardsCarnageDatabase()
    
    # Initialize user progress and achievements
    db.initialize_user_progress()
    db.initialize_achievements()
    
    # Create a sample player card
    print("\n🏀 Creating sample player card...")
    attributes = {
        'overall': 95,
        'scoring': 92,
        'shooting': 88,
        'speed': 85,
        'strength': 80,
        'handles': 90,
        'playmaking': 87,
        'defense': 83,
        'rebounding': 75
    }
    card_id = db.add_player_card(
        player_name="LeBron James",
        positions=["SF", "PF"],
        attributes=attributes,
        card_design="Elite Gold",
        image_url="https://example.com/lebron.jpg"
    )
    print(f"✅ Created card with ID: {card_id}")
    
    # Retrieve the card
    card = db.get_player_card(card_id)
    print(f"📋 Card: {card['player_name']} - OVR: {card['overall']}")
    
    # Add money and XP to user
    print("\n💰 Adding money and XP...")
    db.add_money(5000)
    db.add_xp(250)
    progress = db.get_user_progress()
    print(f"✅ Money: ${progress['money']}, XP: {progress['total_xp']}")
    
    # Record a challenge completion
    print("\n🎯 Recording challenge completion...")
    db.add_challenge_completion(
        challenge_name="Score 50 Points",
        difficulty="Medium",
        reward_money=2500,
        reward_xp=500
    )
    
    # Get database stats
    print("\n📊 Database Statistics:")
    stats = db.get_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Export save file
    print("\n💾 Exporting save file...")
    if db.export_save_file("game_save.json"):
        print("✅ Save file exported successfully!")
    
    # Close database
    db.close()
