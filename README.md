# GitHub Internship Notifier for Discord

A Python script that monitors GitHub repositories for new internship postings and sends Discord notifications when updates are detected. This tool specifically watches for new commits in internship repositories and alerts you immediately so you don't miss any opportunities!

## 🎯 Features

- **Real-time Monitoring**: Checks for new commits every 10 minutes
- **Discord Notifications**: Sends formatted messages to your Discord channel
- **State Management**: Tracks processed commits to avoid duplicates
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
├── last_commits.json      # State file for tracking commits
├── notifier.py           # Main application script
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── setup.sh             # Automated setup script
└── venv/                # Virtual environment (created during setup)
```

## 📝 Usage

Once running, the bot will:

1. Check both repositories every 10 minutes
2. Compare the latest commit SHA with the stored SHA
3. Send a Discord notification if a new commit is found
4. Update the stored SHA for the next check

### Example Notification

```
🚨 New commit detected in vanshb03/Summer2026-Internships!
📝 Message: Add new internship opportunities for December 2024
👤 Author: John Doe
🔗 Link: https://github.com/vanshb03/Summer2026-Internships/commit/abc123
📅 Date: 2024-12-19 10:30:00
---
Check for new internship opportunities! 🎯
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
