# GitHub Internship Notifier for Discord

A Python script that monitors GitHub repositories for new internship job postings and sends Discord notifications when new opportunities are found. This tool specifically parses job tables in README.md files and alerts you immediately when new internships are posted so you don't miss any opportunities!

## 🎯 Features

- **Job Table Parsing**: Parses markdown job tables from README.md files
- **Real-time Monitoring**: Checks for new job postings every 10 minutes
- **Discord Notifications**: Sends formatted messages with job details to your Discord channel
- **State Management**: Tracks processed jobs to avoid duplicates
- **Smart Deduplication**: Creates unique job IDs based on company, role, and location
- **Error Handling**: Robust error handling and retry mechanisms
- **Easy Setup**: Automated setup script included

## 📋 Monitored Repositories

- [`vanshb03/Summer2026-Internships`](https://github.com/vanshb03/Summer2026-Internships)
- [`SimplifyJobs/Summer2026-Internships`](https://github.com/SimplifyJobs/Summer2026-Internships)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repository-url>
cd Internship-Updates
chmod +x setup.sh
./setup.sh
```

### 2. Configure Credentials

Edit the `.env` file with your credentials:

```env
GITHUB_TOKEN="your_github_personal_access_token_here"
DISCORD_TOKEN="your_discord_bot_token_here"
DISCORD_CHANNEL_ID="your_discord_channel_id_here"
```

### 3. Run the Notifier

```bash
source venv/bin/activate
python notifier.py
```

## 🔧 Manual Setup

If you prefer to set up manually:

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy the template and fill in your credentials:

```bash
cp env.template .env
# Edit .env with your credentials
```

## 🔑 Getting Credentials

### GitHub Personal Access Token

1. Go to [GitHub Settings](https://github.com/settings/tokens) > Developer settings > Personal access tokens > Tokens (classic)
2. Click "Generate new token"
3. Give it a descriptive name (e.g., `internship_notifier`)
4. Select the `repo` scope (specifically `public_repo` is sufficient)
5. Copy the generated token

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Under "Token", click "Reset Token" and copy the token
5. Enable "Message Content Intent" under "Privileged Gateway Intents"
6. Go to "OAuth2" > "URL Generator"
7. Select the `bot` scope and "Send Messages" + "Read Message History" permissions
8. Use the generated URL to invite the bot to your server

### Discord Channel ID

1. In Discord, go to User Settings > Advanced
2. Enable "Developer Mode"
3. Right-click on your desired channel and select "Copy Channel ID"

## 📁 Project Structure

```
Internship-Updates/
├── .env                    # Environment variables (create from template)
├── .gitignore             # Git ignore file
├── env.template           # Environment variables template
├── instructions.txt       # Detailed setup instructions
├── jobs.json             # State file for tracking job postings
├── notifier.py           # Main application script
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── setup.sh             # Automated setup script
└── venv/                # Virtual environment (created during setup)
```

## 📝 Usage

Once running, the bot will:

1. Check both repositories every 10 minutes
2. Parse job tables from README.md files
3. Compare current jobs with stored jobs to find new postings
4. Send a Discord notification for each new job found
5. Update the stored jobs for the next check

### Example Notification

```
🆕 New Internship Opportunity!
🏢 Company: Optiver
💼 Role: FPGA Engineer Intern
📍 Location: Austin, TX
🔗 Apply: https://optiver.com/working-at-optiver/career-opportunities/8033390002/
📂 Source: vanshb03/Summer2026-Internships
---
Apply quickly! 🚀
```

## 🔍 Troubleshooting

### Common Issues

1. **"Invalid Discord token"**: Check your `DISCORD_TOKEN` in `.env`
2. **"Could not find channel"**: Verify your `DISCORD_CHANNEL_ID` and bot permissions
3. **GitHub API rate limit**: Ensure your `GITHUB_TOKEN` is valid and has proper scope

### Logs

The script outputs helpful logs to the console:
- Connection status
- Repository checking progress
- Notification sending confirmations
- Error messages with details

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📜 License

This project is for educational and personal use.
