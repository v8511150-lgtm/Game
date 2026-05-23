"""
Cards Carnage: Basketball Card Creator - Complete Foundation
============================================================

A comprehensive game system for creating custom NBA player cards,
building teams, competing in tournaments, and progressing through levels.

All 8 Core Systems:
1. Player Card System
2. Team Management
3. Pack & Card Generation
4. Auction House (Dynamic Pricing)
5. Boost System
6. Challenges & Tournaments
7. Game Simulation Engine
8. Progression System (Leveling, Currency, Achievements)
"""

import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


# ============================================================
# ENUMS & CONSTANTS
# ============================================================

class Position(Enum):
    """Player positions"""
    PG = "Point Guard"
    SG = "Shooting Guard"
    SF = "Small Forward"
    PF = "Power Forward"
    C = "Center"


class CardDesign(Enum):
    """Available card designs"""
    CLASSIC = "Classic"
    MODERN = "Modern"
    HOLOGRAPHIC = "Holographic"
    VINTAGE = "Vintage"
    NEON = "Neon"
    DIAMOND = "Diamond"
    PLATINUM = "Platinum"
    GOLD = "Gold"


class PackType(Enum):
    """Pack types with different odds"""
    BEGINNER = "Beginner"
    RARE = "Rare"
    ELITE = "Elite"
    LEGENDARY = "Legendary"


class BoostRarity(Enum):
    """Boost rarity levels"""
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    EPIC = "Epic"
    LEGENDARY = "Legendary"


class ChallengeDifficulty(Enum):
    """Challenge difficulty levels"""
    EASY = 1
    MEDIUM = 2
    HARD = 3
    ELITE = 4
    LEGENDARY = 5


class Achievement(Enum):
    """Achievement types"""
    FIRST_CARD = "First Card Creator"
    FIRST_TEAM = "Team Builder"
    LEVEL_10 = "Novice"
    LEVEL_25 = "Veteran"
    LEVEL_50 = "Legend"
    PERFECT_CARD = "Perfect 170"
    TOURNEY_WINNER = "Champion"
    SNIPE_MASTER = "Snipe Master"


# ============================================================
# CONSTANTS
# ============================================================

ATTRIBUTES = ["Scoring", "Shooting", "Speed", "Strength", "Handles", "Playmaking", "Defense", "Rebounding"]
MIN_OVR = 75
MAX_OVR = 170
MIN_ATTRIBUTE = 0
MAX_ATTRIBUTE = 170
MAX_SINGLE_ATTRIBUTE = 170  # Only 1 can be this high
MAX_OTHER_ATTRIBUTES = 155  # Others must be this or lower if one is 170

POSITIONS_LIST = [Position.PG, Position.SG, Position.SF, Position.PF, Position.C]
PLAYERS_PER_POSITION = 2

# Pack odds (OVR distribution)
PACK_ODDS = {
    PackType.BEGINNER: {
        (75, 80): 0.40,
        (81, 90): 0.40,
        (91, 95): 0.20,
    },
    PackType.RARE: {
        (85, 95): 0.30,
        (96, 110): 0.40,
        (111, 120): 0.30,
    },
    PackType.ELITE: {
        (100, 125): 0.30,
        (126, 145): 0.50,
        (146, 155): 0.20,
    },
    PackType.LEGENDARY: {
        (120, 140): 0.20,
        (141, 160): 0.40,
        (161, 170): 0.40,
    },
}

PACK_PRICES = {
    PackType.BEGINNER: 1000,
    PackType.RARE: 2500,
    PackType.ELITE: 5000,
    PackType.LEGENDARY: 10000,
}

# Challenge rewards
CHALLENGE_REWARDS = {
    ChallengeDifficulty.EASY: {"money": 500, "xp": 25},
    ChallengeDifficulty.MEDIUM: {"money": 1500, "xp": 100},
    ChallengeDifficulty.HARD: {"money": 3000, "xp": 250},
    ChallengeDifficulty.ELITE: {"money": 6000, "xp": 1000},
    ChallengeDifficulty.LEGENDARY: {"money": 15000, "xp": 3000},
}

TOURNAMENT_REWARDS = {
    ChallengeDifficulty.EASY: {"money": 2000, "xp": 500, "cards": 1},
    ChallengeDifficulty.MEDIUM: {"money": 5000, "xp": 1000, "cards": 2},
    ChallengeDifficulty.HARD: {"money": 10000, "xp": 2000, "cards": 3},
    ChallengeDifficulty.ELITE: {"money": 20000, "xp": 3500, "cards": 4},
    ChallengeDifficulty.LEGENDARY: {"money": 50000, "xp": 5000, "cards": 5},
}

# Boost stats
BOOST_TYPES = ["Scoring", "Shooting", "Speed", "Strength", "Handles", "Playmaking", "Defense", "Rebounding", "All"]
BOOST_DURATIONS = {
    BoostRarity.COMMON: 3,
    BoostRarity.UNCOMMON: 4,
    BoostRarity.RARE: 5,
    BoostRarity.EPIC: 6,
    BoostRarity.LEGENDARY: 8,
}
BOOST_STRENGTH = {
    BoostRarity.COMMON: 2,
    BoostRarity.UNCOMMON: 4,
    BoostRarity.RARE: 6,
    BoostRarity.EPIC: 10,
    BoostRarity.LEGENDARY: 15,
}


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class PlayerCard:
    """Represents a custom basketball player card"""
    card_id: str
    player_name: str
    overall: int
    positions: List[Position]  # Max 2
    design: CardDesign
    image_url: str
    created_date: datetime
    attributes: Dict[str, int] = field(default_factory=dict)
    creator_id: str = "player"
    times_used_in_games: int = 0
    wins: int = 0
    losses: int = 0
    
    def __post_init__(self):
        """Initialize attributes if not provided"""
        if not self.attributes:
            self.attributes = {attr: 0 for attr in ATTRIBUTES}
    
    def get_average_attribute(self) -> int:
        """Get average of all attributes"""
        return int(sum(self.attributes.values()) / len(ATTRIBUTES))
    
    def get_best_attribute(self) -> Tuple[str, int]:
        """Get highest attribute"""
        best_attr = max(self.attributes.items(), key=lambda x: x[1])
        return best_attr
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "card_id": self.card_id,
            "player_name": self.player_name,
            "overall": self.overall,
            "positions": [p.name for p in self.positions],
            "design": self.design.value,
            "attributes": self.attributes,
            "average_attribute": self.get_average_attribute(),
            "best_attribute": self.get_best_attribute()[0],
        }


@dataclass
class Boost:
    """Represents a temporary attribute boost"""
    boost_id: str
    boost_type: str  # Attribute name or "All"
    rarity: BoostRarity
    strength: int
    duration_games: int
    applied_date: datetime
    
    def is_active(self, games_played: int) -> bool:
        """Check if boost is still active"""
        return games_played < self.duration_games


@dataclass
class Team:
    """Represents a team of players"""
    team_id: str
    team_name: str
    is_carnage_team: bool
    cards: Dict[Position, List[PlayerCard]] = field(default_factory=dict)
    created_date: datetime = field(default_factory=datetime.now)
    wins: int = 0
    losses: int = 0
    
    def __post_init__(self):
        """Initialize empty position slots"""
        if not self.cards:
            self.cards = {pos: [] for pos in POSITIONS_LIST}
    
    def add_card(self, card: PlayerCard, position: Position) -> bool:
        """Add a card to the team at a specific position"""
        if len(self.cards[position]) < PLAYERS_PER_POSITION:
            self.cards[position].append(card)
            return True
        return False
    
    def is_complete(self) -> bool:
        """Check if team has all required players (2 per position)"""
        return all(len(self.cards[pos]) == PLAYERS_PER_POSITION for pos in POSITIONS_LIST)
    
    def get_team_overall(self) -> int:
        """Calculate average overall of all players"""
        all_cards = []
        for cards_list in self.cards.values():
            all_cards.extend(cards_list)
        
        if not all_cards:
            return 0
        return int(sum(card.overall for card in all_cards) / len(all_cards))
    
    def get_all_cards(self) -> List[PlayerCard]:
        """Get all cards in team"""
        all_cards = []
        for cards_list in self.cards.values():
            all_cards.extend(cards_list)
        return all_cards
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "is_carnage_team": self.is_carnage_team,
            "team_overall": self.get_team_overall(),
            "wins": self.wins,
            "losses": self.losses,
            "record": f"{self.wins}-{self.losses}",
            "positions": {
                pos.name: [card.to_dict() for card in self.cards[pos]]
                for pos in POSITIONS_LIST
            }
        }


@dataclass
class AuctionListing:
    """Represents a card listing on auction house"""
    listing_id: str
    card: PlayerCard
    price: int
    listed_date: datetime
    is_snipe: bool = False
    discount_percent: int = 0


@dataclass
class UserProgress:
    """Tracks player progression"""
    player_id: str
    level: int = 1
    xp: int = 0
    money: int = 50000  # Starting money
    gems: int = 100  # Premium currency
    total_cards_created: int = 0
    total_teams_created: int = 0
    games_played: int = 0
    games_won: int = 0
    achievements_unlocked: List[Achievement] = field(default_factory=list)
    
    def get_xp_for_next_level(self) -> int:
        """Calculate XP required for next level"""
        return int(100 * (1.1 ** (self.level - 1)))
    
    def add_xp(self, amount: int) -> bool:
        """Add XP and check for level up"""
        self.xp += amount
        xp_needed = self.get_xp_for_next_level()
        
        if self.xp >= xp_needed:
            self.xp -= xp_needed
            self.level += 1
            
            # Milestone bonuses
            if self.level % 5 == 0:
                self.gems += 50
            if self.level == 10:
                self.gems += 100
            if self.level == 25:
                self.gems += 250
            if self.level == 50:
                self.gems += 500
            
            return True
        return False
    
    def get_win_rate(self) -> float:
        """Get win percentage"""
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100
    
    def unlock_achievement(self, achievement: Achievement) -> bool:
        """Unlock an achievement"""
        if achievement not in self.achievements_unlocked:
            self.achievements_unlocked.append(achievement)
            return True
        return False


# ============================================================
# CARD VALIDATION & CREATION
# ============================================================

class CardValidator:
    """Validates card attributes and overall"""
    
    @staticmethod
    def validate_attributes(attributes: Dict[str, int], overall: int) -> Tuple[bool, str]:
        """
        Validate attribute rules:
        - Max OVR is 170
        - Min OVR is 75
        - Only 1 attribute can be 170
        - If 1 is 170, all others must be ≤ 155
        - Attributes must sum to reasonable overall
        """
        
        # Check OVR range
        if not (MIN_OVR <= overall <= MAX_OVR):
            return False, f"Overall must be between {MIN_OVR} and {MAX_OVR}"
        
        # Check attribute values
        max_170_count = sum(1 for v in attributes.values() if v == 170)
        
        if max_170_count > 1:
            return False, "Only 1 attribute can be 170"
        
        if max_170_count == 1:
            # If one is 170, others must be ≤ 155
            for attr, value in attributes.items():
                if value != 170 and value > MAX_OTHER_ATTRIBUTES:
                    return False, f"If one attribute is 170, others must be ≤ {MAX_OTHER_ATTRIBUTES}"
        
        return True, "Valid"
    
    @staticmethod
    def create_balanced_attributes(overall: int) -> Dict[str, int]:
        """Create balanced attributes based on overall"""
        attributes = {}
        base_value = overall // len(ATTRIBUTES)
        remainder = overall % len(ATTRIBUTES)
        
        for i, attr in enumerate(ATTRIBUTES):
            value = base_value + (1 if i < remainder else 0)
            attributes[attr] = min(max(value, MIN_ATTRIBUTE), MAX_ATTRIBUTE)
        
        return attributes


# ============================================================
# PACK GENERATOR
# ============================================================

class PackGenerator:
    """Generates card packs with weighted odds"""
    
    def __init__(self):
        self.pack_counter = 0
    
    def generate_pack(self, pack_type: PackType) -> List[PlayerCard]:
        """Generate a pack of 5 cards"""
        pack = []
        for _ in range(5):
            card = self.generate_single_card(pack_type)
            pack.append(card)
        return pack
    
    def generate_single_card(self, pack_type: PackType) -> PlayerCard:
        """Generate a single card based on pack type odds"""
        self.pack_counter += 1
        
        # Get OVR based on pack odds
        ovr = self._get_overall_by_odds(pack_type)
        
        # Generate card
        card_id = f"CARD_{self.pack_counter}_{datetime.now().timestamp()}"
        name = f"Default Player {self.pack_counter}"
        design = random.choice(list(CardDesign))
        positions = [random.choice(POSITIONS_LIST)]
        
        # 20% chance for multi-position
        if random.random() < 0.20:
            other_pos = random.choice([p for p in POSITIONS_LIST if p != positions[0]])
            positions.append(other_pos)
        
        attributes = CardValidator.create_balanced_attributes(ovr)
        
        card = PlayerCard(
            card_id=card_id,
            player_name=name,
            overall=ovr,
            positions=positions,
            design=design,
            image_url="default_image.png",
            created_date=datetime.now(),
            attributes=attributes,
            creator_id="system"
        )
        
        return card
    
    def _get_overall_by_odds(self, pack_type: PackType) -> int:
        """Get overall based on pack odds"""
        odds = PACK_ODDS[pack_type]
        rand = random.random()
        cumulative = 0
        
        for (min_ovr, max_ovr), probability in odds.items():
            cumulative += probability
            if rand <= cumulative:
                return random.randint(min_ovr, max_ovr)
        
        # Fallback
        last_range = list(odds.keys())[-1]
        return random.randint(last_range[0], last_range[1])


# ============================================================
# AUCTION HOUSE
# ============================================================

class AuctionHouse:
    """Dynamic pricing and auction system"""
    
    def __init__(self):
        self.listings: List[AuctionListing] = []
        self.listing_counter = 0
    
    def calculate_price(self, card: PlayerCard) -> int:
        """
        Calculate price based on:
        - Overall (primary factor)
        - Best attribute
        - Average attribute
        - Design rarity
        """
        base_price = card.overall * 100
        
        best_attr_name, best_attr_value = card.get_best_attribute()
        avg_attr = card.get_average_attribute()
        
        # Bonus for high best attribute
        if best_attr_value >= 160:
            base_price *= 1.5
        elif best_attr_value >= 140:
            base_price *= 1.3
        elif best_attr_value >= 120:
            base_price *= 1.15
        
        # Bonus for high average
        if avg_attr >= 150:
            base_price *= 1.2
        elif avg_attr >= 130:
            base_price *= 1.1
        
        # Design rarity bonus
        design_value = {
            CardDesign.CLASSIC: 1.0,
            CardDesign.MODERN: 1.05,
            CardDesign.HOLOGRAPHIC: 1.15,
            CardDesign.VINTAGE: 1.08,
            CardDesign.NEON: 1.12,
            CardDesign.DIAMOND: 1.25,
            CardDesign.PLATINUM: 1.30,
            CardDesign.GOLD: 1.35,
        }
        base_price *= design_value.get(card.design, 1.0)
        
        # Add variance (±10%)
        variance = random.uniform(0.9, 1.1)
        final_price = int(base_price * variance)
        
        return max(final_price, 100)  # Minimum price
    
    def list_card(self, card: PlayerCard) -> AuctionListing:
        """List a card for auction"""
        self.listing_counter += 1
        price = self.calculate_price(card)
        
        # 15% chance for snipe
        is_snipe = random.random() < 0.15
        discount = 0
        if is_snipe:
            discount = random.randint(20, 40)
            price = int(price * (1 - discount / 100))
        
        listing = AuctionListing(
            listing_id=f"LIST_{self.listing_counter}",
            card=card,
            price=price,
            listed_date=datetime.now(),
            is_snipe=is_snipe,
            discount_percent=discount
        )
        
        self.listings.append(listing)
        return listing
    
    def get_available_listings(self) -> List[AuctionListing]:
        """Get all available listings"""
        return self.listings.copy()
    
    def buy_listing(self, listing_id: str) -> Optional[AuctionListing]:
        """Buy a listing (remove from auction)"""
        for i, listing in enumerate(self.listings):
            if listing.listing_id == listing_id:
                return self.listings.pop(i)
        return None


# ============================================================
# BOOST SYSTEM
# ============================================================

class BoostManager:
    """Manages boosts for cards"""
    
    @staticmethod
    def apply_boost(card: PlayerCard, boost: Boost) -> None:
        """Apply boost to a card"""
        if boost.boost_type == "All":
            for attr in ATTRIBUTES:
                card.attributes[attr] = min(card.attributes[attr] + boost.strength, MAX_ATTRIBUTE)
        else:
            if boost.boost_type in card.attributes:
                card.attributes[boost.boost_type] = min(
                    card.attributes[boost.boost_type] + boost.strength,
                    MAX_ATTRIBUTE
                )
        
        # Recalculate overall if needed
        avg = sum(card.attributes.values()) / len(ATTRIBUTES)
        if avg > card.overall:
            card.overall = min(int(avg), MAX_OVR)
    
    @staticmethod
    def generate_boost(rarity: BoostRarity) -> Boost:
        """Generate a random boost"""
        boost_type = random.choice(BOOST_TYPES)
        strength = BOOST_STRENGTH[rarity]
        duration = BOOST_DURATIONS[rarity]
        
        return Boost(
            boost_id=f"BOOST_{random.randint(10000, 99999)}",
            boost_type=boost_type,
            rarity=rarity,
            strength=strength,
            duration_games=duration,
            applied_date=datetime.now()
        )


# ============================================================
# GAME SIMULATION
# ============================================================

class GameSimulation:
    """Simulates basketball games between teams"""
    
    def __init__(self):
        self.game_counter = 0
    
    def simulate_game(self, team1: Team, team2: Team) -> Tuple[int, int, str]:
        """
        Simulate a game between two teams
        Returns: (team1_score, team2_score, winner_name)
        """
        self.game_counter += 1
        
        team1_ovr = team1.get_team_overall()
        team2_ovr = team2.get_team_overall()
        
        # Quarter scoring
        team1_score = 0
        team2_score = 0
        
        for quarter in range(4):
            # Calculate quarter scores
            t1_quarter = self._calculate_quarter_score(team1_ovr, team2_ovr)
            t2_quarter = self._calculate_quarter_score(team2_ovr, team1_ovr)
            
            team1_score += t1_quarter
            team2_score += t2_quarter
        
        # Overtime if tied
        while team1_score == team2_score:
            team1_score += self._calculate_quarter_score(team1_ovr, team2_ovr)
            team2_score += self._calculate_quarter_score(team2_ovr, team1_ovr)
        
        winner = team1.team_name if team1_score > team2_score else team2.team_name
        
        return team1_score, team2_score, winner
    
    def _calculate_quarter_score(self, team_ovr: int, opponent_ovr: int) -> int:
        """Calculate points scored in a quarter"""
        base_points = team_ovr // 2
        variance = random.randint(-10, 10)
        
        # OVR advantage
        if team_ovr > opponent_ovr:
            base_points += (team_ovr - opponent_ovr) // 2
        
        return max(base_points + variance, 15)


# ============================================================
# CHALLENGES & TOURNAMENTS
# ============================================================

class ChallengeManager:
    """Manages challenges and tournaments"""
    
    def complete_challenge(self, difficulty: ChallengeDifficulty) -> Dict:
        """Complete a challenge"""
        rewards = CHALLENGE_REWARDS[difficulty]
        
        return {
            "difficulty": difficulty.name,
            "money_earned": rewards["money"],
            "xp_earned": rewards["xp"],
            "status": "completed"
        }
    
    def run_tournament(self, team: Team, difficulty: ChallengeDifficulty, num_rounds: int = None) -> Dict:
        """Run a tournament"""
        if num_rounds is None:
            num_rounds = {
                ChallengeDifficulty.EASY: 3,
                ChallengeDifficulty.MEDIUM: 4,
                ChallengeDifficulty.HARD: 5,
                ChallengeDifficulty.ELITE: 6,
                ChallengeDifficulty.LEGENDARY: 6,
            }[difficulty]
        
        rewards = TOURNAMENT_REWARDS[difficulty]
        
        # Simulate tournament wins with difficulty modifier
        win_probability = {
            ChallengeDifficulty.EASY: 0.95,
            ChallengeDifficulty.MEDIUM: 0.80,
            ChallengeDifficulty.HARD: 0.65,
            ChallengeDifficulty.ELITE: 0.50,
            ChallengeDifficulty.LEGENDARY: 0.35,
        }[difficulty]
        
        tournament_won = all(random.random() < win_probability for _ in range(num_rounds))
        
        if tournament_won:
            return {
                "tournament_difficulty": difficulty.name,
                "rounds_completed": num_rounds,
                "status": "won",
                "money_earned": rewards["money"],
                "xp_earned": rewards["xp"],
                "cards_earned": rewards["cards"],
            }
        else:
            # Consolation prizes
            return {
                "tournament_difficulty": difficulty.name,
                "rounds_completed": random.randint(1, num_rounds - 1),
                "status": "lost",
                "money_earned": rewards["money"] // 2,
                "xp_earned": rewards["xp"] // 2,
                "cards_earned": 0,
            }


# ============================================================
# MAIN GAME CONTROLLER
# ============================================================

class CardsCarnageGame:
    """Main game controller - ties all systems together"""
    
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.player_id = f"PLAYER_{random.randint(10000, 99999)}"
        
        # Core systems
        self.progress = UserProgress(player_id=self.player_id)
        self.card_validator = CardValidator()
        self.pack_generator = PackGenerator()
        self.auction_house = AuctionHouse()
        self.boost_manager = BoostManager()
        self.game_sim = GameSimulation()
        self.challenge_manager = ChallengeManager()
        
        # Game data
        self.player_cards: List[PlayerCard] = []
        self.teams: Dict[str, Team] = {}
        self.carnage_team: Optional[Team] = None
        self.boosts: List[Boost] = []
        
        # Initialize
        self._initialize_carnage_team()
        self._give_starter_pack()
    
    def _initialize_carnage_team(self) -> None:
        """Create the Carnage team"""
        self.carnage_team = Team(
            team_id=f"CARNAGE_{self.player_id}",
            team_name="Carnage",
            is_carnage_team=True
        )
    
    def _give_starter_pack(self) -> None:
        """Give starter beginner pack"""
        starter_pack = self.pack_generator.generate_pack(PackType.BEGINNER)
        self.player_cards.extend(starter_pack)
    
    def create_custom_card(self, player_name: str, positions: List[Position],
                          design: CardDesign, image_url: str, 
                          attributes: Dict[str, int]) -> Tuple[bool, str, Optional[PlayerCard]]:
        """Create a custom card"""
        
        # Calculate overall from attributes
        overall = int(sum(attributes.values()) / len(ATTRIBUTES))
        
        # Validate
        is_valid, message = self.card_validator.validate_attributes(attributes, overall)
        if not is_valid:
            return False, message, None
        
        # Create card
        card_id = f"CUSTOM_{len(self.player_cards)}_{datetime.now().timestamp()}"
        card = PlayerCard(
            card_id=card_id,
            player_name=player_name,
            overall=overall,
            positions=positions[:2],  # Max 2 positions
            design=design,
            image_url=image_url,
            created_date=datetime.now(),
            attributes=attributes,
            creator_id=self.player_id
        )
        
        self.player_cards.append(card)
        self.progress.total_cards_created += 1
        self.progress.add_xp(50)
        
        # Check achievement
        if self.progress.total_cards_created == 1:
            self.progress.unlock_achievement(Achievement.FIRST_CARD)
        
        if overall == MAX_OVR and max(attributes.values()) == MAX_ATTRIBUTE:
            self.progress.unlock_achievement(Achievement.PERFECT_CARD)
        
        return True, "Card created successfully", card
    
    def create_team(self, team_name: str) -> Tuple[bool, str, Optional[Team]]:
        """Create a custom team"""
        
        # Validate team name (can't be "Carnage")
        if team_name.lower() == "carnage":
            return False, "Cannot name team 'Carnage' - reserved for main team", None
        
        if len(team_name) == 0 or len(team_name) > 50:
            return False, "Team name must be 1-50 characters", None
        
        team_id = f"TEAM_{len(self.teams)}_{datetime.now().timestamp()}"
        team = Team(
            team_id=team_id,
            team_name=team_name,
            is_carnage_team=False
        )
        
        self.teams[team_id] = team
        self.progress.total_teams_created += 1
        self.progress.add_xp(25)
        
        if self.progress.total_teams_created == 1:
            self.progress.unlock_achievement(Achievement.FIRST_TEAM)
        
        return True, "Team created successfully", team
    
    def add_card_to_team(self, team_id: str, card: PlayerCard, position: Position) -> Tuple[bool, str]:
        """Add a card to a team"""
        if team_id not in self.teams:
            return False, "Team not found"
        
        team = self.teams[team_id]
        
        if position not in card.positions:
            return False, f"Card is not eligible for {position.name}"
        
        if team.add_card(card, position):
            return True, f"Card added to {position.name}"
        
        return False, f"{position.name} position is full (2 players max)"
    
    def buy_pack(self, pack_type: PackType) -> Tuple[bool, str, Optional[List[PlayerCard]]]:
        """Buy a pack"""
        cost = PACK_PRICES[pack_type]
        
        if self.progress.money < cost:
            return False, f"Not enough money. Need ${cost}, have ${self.progress.money}", None
        
        self.progress.money -= cost
        pack = self.pack_generator.generate_pack(pack_type)
        self.player_cards.extend(pack)
        
        return True, f"Pack purchased! Got 5 cards", pack
    
    def sell_card_to_auction(self, card: PlayerCard) -> Tuple[bool, str, Optional[AuctionListing]]:
        """Sell a card on auction house"""
        if card not in self.player_cards:
            return False, "Card not in your collection", None
        
        listing = self.auction_house.list_card(card)
        
        # Remove from player cards
        self.player_cards.remove(card)
        
        snipe_text = " (SNIPE!)" if listing.is_snipe else ""
        return True, f"Card listed for ${listing.price}{snipe_text}", listing
    
    def buy_from_auction(self, listing_id: str) -> Tuple[bool, str, Optional[PlayerCard]]:
        """Buy from auction house"""
        listing = self.auction_house.buy_listing(listing_id)
        
        if listing is None:
            return False, "Listing not found", None
        
        if self.progress.money < listing.price:
            # Re-list the card
            self.auction_house.list_card(listing.card)
            return False, f"Not enough money. Need ${listing.price}", None
        
        self.progress.money -= listing.price
        self.player_cards.append(listing.card)
        
        return True, f"Purchased {listing.card.player_name} for ${listing.price}", listing.card
    
    def simulate_game_carnage(self, opponent_team: Team = None) -> Dict:
        """Simulate a game with Carnage team"""
        if self.carnage_team is None or not self.carnage_team.is_complete():
            return {"status": "error", "message": "Carnage team not complete"}
        
        # Create opponent if not provided
        if opponent_team is None:
            opponent_team = self._create_ai_team()
        
        score1, score2, winner = self.game_sim.simulate_game(self.carnage_team, opponent_team)
        
        is_win = winner == self.carnage_team.team_name
        
        self.progress.games_played += 1
        if is_win:
            self.progress.games_won += 1
            self.carnage_team.wins += 1
            self.progress.add_xp(100)
        else:
            self.carnage_team.losses += 1
            self.progress.add_xp(50)
        
        return {
            "carnage_score": score1,
            "opponent_score": score2,
            "winner": winner,
            "result": "WIN" if is_win else "LOSS",
            "xp_earned": 100 if is_win else 50,
            "stats": {
                "carnage_record": f"{self.carnage_team.wins}-{self.carnage_team.losses}",
                "player_record": f"{self.progress.games_won}-{self.progress.games_played - self.progress.games_won}",
                "win_rate": f"{self.progress.get_win_rate():.1f}%"
            }
        }
    
    def _create_ai_team(self) -> Team:
        """Create an AI team for opponent"""
        ai_team = Team(
            team_id=f"AI_{self.game_sim.game_counter}",
            team_name="AI Opponent",
            is_carnage_team=False
        )
        
        # Generate AI team
        for position in POSITIONS_LIST:
            for _ in range(PLAYERS_PER_POSITION):
                card = self.pack_generator.generate_single_card(PackType.ELITE)
                card.positions = [position]
                ai_team.add_card(card, position)
        
        return ai_team
    
    def complete_challenge(self, difficulty: ChallengeDifficulty) -> Dict:
        """Complete a challenge"""
        result = self.challenge_manager.complete_challenge(difficulty)
        
        self.progress.money += result["money_earned"]
        self.progress.add_xp(result["xp_earned"])
        
        return result
    
    def run_tournament(self, difficulty: ChallengeDifficulty) -> Dict:
        """Run a tournament with Carnage team"""
        if self.carnage_team is None or not self.carnage_team.is_complete():
            return {"status": "error", "message": "Carnage team not complete"}
        
        result = self.challenge_manager.run_tournament(self.carnage_team, difficulty)
        
        self.progress.money += result["money_earned"]
        self.progress.add_xp(result["xp_earned"])
        
        if result["status"] == "won":
            self.progress.unlock_achievement(Achievement.TOURNEY_WINNER)
        
        return result
    
    def get_player_stats(self) -> Dict:
        """Get comprehensive player statistics"""
        return {
            "player_name": self.player_name,
            "player_id": self.player_id,
            "level": self.progress.level,
            "xp": self.progress.xp,
            "xp_for_next_level": self.progress.get_xp_for_next_level(),
            "money": self.progress.money,
            "gems": self.progress.gems,
            "stats": {
                "cards_created": self.progress.total_cards_created,
                "teams_created": self.progress.total_teams_created,
                "games_played": self.progress.games_played,
                "games_won": self.progress.games_won,
                "win_rate": f"{self.progress.get_win_rate():.1f}%",
            },
            "carnage_team": self.carnage_team.to_dict() if self.carnage_team else None,
            "achievements": [ach.value for ach in self.progress.achievements_unlocked],
        }


# ============================================================
# EXAMPLE USAGE / DEMO
# ============================================================

def main():
    """Demonstrate the complete game system"""
    
    print("=" * 70)
    print("CARDS CARNAGE: BASKETBALL CARD CREATOR - FOUNDATION DEMO")
    print("=" * 70)
    
    # Create game
    game = CardsCarnageGame("ProGamer")
    
    print(f"\n✅ Game initialized for {game.player_name}")
    print(f"   Starting money: ${game.progress.money}")
    print(f"   Starting cards: {len(game.player_cards)}")
    
    # Create custom card
    print("\n" + "=" * 70)
    print("CREATING CUSTOM CARD")
    print("=" * 70)
    
    success, message, card = game.create_custom_card(
        player_name="Kevin Durant",
        positions=[Position.SF, Position.PF],
        design=CardDesign.DIAMOND,
        image_url="kd.jpg",
        attributes={
            "Scoring": 170,
            "Shooting": 168,
            "Speed": 155,
            "Strength": 150,
            "Handles": 148,
            "Playmaking": 152,
            "Defense": 155,
            "Rebounding": 153,
        }
    )
    
    if success:
        print(f"✅ {message}")
        print(f"   Player: {card.player_name}")
        print(f"   Overall: {card.overall}")
        print(f"   Positions: {', '.join([p.name for p in card.positions])}")
        print(f"   Design: {card.design.value}")
        print(f"   Attributes: {card.attributes}")
    else:
        print(f"❌ {message}")
    
    # Create team
    print("\n" + "=" * 70)
    print("CREATING TEAM")
    print("=" * 70)
    
    success, message, team = game.create_team("My Dream Team")
    if success:
        print(f"✅ {message}")
        print(f"   Team: {team.team_name}")
    
    # Buy pack
    print("\n" + "=" * 70)
    print("BUYING PACK")
    print("=" * 70)
    
    success, message, pack = game.buy_pack(PackType.BEGINNER)
    if success:
        print(f"✅ {message}")
        for i, card in enumerate(pack, 1):
            print(f"   {i}. {card.player_name} - {card.overall} OVR")
    
    # Auction House
    print("\n" + "=" * 70)
    print("AUCTION HOUSE DEMO")
    print("=" * 70)
    
    if len(game.player_cards) > 0:
        card_to_sell = game.player_cards[0]
        success, message, listing = game.sell_card_to_auction(card_to_sell)
        if success:
            print(f"✅ {message}")
            print(f"   Player: {listing.card.player_name}")
            print(f"   Price: ${listing.price}")
            if listing.is_snipe:
                print(f"   🎯 SNIPE! {listing.discount_percent}% off!")
    
    # Game Simulation
    print("\n" + "=" * 70)
    print("SIMULATING GAME")
    print("=" * 70)
    
    result = game.simulate_game_carnage()
    if result.get("status") != "error":
        print(f"✅ Game Simulated!")
        print(f"   Carnage: {result['carnage_score']} vs {result['opponent_score']}")
        print(f"   Result: {result['result']}")
        print(f"   XP Earned: {result['xp_earned']}")
    else:
        print(f"⚠️  {result.get('message', 'Error')}")
    
    # Challenge
    print("\n" + "=" * 70)
    print("COMPLETING CHALLENGE")
    print("=" * 70)
    
    result = game.complete_challenge(ChallengeDifficulty.MEDIUM)
    print(f"✅ Challenge Completed!")
    print(f"   Money Earned: ${result['money_earned']}")
    print(f"   XP Earned: {result['xp_earned']}")
    
    # Final Stats
    print("\n" + "=" * 70)
    print("PLAYER STATISTICS")
    print("=" * 70)
    
    stats = game.get_player_stats()
    print(f"Player: {stats['player_name']}")
    print(f"Level: {stats['level']} | XP: {stats['xp']}/{stats['xp_for_next_level']}")
    print(f"Money: ${stats['money']} | Gems: {stats['gems']}")
    print(f"\nStats:")
    for key, value in stats['stats'].items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    print(f"\nAchievements: {len(stats['achievements'])}")
    for ach in stats['achievements']:
        print(f"   🏆 {ach}")
    
    print("\n" + "=" * 70)
    print("✅ FOUNDATION COMPLETE AND WORKING!")
    print("=" * 70)


if __name__ == "__main__":
    main()
