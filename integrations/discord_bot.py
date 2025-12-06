"""
Discord Bot for Multi-Agent Chatroom.

This module provides Discord integration, allowing users to relay messages
between a Discord channel and the AI chatroom.
"""

import asyncio
import logging
from typing import Optional, Dict
import json

import disnake
from disnake.ext import commands

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import (
    DISCORD_BOT_TOKEN,
    DISCORD_GUILD_ID,
    LOG_LEVEL,
    LOG_FORMAT
)
from core.chatroom import Chatroom, get_chatroom
from core.models import Message

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class ChatroomBot(commands.Bot):
    """
    Discord bot for Multi-Agent Chatroom integration.
    
    Features:
    - /joinroom - Connect a Discord channel to the AI chatroom
    - /leaveroom - Disconnect from the chatroom
    - /send - Send a message to the AI chatroom
    - /agents - List active agents
    - /status - Get chatroom status
    
    Messages from AI agents are relayed to connected Discord channels.
    """
    
    def __init__(self):
        """Initialize the Discord bot."""
        intents = disnake.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            test_guilds=[int(DISCORD_GUILD_ID)] if DISCORD_GUILD_ID else None
        )
        
        self._chatroom: Optional[Chatroom] = None
        self._connected_channels: Dict[int, int] = {}  # channel_id: guild_id
        self._setup_commands()
    
    def _setup_commands(self):
        """Register slash commands."""
        
        @self.slash_command(name="joinroom", description="Connect this channel to the AI chatroom")
        async def joinroom(inter: disnake.ApplicationCommandInteraction):
            """Connect the current channel to the chatroom."""
            channel_id = inter.channel_id
            guild_id = inter.guild_id
            
            if channel_id in self._connected_channels:
                await inter.response.send_message(
                    "This channel is already connected to the chatroom!",
                    ephemeral=True
                )
                return
            
            self._connected_channels[channel_id] = guild_id
            
            # Subscribe to chatroom messages
            await self._ensure_chatroom()
            
            embed = disnake.Embed(
                title="Connected to AI Chatroom",
                description="This channel is now receiving messages from the AI chatroom.\n\n"
                           "Use `/send <message>` to send messages to the AI agents.\n"
                           "Use `/leaveroom` to disconnect.",
                color=disnake.Color.green()
            )
            
            # Add agents info
            if self._chatroom:
                status = self._chatroom.get_status()
                agents = status.get("active_agents", [])
                if agents:
                    agent_names = [a["name"] for a in agents]
                    embed.add_field(
                        name="Active Agents",
                        value=", ".join(agent_names),
                        inline=False
                    )
            
            await inter.response.send_message(embed=embed)
            logger.info(f"Discord channel {channel_id} connected to chatroom")
        
        @self.slash_command(name="leaveroom", description="Disconnect this channel from the AI chatroom")
        async def leaveroom(inter: disnake.ApplicationCommandInteraction):
            """Disconnect the current channel from the chatroom."""
            channel_id = inter.channel_id
            
            if channel_id not in self._connected_channels:
                await inter.response.send_message(
                    "This channel is not connected to the chatroom.",
                    ephemeral=True
                )
                return
            
            del self._connected_channels[channel_id]
            
            embed = disnake.Embed(
                title="Disconnected from AI Chatroom",
                description="This channel will no longer receive chatroom messages.",
                color=disnake.Color.orange()
            )
            
            await inter.response.send_message(embed=embed)
            logger.info(f"Discord channel {channel_id} disconnected from chatroom")
        
        @self.slash_command(name="send", description="Send a message to the AI chatroom")
        async def send(
            inter: disnake.ApplicationCommandInteraction,
            message: str = commands.Param(description="Your message to send")
        ):
            """Send a message to the chatroom."""
            await inter.response.defer()
            
            await self._ensure_chatroom()
            
            if not self._chatroom:
                await inter.followup.send(
                    "Chatroom is not available.",
                    ephemeral=True
                )
                return
            
            # Send message to chatroom
            username = f"{inter.author.display_name} (Discord)"
            user_id = f"discord_{inter.author.id}"
            
            await self._chatroom.add_human_message(
                content=message,
                username=username,
                user_id=user_id
            )
            
            # Trigger agent responses
            asyncio.create_task(self._chatroom.trigger_response_to_human())
            
            embed = disnake.Embed(
                description=f"**{inter.author.display_name}**: {message}",
                color=disnake.Color.blue()
            )
            embed.set_footer(text="Message sent to AI chatroom")
            
            await inter.followup.send(embed=embed)
        
        @self.slash_command(name="agents", description="List active AI agents in the chatroom")
        async def agents(inter: disnake.ApplicationCommandInteraction):
            """List all active agents."""
            await self._ensure_chatroom()
            
            if not self._chatroom:
                await inter.response.send_message(
                    "Chatroom is not available.",
                    ephemeral=True
                )
                return
            
            status = self._chatroom.get_status()
            agents_list = status.get("active_agents", [])
            
            embed = disnake.Embed(
                title="Active AI Agents",
                color=disnake.Color.purple()
            )
            
            if agents_list:
                for agent in agents_list:
                    embed.add_field(
                        name=agent["name"],
                        value=f"Model: `{agent['model']}`\n{agent.get('persona', 'No description')}",
                        inline=False
                    )
            else:
                embed.description = "No agents currently active."
            
            await inter.response.send_message(embed=embed)
        
        @self.slash_command(name="status", description="Get AI chatroom status")
        async def status(inter: disnake.ApplicationCommandInteraction):
            """Get chatroom status."""
            await self._ensure_chatroom()
            
            if not self._chatroom:
                await inter.response.send_message(
                    "Chatroom is not available.",
                    ephemeral=True
                )
                return
            
            status_data = self._chatroom.get_status()
            
            embed = disnake.Embed(
                title="Chatroom Status",
                color=disnake.Color.green() if status_data["is_running"] else disnake.Color.red()
            )
            
            embed.add_field(name="Running", value="Yes" if status_data["is_running"] else "No", inline=True)
            embed.add_field(name="Round", value=str(status_data["round_number"]), inline=True)
            embed.add_field(name="Messages", value=str(status_data["message_count"]), inline=True)
            embed.add_field(name="Agents", value=str(len(status_data["active_agents"])), inline=True)
            embed.add_field(name="Humans", value=str(status_data["connected_humans"]), inline=True)
            embed.add_field(name="Discord Channels", value=str(len(self._connected_channels)), inline=True)
            
            await inter.response.send_message(embed=embed)
    
    async def _ensure_chatroom(self):
        """Ensure chatroom is initialized and subscribed."""
        if self._chatroom is None:
            self._chatroom = await get_chatroom()
            self._chatroom.on_message(self._on_chatroom_message)
    
    async def _on_chatroom_message(self, message: Message):
        """
        Handle messages from the chatroom.
        
        Relays messages to all connected Discord channels.
        
        Args:
            message: The chatroom message
        """
        if not self._connected_channels:
            return
        
        # Don't relay messages from Discord users back to Discord
        if message.sender_id.startswith("discord_"):
            return
        
        # Create embed for the message
        embed = disnake.Embed(
            description=message.content,
            color=self._get_color_for_sender(message.sender_name),
            timestamp=message.timestamp
        )
        embed.set_author(name=message.sender_name)
        
        if message.metadata.get("model"):
            embed.set_footer(text=f"Model: {message.metadata['model']}")
        
        # Send to all connected channels
        for channel_id in list(self._connected_channels.keys()):
            try:
                channel = self.get_channel(channel_id)
                if channel:
                    await channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Error sending to Discord channel {channel_id}: {e}")
                # Remove disconnected channel
                del self._connected_channels[channel_id]
    
    def _get_color_for_sender(self, sender_name: str) -> disnake.Color:
        """Get a consistent color for a sender based on their name."""
        colors = [
            disnake.Color.blue(),
            disnake.Color.green(),
            disnake.Color.purple(),
            disnake.Color.orange(),
            disnake.Color.red(),
            disnake.Color.teal(),
            disnake.Color.gold(),
            disnake.Color.magenta(),
        ]
        
        # Use hash of name to pick consistent color
        color_index = hash(sender_name) % len(colors)
        return colors[color_index]
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Discord bot logged in as {self.user}")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        
        # Initialize chatroom
        await self._ensure_chatroom()
    
    async def on_message(self, message: disnake.Message):
        """
        Handle regular messages in connected channels.
        
        Args:
            message: The Discord message
        """
        # Ignore bot's own messages
        if message.author == self.user:
            return
        
        # Ignore messages outside connected channels
        if message.channel.id not in self._connected_channels:
            return
        
        # Ignore commands (they're handled by slash commands)
        if message.content.startswith("/") or message.content.startswith("!"):
            return
        
        # Forward message to chatroom
        await self._ensure_chatroom()
        
        if self._chatroom:
            username = f"{message.author.display_name} (Discord)"
            user_id = f"discord_{message.author.id}"
            
            await self._chatroom.add_human_message(
                content=message.content,
                username=username,
                user_id=user_id
            )
            
            # Trigger agent responses
            asyncio.create_task(self._chatroom.trigger_response_to_human())
            
            # React to acknowledge
            try:
                await message.add_reaction("")
            except:
                pass


def main():
    """Main entry point for the Discord bot."""
    if not DISCORD_BOT_TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not set in environment variables")
        print("Please set DISCORD_BOT_TOKEN in your .env file")
        return
    
    bot = ChatroomBot()
    
    print("Starting Multi-Agent Chatroom Discord Bot...")
    print("Use /joinroom in a Discord channel to connect it to the chatroom")
    print()
    
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except disnake.LoginFailure:
        print("ERROR: Invalid Discord bot token")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
