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
from datetime import datetime

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

async def send_discord_notifications(new_jobs):
    """Send Discord notifications for new jobs."""
    if not new_jobs:
        print("No new jobs to notify about")
        return
    
    # Set up Discord client
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f'Logged in as {client.user} (ID: {client.user.id})')
        
        # Get the Discord channel
        channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))
        channel = client.get_channel(channel_id)
        
        if not channel:
            print(f"Error: Could not find channel with ID {channel_id}")
            await client.close()
            return
        
        print(f"Sending notifications to channel: {channel.name}")
        
        # Send notifications for new jobs
        for job in new_jobs:
            message = format_job_notification(job)
            await channel.send(message)
            print(f"Sent job notification: {job['company']} - {job['role']}")
            
            # Small delay between messages to avoid rate limiting
            await asyncio.sleep(1)
        
        print(f"Sent {len(new_jobs)} job notifications")
        await client.close()
    
    try:
        await client.start(os.getenv("DISCORD_TOKEN"))
    except discord.LoginFailure:
        print("Error: Invalid Discord token. Please check your DISCORD_TOKEN")
    except Exception as e:
        print(f"Error running Discord bot: {str(e)}")

async def send_log_message(message):
    """Send a log message to the designated log channel."""
    # Set up Discord client for logging
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f'Logged in for logging as {client.user} (ID: {client.user.id})')
        
        # Get the Discord log channel
        log_channel_id = int(os.getenv("DISCORD_LOG_CHANNEL_ID"))
        channel = client.get_channel(log_channel_id)
        
        if not channel:
            print(f"Error: Could not find log channel with ID {log_channel_id}")
            await client.close()
            return
        
        # Send the log message
        await channel.send(message)
        print(f"Sent log message to channel: {channel.name}")
        
        await client.close()
    
    try:
        await client.start(os.getenv("DISCORD_TOKEN"))
    except discord.LoginFailure:
        print("Error: Invalid Discord token for logging. Please check your DISCORD_TOKEN")
    except Exception as e:
        print(f"Error sending log message: {str(e)}")

async def main():
    """Main function to run the job checker once."""
    # Check if all required environment variables are set
    required_vars = ["GITHUB_TOKEN", "DISCORD_TOKEN", "DISCORD_CHANNEL_ID", "DISCORD_LOG_CHANNEL_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return
    
    # Log start of execution
    start_time = datetime.now()
    start_message = f"🚀 **Job Checker Started**\n📅 Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n🔍 Checking repositories: {', '.join(REPOS)}"
    await send_log_message(start_message)
    
    # Check for new jobs
    print("Starting job check...")
    new_jobs = check_for_new_jobs()
    
    # Send notifications if new jobs found
    if new_jobs:
        print(f"Found {len(new_jobs)} new jobs, sending Discord notifications...")
        await send_discord_notifications(new_jobs)
        result_message = f"✅ **Job Check Complete**\n📊 New jobs found: {len(new_jobs)}\n📢 Notifications sent successfully"
    else:
        print("No new jobs found")
        result_message = f"✅ **Job Check Complete**\n📊 New jobs found: 0\n💤 No notifications needed"
    
    # Log completion
    end_time = datetime.now()
    duration = end_time - start_time
    final_message = f"{result_message}\n⏱️ Duration: {duration.total_seconds():.2f} seconds\n📅 Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
    await send_log_message(final_message)

if __name__ == "__main__":
    asyncio.run(main())