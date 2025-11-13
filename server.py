import discord
import logging
from discord.ext import commands
import openai
import json
import asyncio
from datetime import datetime
from collections import defaultdict
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration/intents for the bot
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Storage for user violations
user_violations = defaultdict(int)

# Configuration settings
config = {
    "toxicity_threshold": 0.7,
    "spam_threshold": 5,
    "auto_mute_violations": 3,
    "mute_duration": 600,
    "mod_log_channel": None,
    "enabled": True
}

# Message tracking for spam detection
user_messages = defaultdict(list)

# OpenAI client setup
openai.api_key = os.getenv('OPENAI_API_KEY')


@bot.event
async def on_ready():
    print(f"We are ready to hop in, {bot.user}")


async def analyze_message_toxicity(content):
    """Analyze message using OpenAI for toxicity detection"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """You are a content moderation AI. Analyze the message and return a JSON object with:
                - toxicity_score: 0-1 (0 = safe, 1 = highly toxic)
                - categories: list of issues found (hate_speech, harassment, spam, threats, nsfw, etc)
                - reason: brief explanation
                Only flag genuinely problematic content. Consider context and intent."""},
                {"role": "user", "content": f"Analyze this message: {content}"}
            ],
            temperature=0.3
        )

        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"Error analyzing message: {e}")
        return {"toxicity_score": 0, "categories": [], "reason": "Analysis failed"}


async def check_spam(user_id):
    """Check if user is spamming"""
    current_time = datetime.now().timestamp()
    user_messages[user_id] = [t for t in user_messages[user_id] if current_time - t < 10]
    user_messages[user_id].append(current_time)
    return len(user_messages[user_id]) >= config["spam_threshold"]


async def log_to_mod_channel(guild, embed):
    """Log moderation action to mod channel"""
    if config["mod_log_channel"]:
        channel = guild.get_channel(config["mod_log_channel"])
        if channel:
            await channel.send(embed=embed)


@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author == bot.user:
        return

    # Process commands first
    await bot.process_commands(message)

    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} - don't use that word!")
        return

    # Skip if GuardianServer+ is disabled
    if not config["enabled"]:
        return

    # Check for spam
    is_spam = await check_spam(message.author.id)
    if is_spam:
        await handle_violation(message, "spam", "Rapid message sending detected", 0.9)
        return

    # Analyze message with AI
    analysis = await analyze_message_toxicity(message.content)

    if analysis["toxicity_score"] >= config["toxicity_threshold"]:
        await handle_violation(
            message,
            ", ".join(analysis["categories"]),
            analysis["reason"],
            analysis["toxicity_score"]
        )


@bot.event
async def on_member_join(member):
    # Send welcome message to a channel (you can set which channel)
    # Option 1: Send to system channel (default welcome channel)
    if member.guild.system_channel:
        await member.guild.system_channel.send(f"Welcome {member.mention}! WE HOPE YOU BROUGHT SOME PASTA 🍝")

    # Option 2: Also send a DM to the member
    try:
        await member.send(f"Welcome to {member.guild.name}! WE HOPE YOU BROUGHT SOME PASTA 🍝")
    except discord.Forbidden:
        print(f"Could not DM {member.name}")


async def handle_violation(message, violation_type, reason, score):
    """Handle a content violation"""
    user_violations[message.author.id] += 1
    violation_count = user_violations[message.author.id]

    # Delete the message
    try:
        await message.delete()
    except:
        pass

    # Create log embed
    embed = discord.Embed(
        title="🚨 Content Violation Detected",
        color=discord.Color.red(),
        timestamp=datetime.now()
    )
    embed.add_field(name="User", value=f"{message.author.mention} ({message.author})", inline=False)
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)
    embed.add_field(name="Violation Type", value=violation_type, inline=True)
    embed.add_field(name="Toxicity Score", value=f"{score:.2f}", inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Message Content", value=message.content[:1024], inline=False)
    embed.add_field(name="Violation Count", value=f"{violation_count}/{config['auto_mute_violations']}", inline=True)
    embed.set_footer(text=f"User ID: {message.author.id}")

    # Log to mod channel
    await log_to_mod_channel(message.guild, embed)

    # Warn user
    try:
        warning_embed = discord.Embed(
            title="⚠️ Warning",
            description=f"Your message was removed for: **{violation_type}**\n\n{reason}",
            color=discord.Color.orange()
        )
        warning_embed.add_field(
            name="Violations",
            value=f"{violation_count}/{config['auto_mute_violations']} (Auto-mute threshold)",
            inline=False
        )
        await message.author.send(embed=warning_embed)
    except:
        pass

    # Auto-mute if threshold reached
    if violation_count >= config["auto_mute_violations"]:
        await auto_mute_user(message.guild, message.author)


async def auto_mute_user(guild, member):
    """Automatically mute a user"""
    try:
        # Get or create muted role
        muted_role = discord.utils.get(guild.roles, name="Muted")
        if not muted_role:
            muted_role = await guild.create_role(name="Muted", reason="Auto-mute by Server Guardian+")
            # Set permissions for muted role
            for channel in guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False)

        await member.add_roles(muted_role, reason="Auto-muted: Exceeded violation threshold")

        # Schedule unmute
        await asyncio.sleep(config["mute_duration"])
        await member.remove_roles(muted_role, reason="Auto-mute duration expired")

        # Log unmute
        unmute_embed = discord.Embed(
            title="🔓 User Auto-Unmuted",
            description=f"{member.mention} has been unmuted after {config['mute_duration']}s",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        await log_to_mod_channel(guild, unmute_embed)

    except Exception as e:
        print(f"Error muting user: {e}")


# Admin Commands
@bot.command(name='config')
@commands.has_permissions(administrator=True)
async def show_config(ctx):
    """Show current configuration"""
    embed = discord.Embed(title="🛡️ Server Guardian+ Configuration", color=discord.Color.blue())
    embed.add_field(name="Status", value="✅ Enabled" if config["enabled"] else "❌ Disabled", inline=True)
    embed.add_field(name="Toxicity Threshold", value=f"{config['toxicity_threshold']}", inline=True)
    embed.add_field(name="Spam Threshold", value=f"{config['spam_threshold']} msgs/10s", inline=True)
    embed.add_field(name="Auto-Mute After", value=f"{config['auto_mute_violations']} violations", inline=True)
    embed.add_field(name="Mute Duration", value=f"{config['mute_duration']}s", inline=True)

    mod_channel = ctx.guild.get_channel(config["mod_log_channel"]) if config["mod_log_channel"] else None
    embed.add_field(name="Mod Log Channel", value=mod_channel.mention if mod_channel else "Not set", inline=True)

    await ctx.send(embed=embed)


@bot.command(name='setlogchannel')
@commands.has_permissions(administrator=True)
async def set_log_channel(ctx, channel: discord.TextChannel):
    """Set the mod log channel"""
    config["mod_log_channel"] = channel.id
    await ctx.send(f"✅ Mod log channel set to {channel.mention}")


@bot.command(name='setthreshold')
@commands.has_permissions(administrator=True)
async def set_threshold(ctx, threshold: float):
    """Set toxicity threshold (0-1)"""
    if 0 <= threshold <= 1:
        config["toxicity_threshold"] = threshold
        await ctx.send(f"✅ Toxicity threshold set to {threshold}")
    else:
        await ctx.send("❌ Threshold must be between 0 and 1")


@bot.command(name='toggle')
@commands.has_permissions(administrator=True)
async def toggle_guardian(ctx):
    """Enable/disable the guardian"""
    config["enabled"] = not config["enabled"]
    status = "enabled" if config["enabled"] else "disabled"
    await ctx.send(f"✅ Server Guardian+ {status}")


@bot.command(name='resetviolations')
@commands.has_permissions(administrator=True)
async def reset_violations(ctx, member: discord.Member):
    """Reset violation count for a user"""
    user_violations[member.id] = 0
    await ctx.send(f"✅ Violations reset for {member.mention}")


@bot.command(name='violations')
@commands.has_permissions(administrator=True)
async def show_violations(ctx, member: discord.Member = None):
    """Show violation count for a user or top violators"""
    if member:
        count = user_violations[member.id]
        await ctx.send(f"{member.mention} has {count} violation(s)")
    else:
        if not user_violations:
            await ctx.send("No violations recorded yet")
            return

        # Show top 10 violators
        sorted_violations = sorted(user_violations.items(), key=lambda x: x[1], reverse=True)[:10]
        embed = discord.Embed(title="📊 Top Violators", color=discord.Color.red())

        for user_id, count in sorted_violations:
            member = ctx.guild.get_member(user_id)
            if member:
                embed.add_field(name=str(member), value=f"{count} violations", inline=False)

        await ctx.send(embed=embed)


@bot.command(name='help')
async def help_command(ctx):
    """Show help information"""
    embed = discord.Embed(
        title="🛡️ Server Guardian+ Help",
        description="Next-gen AI-powered moderation bot",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Admin Commands",
        value="""
        `!config` - View current configuration
        `!setlogchannel #channel` - Set mod log channel
        `!setthreshold <0-1>` - Set toxicity threshold
        `!toggle` - Enable/disable guardian
        `!resetviolations @user` - Reset user violations
        `!violations [@user]` - View violations
        """,
        inline=False
    )

    embed.add_field(
        name="Features",
        value="""
        ✅ AI-powered toxicity detection
        ✅ Contextual content analysis
        ✅ Spam detection
        ✅ Auto-warn system
        ✅ Auto-mute after threshold
        ✅ Comprehensive logging
        """,
        inline=False
    )

    await ctx.send(embed=embed)


# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables")
    else:
        bot.run(token, log_handler=handler, log_level=logging.DEBUG)
