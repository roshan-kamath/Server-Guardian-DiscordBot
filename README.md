# 🛡️ Server Guardian+

A smart Discord moderation bot powered by Google's Gemini AI that helps keep your server clean by catching toxicity, spam, and hate speech before it becomes a problem.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)
![Gemini](https://img.shields.io/badge/Google-Gemini%20API-4285F4.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ What It Does

- 🤖 **Smart Detection** - Uses Google's Gemini AI to understand context and catch toxic behavior, not just keywords
- ⚡ **Instant Response** - Catches and removes harmful messages in real-time
- ⚙️ **Fully Customizable** - Set your own warning limits and rules that fit your community
- 📊 **Transparent Logging** - Every action gets logged so moderators can review what happened
- 🔔 **Fair Warning System** - Users get warnings before facing serious consequences
- 🔇 **Auto-Timeout** - Repeat offenders get automatically muted after too many strikes
- 📋 **Easy to Track** - Clean, organized logs make moderation review simple

## 🎯 How It Works

The bot watches your server channels and runs messages through Gemini AI to detect problematic content. When something gets flagged, it immediately deletes the message, warns the user, and logs everything for your mod team. After a configurable number of warnings, users get auto-muted to give everyone a breather.

![Demo](demo-screenshot.png)
*Real example: The bot caught a vulgar word, deleted it, and warned the user—all automatically*

## 🚀 Quick Setup

### What You'll Need

- Python 3.8 or newer
- A Discord Bot Token ([get one here](https://discord.com/developers/applications))
- A Google Gemini API Key ([get one here](https://ai.google.dev/))

### Getting Started

1. **Download the code**
```bash
   git clone https://github.com/yourusername/server-guardian-plus.git
   cd server-guardian-plus
```

2. **Install what it needs**
```bash
   pip install -r requirements.txt
```

3. **Add your keys**
   
   Create a `.env` file and add:
```env
   DISCORD_TOKEN=your_discord_bot_token
   GEMINI_API_KEY=your_gemini_api_key
```

4. **Tweak the settings** (optional)
   
   Open `config.json` and adjust to your liking:
```json
   {
     "warning_threshold": 3,
     "mute_duration": 600,
     "log_channel_id": "your_log_channel_id",
     "moderation_enabled": true
   }
```

5. **Fire it up!**
```bash
   python bot.py
```

## 📝 Settings You Can Change

### config.json Options

| Setting | What It Does | Default |
|---------|-------------|---------|
| `warning_threshold` | Warnings before auto-mute kicks in | 3 |
| `mute_duration` | How long mutes last (in seconds) | 600 (10 min) |
| `log_channel_id` | Where to send mod logs | - |
| `moderation_enabled` | Turn auto-mod on/off | true |
| `toxicity_threshold` | How confident the AI needs to be (0-1) | 0.7 |

## 🎮 Commands

| Command | What It Does | Who Can Use It |
|---------|-------------|------------|
| `!warnings @user` | See how many warnings someone has | Moderators |
| `!clearwarnings @user` | Reset someone's warnings | Admins |
| `!config` | Check current settings | Admins |
| `!toggle` | Turn moderation on/off | Admins |

## 🔧 Built With

- **Python 3.8+** - The backbone of the bot
- **discord.py 2.0+** - For Discord integration
- **Google Gemini API** - The AI brain doing the heavy lifting
- **python-dotenv** - Keeps your secrets safe
- **JSON** - Simple data storage (can upgrade to a database later)

## 📂 What's Inside
```
server-guardian-plus/
│
├── bot.py                 # The main bot code
├── cogs/
│   ├── moderation.py      # Moderation commands and logic
│   └── logging.py         # Handles all the logging
├── utils/
│   ├── ai_moderator.py    # Gemini API integration
│   └── database.py        # Tracks warnings and user data
├── config.json            # Your settings
├── requirements.txt       # Everything the bot needs to run
├── .env.example          # Template for your API keys
└── README.md             # You're reading it!
```

## 🤝 Want to Contribute?

I'd love your help making this better! Here's how:

1. Fork this repo
2. Create your feature branch (`git checkout -b feature/CoolNewFeature`)
3. Commit your changes (`git commit -m 'Added something cool'`)
4. Push it up (`git push origin feature/CoolNewFeature`)
5. Open a Pull Request and let's chat!

## 📋 What's Next

Here's what I'm thinking about adding:

- [ ] Support for multiple languages
- [ ] Proper database (PostgreSQL or MongoDB)
- [ ] Web dashboard with stats and analytics
- [ ] Custom word filters you can manage
- [ ] User appeal system for false positives
- [ ] Image and media moderation

## ⚠️ Fair Warning

This bot uses AI, which is pretty smart but not perfect. You should still have human moderators review flagged content regularly. Think of this as a helpful assistant, not a replacement for your mod team.

## 📄 License

This project is licensed under the MIT License - basically, use it however you want! See the [LICENSE](LICENSE) file for the legal stuff.

## 🙏 Thanks To

- [Discord.py](https://github.com/Rapptz/discord.py) - For making Discord bots actually doable
- [Google Gemini](https://ai.google.dev/) - For the AI magic
- Everyone who tested this and gave feedback

## 📧 Let's Connect

Want to chat about the project or have questions?

**LinkedIn:** www.linkedin.com/in/roshan-kamath-9806b337b

---

⭐ If this helped your server, drop a star! It means a lot and keeps me motivated to improve it.
