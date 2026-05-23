"""
Cards Carnage: Basketball Card Creator - MAIN LAUNCHER
======================================================

This is the main entry point for the game.
It connects the game logic (foundation.py) with the database (database.py)
and provides a complete, playable experience with persistent data storage.

Run this file to start playing!
"""

import sys
from datetime import datetime
from cards_carnage_foundation import (
    CardsCarnageGame, Position, CardDesign, PackType, ChallengeDifficulty, Achievement
)
from database import CardsCarnageDatabase


class GameLauncher:
    """Main game launcher that integrates foundation and database"""
    
    def __init__(self):
        self.db = CardsCarnageDatabase("cards_carnage.db")
        self.game = None
        self.player_name = None
        self.running = True
    
    def display_title(self):
        """Display game title"""
        print("\n" + "=" * 80)
        print("CARDS CARNAGE: BASKETBALL CARD CREATOR".center(80))
        print("=" * 80)
        print("Create Custom NBA Player Cards & Build Your Team!".center(80))
        print("=" * 80 + "\n")
    
    def main_menu(self):
        """Display main menu"""
        print("\n" + "=" * 80)
        print("MAIN MENU".center(80))
        print("=" * 80)
        print("1. Start New Game")
        print("2. Continue Game")
        print("3. View Statistics")
        print("4. Exit")
        print("=" * 80)
        return input("\nSelect an option (1-4): ").strip()
    
    def start_new_game(self):
        """Start a new game"""
        print("\n" + "=" * 80)
        print("CREATE NEW PLAYER".center(80))
        print("=" * 80)
        
        self.player_name = input("\nEnter your player name: ").strip()
        
        if not self.player_name or len(self.player_name) > 50:
            print("Error - Player name must be 1-50 characters!")
            return False
        
        self.db.initialize_user_progress()
        self.db.initialize_achievements()
        
        self.game = CardsCarnageGame(self.player_name)
        
        print(f"\nWelcome, {self.player_name}!")
        print(f"Starting Stats:")
        print(f"   Money: ${self.game.progress.money}")
        print(f"   Gems: {self.game.progress.gems}")
        print(f"   Starting Cards: {len(self.game.player_cards)}")
        
        return True
    
    def continue_game(self):
        """Continue existing game"""
        progress = self.db.get_user_progress()
        
        if progress is None:
            print("\nNo saved game found! Start a new game first.")
            return False
        
        print(f"\nLoaded game!")
        print(f"Your Stats:")
        print(f"   Level: {progress['level']}")
        print(f"   Money: ${progress['money']}")
        print(f"   Gems: {progress['gems']}")
        
        self.player_name = "Loaded Player"
        self.game = CardsCarnageGame(self.player_name)
        
        return True
    
    def game_menu(self):
        """Display in-game menu"""
        print("\n" + "=" * 80)
        print("GAME MENU".center(80))
        print("=" * 80)
        print("1. Create Custom Card")
        print("2. View My Cards")
        print("3. Create Team")
        print("4. Buy Pack")
        print("5. Play Game")
        print("6. View Stats")
        print("7. Save Game")
        print("8. Back to Main Menu")
        print("=" * 80)
        return input("\nSelect an option (1-8): ").strip()
    
    def create_card_menu(self):
        """Create a custom card"""
        print("\n" + "=" * 80)
        print("CREATE CUSTOM CARD".center(80))
        print("=" * 80)
        
        player_name = input("\nEnter player name: ").strip()
        if not player_name:
            print("Error - Player name cannot be empty!")
            return
        
        print("\nAvailable Positions:")
        for i, pos in enumerate(Position, 1):
            print(f"  {i}. {pos.value}")
        
        pos1_choice = input("\nSelect primary position (1-5): ").strip()
        if not pos1_choice.isdigit() or int(pos1_choice) < 1 or int(pos1_choice) > 5:
            print("Error - Invalid choice!")
            return
        
        positions = [list(Position)[int(pos1_choice) - 1]]
        
        print("\nAvailable Card Designs:")
        for i, design in enumerate(CardDesign, 1):
            print(f"  {i}. {design.value}")
        
        design_choice = input("\nSelect card design (1-8): ").strip()
        if not design_choice.isdigit() or int(design_choice) < 1 or int(design_choice) > 8:
            print("Error - Invalid choice!")
            return
        
        design = list(CardDesign)[int(design_choice) - 1]
        
        print("\nEnter Attributes (0-170 each):")
        
        attributes = {}
        try:
            for attr in ["Scoring", "Shooting", "Speed", "Strength", "Handles", "Playmaking", "Defense", "Rebounding"]:
                value = int(input(f"  {attr}: ").strip())
                if not (0 <= value <= 170):
                    print(f"Error - {attr} must be between 0 and 170!")
                    return
                attributes[attr] = value
        except ValueError:
            print("Error - Invalid input!")
            return
        
        image_url = "default_image.png"
        
        success, message, card = self.game.create_custom_card(
            player_name=player_name,
            positions=positions,
            design=design,
            image_url=image_url,
            attributes=attributes
        )
        
        if success:
            print(f"\n✓ {message}")
            print(f"   Player: {card.player_name}")
            print(f"   Overall: {card.overall}")
            print(f"   Design: {card.design.value}")
            
            self.db.add_player_card(
                player_name=card.player_name,
                positions=[p.name for p in card.positions],
                attributes=card.attributes,
                card_design=card.design.value,
                image_url=card.image_url,
                is_custom=True
            )
            print("   Saved to database!")
        else:
            print(f"Error - {message}")
    
    def view_cards_menu(self):
        """View all created cards"""
        print("\n" + "=" * 80)
        print("MY CARDS".center(80))
        print("=" * 80)
        
        if not self.game.player_cards:
            print("\nYou have no cards yet!")
            return
        
        for i, card in enumerate(self.game.player_cards, 1):
            print(f"\n{i}. {card.player_name}")
            print(f"   Overall: {card.overall}")
            print(f"   Positions: {', '.join([p.name for p in card.positions])}")
            print(f"   Design: {card.design.value}")
    
    def create_team_menu(self):
        """Create a new team"""
        print("\n" + "=" * 80)
        print("CREATE TEAM".center(80))
        print("=" * 80)
        
        team_name = input("\nEnter team name (cannot be 'Carnage'): ").strip()
        
        success, message, team = self.game.create_team(team_name)
        
        if success:
            print(f"\n✓ {message}")
            print(f"   Team: {team.team_name}")
            
            self.db.add_team(
                team_name=team.team_name,
                pg_players=[],
                sg_players=[],
                sf_players=[],
                pf_players=[],
                c_players=[],
                team_type='custom'
            )
            print("   Saved to database!")
        else:
            print(f"Error - {message}")
    
    def buy_pack_menu(self):
        """Buy a pack"""
        print("\n" + "=" * 80)
        print("PACK SHOP".center(80))
        print("=" * 80)
        
        print(f"\nYour Money: ${self.game.progress.money}")
        print("\nAvailable Packs:")
        print("1. Beginner - $1,000")
        print("2. Rare - $2,500")
        print("3. Elite - $5,000")
        print("4. Legendary - $10,000")
        print("5. Cancel")
        
        choice = input("\nSelect a pack (1-5): ").strip()
        
        pack_map = {
            '1': PackType.BEGINNER,
            '2': PackType.RARE,
            '3': PackType.ELITE,
            '4': PackType.LEGENDARY,
        }
        
        if choice not in pack_map:
            print("Invalid choice!")
            return
        
        success, message, pack = self.game.buy_pack(pack_map[choice])
        
        if success:
            print(f"\n✓ {message}")
            for i, card in enumerate(pack, 1):
                print(f"   {i}. {card.player_name} - {card.overall} OVR")
            print(f"\nNew Money: ${self.game.progress.money}")
        else:
            print(f"Error - {message}")
    
    def play_game(self):
        """Play a game"""
        print("\n" + "=" * 80)
        print("PLAY GAME".center(80))
        print("=" * 80)
        
        if self.game.carnage_team is None or not self.game.carnage_team.is_complete():
            print("\nYour Carnage team is not complete!")
            print("Add players to your Carnage team first in the 'Build Carnage Team' menu.")
            return
        
        print("\nSimulating game...")
        result = self.game.simulate_game_carnage()
        
        if result.get("status") == "error":
            print(f"Error - {result.get('message')}")
            return
        
        print(f"\n✓ Game Complete!")
        print(f"   Carnage: {result['carnage_score']}")
        print(f"   Opponent: {result['opponent_score']}")
        print(f"   Result: {result['result']}")
        print(f"   XP Earned: +{result['xp_earned']}")
        
        self.db.add_game(
            carnage_team_id=1,
            ai_team_id=1,
            carnage_score=result['carnage_score'],
            ai_score=result['opponent_score'],
            winner=result['winner']
        )
    
    def view_stats(self):
        """View player statistics"""
        print("\n" + "=" * 80)
        print("PLAYER STATISTICS".center(80))
        print("=" * 80)
        
        stats = self.game.get_player_stats()
        
        print(f"\nPlayer: {stats['player_name']}")
        print(f"Level: {stats['level']}")
        print(f"XP: {stats['xp']}/{stats['xp_for_next_level']}")
        print(f"Money: ${stats['money']}")
        print(f"Gems: {stats['gems']}")
        
        print(f"\nStatistics:")
        for key, value in stats['stats'].items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        
        print(f"\nAchievements: {len(stats['achievements'])}")
        for ach in stats['achievements']:
            print(f"   - {ach}")
    
    def save_game(self):
        """Save game to database"""
        print("\nSaving game...")
        
        self.db.update_user_progress(
            level=self.game.progress.level,
            total_xp=self.game.progress.xp,
            money=self.game.progress.money,
            gems=self.game.progress.gems,
            total_cards_created=self.game.progress.total_cards_created,
            total_teams_created=self.game.progress.total_teams_created,
            games_won=self.game.progress.games_won
        )
        
        self.db.export_save_file("game_save.json")
        
        print("✓ Game saved successfully!")
    
    def run(self):
        """Main game loop"""
        self.display_title()
        
        while self.running:
            choice = self.main_menu()
            
            if choice == '1':
                if self.start_new_game():
                    self.game_loop()
            elif choice == '2':
                if self.continue_game():
                    self.game_loop()
            elif choice == '3':
                progress = self.db.get_user_progress()
                if progress:
                    print(f"\nGame Statistics:")
                    print(f"   Level: {progress['level']}")
                    print(f"   Money: ${progress['money']}")
                    print(f"   Cards Created: {progress['total_cards_created']}")
                    print(f"   Games Won: {progress['games_won']}")
                else:
                    print("\nNo game data found!")
            elif choice == '4':
                print("\nThanks for playing!")
                self.db.close()
                self.running = False
            else:
                print("Invalid choice!")
    
    def game_loop(self):
        """In-game loop"""
        game_running = True
        
        while game_running:
            choice = self.game_menu()
            
            if choice == '1':
                self.create_card_menu()
            elif choice == '2':
                self.view_cards_menu()
            elif choice == '3':
                self.create_team_menu()
            elif choice == '4':
                self.buy_pack_menu()
            elif choice == '5':
                self.play_game()
            elif choice == '6':
                self.view_stats()
            elif choice == '7':
                self.save_game()
            elif choice == '8':
                confirm = input("\nSave before leaving? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.save_game()
                game_running = False
            else:
                print("Invalid choice!")


# Main Entry Point
if __name__ == "__main__":
    try:
        launcher = GameLauncher()
        launcher.run()
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure all 3 files are in the same folder:")
        print("  - launcher.py")
        print("  - cards_carnage_foundation.py")
        print("  - database.py")
        sys.exit(1)
