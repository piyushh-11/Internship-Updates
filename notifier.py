import os
import json
import asyncio
import discord
import requests
import re
from github import Github
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import hashlib

# Load environment variables
load_dotenv()

# Constants
REPOS = ["vanshb03/Summer2026-Internships", "SimplifyJobs/Summer2026-Internships"]
STATE_FILE = "jobs.json"

def load_jobs():
    """Load the stored jobs from the state file."""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # If file doesn't exist, return default structure
        return {repo: {} for repo in REPOS}
    except json.JSONDecodeError:
        # If file is corrupted, return default structure
        print(f"Warning: {STATE_FILE} is corrupted, resetting to default state")
        return {repo: {} for repo in REPOS}

def save_jobs(data):
    """Save the jobs data to the state file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def extract_url_from_html(html_content):
    """Extract the actual URL from HTML link content."""
    if not html_content:
        return None
    
    # Try to find href attribute
    href_match = re.search(r'href="([^"]*)"', html_content)
    if href_match:
        return href_match.group(1)
    
    # If no href found, return None
    return None

def create_job_id(company, role, location):
    """Create a unique identifier for a job posting."""
    # Clean up the data and create a hash
    clean_data = f"{company.strip().lower()}_{role.strip().lower()}_{location.strip().lower()}"
    return hashlib.md5(clean_data.encode()).hexdigest()

def parse_job_table(markdown_content, repo_name):
    """Parse job table from markdown content."""
    jobs = {}
    
    # Split content into lines
    lines = markdown_content.split('\n')
    
    # Find the table header
    header_line = None
    for i, line in enumerate(lines):
        if '| Company |' in line and '| Role |' in line:
            header_line = i
            break
    
    if header_line is None:
        print(f"No job table found in {repo_name}")
        return jobs
    
    # Skip header and separator lines
    current_company = None
    
    for line in lines[header_line + 2:]:  # Skip header and separator
        line = line.strip()
        if not line or not line.startswith('|'):
            continue
        
        # Parse the table row
        columns = [col.strip() for col in line.split('|')[1:-1]]  # Remove empty first/last elements
        
        if len(columns) < 4:
            continue
        
        company = columns[0].strip()
        role = columns[1].strip()
        location = columns[2].strip()
        application_link = columns[3].strip()
        
        # Handle company continuation (↳ symbol)
        if company == '↳' and current_company:
            company = current_company
        elif company and company != '↳':
            current_company = company
            # Clean up company name (remove markdown formatting)
            company = re.sub(r'\*\*|\[|\]|\(.*?\)', '', company).strip()
            current_company = company
        
        # Skip empty rows
        if not company or not role:
            continue
        
        # Extract URL from application link
        url = extract_url_from_html(application_link)
        
        # Clean up location (remove HTML tags)
        location = re.sub(r'<[^>]*>', '', location).replace('</br>', ', ').replace('<br>', ', ').strip()
        
        # Create job entry
        job_id = create_job_id(company, role, location)
        jobs[job_id] = {
            'company': company,
            'role': role,
            'location': location,
            'link': url,
            'repo': repo_name
        }
    
    return jobs

def fetch_readme_content(repo_name):
    """Fetch README.md content from GitHub repository."""
    try:
        # Initialize GitHub client
        g = Github(os.getenv("GITHUB_TOKEN"))
        
        # Get repository
        repo = g.get_repo(repo_name)
        
        # Get README.md content
        readme = repo.get_contents("README.md")
        content = readme.decoded_content.decode('utf-8')
        
        return content
    except Exception as e:
        print(f"Error fetching README for {repo_name}: {str(e)}")
        return None

def check_for_new_jobs():
    """Check for new job postings and return notifications."""
    try:
        # Load stored jobs
        stored_jobs = load_jobs()
        new_jobs = []
        
        # Check each repository
        for repo_name in REPOS:
            try:
                print(f"Checking jobs in {repo_name}...")
                
                # Fetch README content
                readme_content = fetch_readme_content(repo_name)
                if not readme_content:
                    continue
                
                # Parse job table
                current_jobs = parse_job_table(readme_content, repo_name)
                
                # Check for new jobs
                stored_repo_jobs = stored_jobs.get(repo_name, {})
                
                for job_id, job_data in current_jobs.items():
                    if job_id not in stored_repo_jobs:
                        new_jobs.append(job_data)
                        print(f"New job found: {job_data['company']} - {job_data['role']}")
                
                # Update stored jobs for this repo
                stored_jobs[repo_name] = current_jobs
                
            except Exception as e:
                print(f"Error checking {repo_name}: {str(e)}")
                continue
        
        # Save updated jobs
        save_jobs(stored_jobs)
        
        return new_jobs
        
    except Exception as e:
        print(f"Error in check_for_new_jobs: {str(e)}")
        return []

def format_job_notification(job):
    """Format a job posting for Discord notification."""
    message = (
        f"🆕 **New Internship Opportunity!**\n"
        f"🏢 **Company:** {job['company']}\n"
        f"💼 **Role:** {job['role']}\n"
        f"📍 **Location:** {job['location']}\n"
    )
    
    if job['link']:
        message += f"🔗 **Apply:** {job['link']}\n"
    
    return message

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
                f"🤖 **Internship Job Tracker Started!**\n"
                f"📊 Monitoring repositories: {', '.join(REPOS)}\n"
                f"🔄 Checking for new job postings every 10 minutes\n"
                f"💼 Tracking job tables for new opportunities\n"
                f"✅ Bot is now online and ready!"
            )
            await channel.send(startup_message)
            print(f"Sent startup message to Discord channel: {channel.name}")
        else:
            print(f"Warning: Could not find channel with ID {channel_id}")
        
        # Start the background task
        self.bg_task = self.loop.create_task(self.background_task())

    async def background_task(self):
        """Background task that checks for new jobs every 10 minutes."""
        await self.wait_until_ready()
        
        # Get the Discord channel
        channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))
        channel = self.get_channel(channel_id)
        
        if not channel:
            print(f"Error: Could not find channel with ID {channel_id}")
            return
        
        print(f"Monitoring channel: {channel.name}")
        print("Starting job monitoring loop...")
        
        while not self.is_closed():
            try:
                # Check for new jobs
                new_jobs = check_for_new_jobs()
                
                # Send notifications for new jobs
                if new_jobs:
                    for job in new_jobs:
                        message = format_job_notification(job)
                        await channel.send(message)
                        print(f"Sent job notification: {job['company']} - {job['role']}")
                        
                        # Small delay between messages to avoid rate limiting
                        await asyncio.sleep(1)
                    
                    print(f"Found and notified about {len(new_jobs)} new jobs")
                else:
                    print("No new jobs found")
                
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