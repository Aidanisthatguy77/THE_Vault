#!/usr/bin/env python3
"""
NBA 2K Legacy Vault Backend API Test Suite
Tests all CRUD operations, comments, email subscriptions, and admin auth
"""

import requests
import sys
import json
from datetime import datetime

class LegacyVaultAPITester:
    def __init__(self, base_url="https://classic-2k.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_games = []
        self.created_comments = []
        self.subscribed_emails = []

    def log_test(self, name, success, response_code=None, error=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED (Status: {response_code})")
        else:
            print(f"❌ {name} - FAILED (Status: {response_code}, Error: {error})")
        return success

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_base}/{endpoint}" if not endpoint.startswith('http') else endpoint
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=10)

            success = response.status_code == expected_status
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {}
                
            return self.log_test(name, success, response.status_code), response_data, response.status_code

        except Exception as e:
            return self.log_test(name, False, None, str(e)), {}, None

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, data, status = self.run_test("Root API Endpoint", "GET", "", 200)
        return success

    def test_seed_games(self):
        """Test game seeding"""
        success, data, status = self.run_test("Seed Games", "POST", "seed", 200)
        if success:
            print(f"   Seeded {data.get('count', 'unknown')} games")
        return success

    def test_get_games(self):
        """Test getting active games"""
        success, data, status = self.run_test("Get Active Games", "GET", "games", 200)
        if success and isinstance(data, list):
            print(f"   Found {len(data)} active games")
            return len(data) >= 0  # Should return a list
        return False

    def test_get_all_games(self):
        """Test getting all games (admin route)"""
        success, data, status = self.run_test("Get All Games (Admin)", "GET", "games/all", 200)
        if success and isinstance(data, list):
            print(f"   Found {len(data)} total games")
            return len(data) >= 0
        return False

    def test_create_game(self):
        """Test creating a new game"""
        test_game = {
            "title": "NBA 2K Test Game",
            "year": "2024", 
            "cover_image": "https://example.com/test.jpg",
            "hook_text": "Test game for API validation",
            "cover_athletes": "Test Player",
            "description": "This is a test game created during API testing",
            "youtube_embed": "https://www.youtube.com/embed/test",
            "order": 99,
            "is_active": True
        }
        
        success, data, status = self.run_test("Create Game", "POST", "games", 200, test_game)
        if success and 'id' in data:
            self.created_games.append(data['id'])
            print(f"   Created game with ID: {data['id']}")
        return success

    def test_get_single_game(self):
        """Test getting a single game by ID"""
        if not self.created_games:
            print("❌ Get Single Game - SKIPPED (No game ID available)")
            return False
            
        game_id = self.created_games[0]
        success, data, status = self.run_test("Get Single Game", "GET", f"games/{game_id}", 200)
        if success:
            print(f"   Retrieved game: {data.get('title', 'Unknown')}")
        return success

    def test_update_game(self):
        """Test updating a game"""
        if not self.created_games:
            print("❌ Update Game - SKIPPED (No game ID available)")
            return False
            
        game_id = self.created_games[0]
        update_data = {
            "title": "NBA 2K Test Game - Updated",
            "hook_text": "Updated test game"
        }
        
        success, data, status = self.run_test("Update Game", "PUT", f"games/{game_id}", 200, update_data)
        if success:
            print(f"   Updated game title: {data.get('title', 'Unknown')}")
        return success

    def test_toggle_game_visibility(self):
        """Test toggling game visibility"""
        if not self.created_games:
            print("❌ Toggle Game Visibility - SKIPPED (No game ID available)")
            return False
            
        game_id = self.created_games[0]
        toggle_data = {"is_active": False}
        
        success, data, status = self.run_test("Toggle Game Visibility", "PUT", f"games/{game_id}", 200, toggle_data)
        if success:
            print(f"   Game visibility set to: {data.get('is_active', 'Unknown')}")
        return success

    def test_create_comment(self):
        """Test creating a comment"""
        comment_data = {
            "author_name": "Test User",
            "content": "This is a test comment for the Legacy Vault concept!"
        }
        
        success, data, status = self.run_test("Create Comment", "POST", "comments", 200, comment_data)
        if success and 'id' in data:
            self.created_comments.append(data['id'])
            print(f"   Created comment with ID: {data['id']}")
        return success

    def test_get_comments(self):
        """Test getting comments"""
        success, data, status = self.run_test("Get Comments", "GET", "comments", 200)
        if success and isinstance(data, list):
            print(f"   Found {len(data)} comments")
        return success

    def test_create_reply(self):
        """Test creating a reply to a comment"""
        if not self.created_comments:
            print("❌ Create Reply - SKIPPED (No comment ID available)")
            return False
            
        parent_id = self.created_comments[0]
        reply_data = {
            "author_name": "Reply User",
            "content": "This is a reply to the test comment",
            "parent_id": parent_id
        }
        
        success, data, status = self.run_test("Create Reply", "POST", "comments", 200, reply_data)
        if success and 'id' in data:
            print(f"   Created reply with ID: {data['id']}")
        return success

    def test_email_subscription(self):
        """Test email subscription"""
        test_email = f"test-{datetime.now().strftime('%H%M%S')}@example.com"
        subscription_data = {"email": test_email}
        
        success, data, status = self.run_test("Email Subscription", "POST", "subscribe", 201, subscription_data)
        if success:
            self.subscribed_emails.append(test_email)
            print(f"   Subscribed email: {test_email}")
        return success

    def test_duplicate_subscription(self):
        """Test duplicate email subscription (should fail)"""
        if not self.subscribed_emails:
            print("❌ Duplicate Subscription - SKIPPED (No subscribed email)")
            return False
            
        email = self.subscribed_emails[0]
        subscription_data = {"email": email}
        
        success, data, status = self.run_test("Duplicate Subscription (Should Fail)", "POST", "subscribe", 400, subscription_data)
        return success

    def test_get_subscriptions(self):
        """Test getting all subscriptions"""
        success, data, status = self.run_test("Get Subscriptions", "GET", "subscriptions", 200)
        if success and isinstance(data, list):
            print(f"   Found {len(data)} subscriptions")
        return success

    def test_admin_login_success(self):
        """Test admin login with correct password"""
        login_data = {"password": "legacyvault2k"}
        success, data, status = self.run_test("Admin Login (Correct)", "POST", "admin/login", 200, login_data)
        if success:
            print(f"   Login successful: {data.get('message', 'Success')}")
        return success

    def test_admin_login_failure(self):
        """Test admin login with wrong password"""
        login_data = {"password": "wrongpassword"}
        success, data, status = self.run_test("Admin Login (Wrong Password)", "POST", "admin/login", 401, login_data)
        return success

    def test_delete_comment(self):
        """Test deleting a comment"""
        if not self.created_comments:
            print("❌ Delete Comment - SKIPPED (No comment ID available)")
            return False
            
        comment_id = self.created_comments[0]
        success, data, status = self.run_test("Delete Comment", "DELETE", f"comments/{comment_id}", 200)
        if success:
            print(f"   Deleted comment: {data.get('message', 'Success')}")
        return success

    def test_delete_game(self):
        """Test deleting a game"""
        if not self.created_games:
            print("❌ Delete Game - SKIPPED (No game ID available)")
            return False
            
        game_id = self.created_games[0]
        success, data, status = self.run_test("Delete Game", "DELETE", f"games/{game_id}", 200)
        if success:
            print(f"   Deleted game: {data.get('message', 'Success')}")
        return success

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🏀 NBA 2K Legacy Vault API Test Suite")
        print("=" * 50)
        
        # Basic API Tests
        print("\n📡 Basic API Tests")
        self.test_root_endpoint()
        
        # Game CRUD Tests
        print("\n🎮 Game Management Tests")
        self.test_seed_games()
        self.test_get_games()
        self.test_get_all_games()
        self.test_create_game()
        self.test_get_single_game()
        self.test_update_game()
        self.test_toggle_game_visibility()
        
        # Comment Tests
        print("\n💬 Comment System Tests")
        self.test_create_comment()
        self.test_get_comments()
        self.test_create_reply()
        
        # Email Subscription Tests  
        print("\n📧 Email Subscription Tests")
        self.test_email_subscription()
        self.test_duplicate_subscription()
        self.test_get_subscriptions()
        
        # Admin Authentication Tests
        print("\n🔐 Admin Authentication Tests")
        self.test_admin_login_success()
        self.test_admin_login_failure()
        
        # Cleanup Tests
        print("\n🗑️  Cleanup Tests")
        self.test_delete_comment()
        self.test_delete_game()
        
        # Final Results
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} PASSED")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests PASSED! Backend API is working correctly.")
            return 0
        else:
            print("⚠️  Some tests FAILED. Check the backend implementation.")
            return 1

def main():
    tester = LegacyVaultAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())