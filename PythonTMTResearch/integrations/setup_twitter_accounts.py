"""
Setup script for adding Twitter accounts to twscrape
Run this once to configure Twitter accounts for scraping

SECURITY NOTE: Do NOT commit actual credentials to version control
"""
import asyncio
from twscrape import API


async def setup_accounts():
    """
    Interactive setup for Twitter accounts
    
    NOTE: You need at least 1-2 Twitter accounts for scraping
    Free Twitter accounts work, but may get rate-limited or suspended
    """
    api = API()
    
    print("=" * 60)
    print("Twitter Account Setup for Social News Scraping")
    print("=" * 60)
    print()
    print("You need to add at least one Twitter account for scraping.")
    print("Free accounts work, but consider using dedicated scraper accounts.")
    print()
    print("WARNING: Scraping may violate Twitter's ToS and accounts may get suspended.")
    print("Use at your own risk with accounts you can afford to lose.")
    print()
    
    # Check existing accounts
    accounts = await api.pool.accounts_info()
    if accounts:
        print(f"\n✓ Found {len(accounts)} existing account(s) configured:")
        for acc in accounts:
            print(f"  - {acc.username}")
        print()
    
    add_more = input("Add a new Twitter account? (y/n): ").lower().strip()
    
    while add_more == 'y':
        print("\nEnter Twitter account credentials:")
        username = input("Username (without @): ").strip()
        password = input("Password: ").strip()
        email = input("Email: ").strip()
        email_password = input("Email password: ").strip()
        
        print(f"\nAdding account @{username}...")
        try:
            await api.pool.add_account(username, password, email, email_password)
            print(f"✓ Account @{username} added successfully!")
            
            # Try to login
            print("Testing login...")
            await api.pool.login_all()
            print("✓ Login successful!")
            
        except Exception as e:
            print(f"✗ Error adding account: {e}")
        
        add_more = input("\nAdd another account? (y/n): ").lower().strip()
    
    # Show final status
    accounts = await api.pool.accounts_info()
    print(f"\n{'='*60}")
    print(f"Setup complete! {len(accounts)} account(s) configured.")
    print(f"{'='*60}")
    
    if accounts:
        print("\nYou can now run the social news service:")
        print("  python integrations/social_news_service.py")
    else:
        print("\nNo accounts configured. Social news scraping will not work.")
        print("Re-run this script to add accounts.")


if __name__ == "__main__":
    asyncio.run(setup_accounts())
