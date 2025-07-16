import os
import json
import asyncio
import discord
from github import Github
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
REPOS = ["vanshb03/Summer2026-Internships", "SimplifyJobs/Summer2026-Internships"]
STATE_FILE = "last_commits.json"

def load_last_commits():
    """Load the last known commit SHAs from the state file."""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # If file doesn't exist, return default structure
        return {repo: None for repo in REPOS}
    except json.JSONDecodeError:
        # If file is corrupted, return default structure
        print(f"Warning: {STATE_FILE} is corrupted, resetting to default state")
        return {repo: None for repo in REPOS}

def save_last_commits(data):
    """Save the last known commit SHAs to the state file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def check_github_for_new_commits():
    """Check GitHub repositories for new commits and return notifications."""
    try:
        # Initialize GitHub client
        g = Github(os.getenv("GITHUB_TOKEN"))
        
        # Load last known commits
        last_commits = load_last_commits()
        notifications = []
        
        # Check each repository
        for repo_name in REPOS:
            try:
                print(f"Checking {repo_name}...")
                
                # Get repository object
                repo = g.get_repo(repo_name)
                
                # Get the latest commit on the main branch
                commits = repo.get_commits(sha=repo.default_branch)
                latest_commit = commits[0]
                
                # Check if this is a new commit
                if (last_commits[repo_name] != latest_commit.sha and 
                    last_commits[repo_name] is not None):
                    
                    # Create notification message
                    message = (
                        f"🚨 **New commit detected in {repo_name}!**\n"
                        f"📝 **Message:** {latest_commit.commit.message}\n"
                        f"👤 **Author:** {latest_commit.commit.author.name}\n"
                        f"🔗 **Link:** {latest_commit.html_url}\n"
                        f"📅 **Date:** {latest_commit.commit.author.date}\n"
                        f"---\n"
                        f"Check for new internship opportunities! 🎯"
                    )
                    notifications.append(message)
                    print(f"New commit found in {repo_name}")
                
                # Update the last commit SHA for this repo
                last_commits[repo_name] = latest_commit.sha
                
            except Exception as e:
                print(f"Error checking {repo_name}: {str(e)}")
                continue
        
        # Save updated commit SHAs
        save_last_commits(last_commits)
        
        return notifications
        
    except Exception as e:
        print(f"Error in check_github_for_new_commits: {str(e)}")
        return []

class InternshipNotifier(discord.Client):
    def __init__(self, *args, **kwargs):
        # Set up intents for Discord bot
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, *args, **kwargs)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        
        # Send startup message to Discord channel
        channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))
        channel = self.get_channel(channel_id)
        
        if channel:
            startup_message = (
                f"🤖 **Internship Bot Started!**\n"
                f"📊 Monitoring repositories: {', '.join(REPOS)}\n"
                f"🔄 Checking for updates every 10 minutes\n"
                f"✅ Bot is now online and ready!"
            )
            await channel.send(startup_message)
            print(f"Sent startup message to Discord channel: {channel.name}")
        else:
            print(f"Warning: Could not find channel with ID {channel_id}")
        
        # Start the background task
        self.bg_task = self.loop.create_task(self.background_task())

    async def background_task(self):
        """Background task that checks for new commits every 10 minutes."""
        await self.wait_until_ready()
        
        # Get the Discord channel
        channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))
        channel = self.get_channel(channel_id)
        
        if not channel:
            print(f"Error: Could not find channel with ID {channel_id}")
            return
        
        print(f"Monitoring channel: {channel.name}")
        print("Starting monitoring loop...")
        
        while not self.is_closed():
            try:
                # Check for new commits
                notifications = check_github_for_new_commits()
                
                # Send notifications if any
                if notifications:
                    for message in notifications:
                        await channel.send(message)
                        print(f"Sent notification to Discord")
                else:
                    print("No new commits found")
                
                # Wait 10 minutes before next check
                await asyncio.sleep(600)  # 600 seconds = 10 minutes
                
            except Exception as e:
                print(f"Error in background task: {str(e)}")
                await asyncio.sleep(600)  # Wait before retrying

def main():
    """Main function to run the Discord bot."""
    # Check if all required environment variables are set
    required_vars = ["GITHUB_TOKEN", "DISCORD_TOKEN", "DISCORD_CHANNEL_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease copy env.template to .env and fill in your credentials.")
        return
    
    # Create and run the Discord client
    client = InternshipNotifier()
    
    try:
        client.run(os.getenv("DISCORD_TOKEN"))
    except discord.LoginFailure:
        print("Error: Invalid Discord token. Please check your DISCORD_TOKEN in .env")
    except Exception as e:
        print(f"Error running Discord bot: {str(e)}")

if __name__ == "__main__":
    main() 