import asyncio
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import InputMediaDice

from config import API_ID, API_HASH, SESSION_STRING
from keep_alive import start_web_server

if not SESSION_STRING:
    print("Error: SESSION_STRING environment variable is missing!")
    exit(1)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Set to prevent duplicate handling of the same message edit event
processed_dice = set()

# 1. Quick command handler for .dice
@client.on(events.NewMessage(outgoing=True, pattern=r'\.dice'))
async def cmd_dice(event):
    try:
        await event.delete()
    except Exception:
        pass
    await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))

# 2. Event-Driven MessageEdited Handler (Zero polling, instant response)
@client.on(events.MessageEdited(outgoing=True))
async def dice_edit_handler(event):
    try:
        # Check if the edited message contains a dice media
        if event.media and hasattr(event.media, 'dice') and event.media.dice.emoticon == '🎲':
            msg_id = event.id
            
            # Prevent handling the same event twice
            if msg_id in processed_dice:
                return
                
            dice_value = event.media.dice.value
            
            # 0 means the dice animation is still rolling on Telegram's server
            if dice_value == 0:
                return
                
            # If a 1 or 2 lands, delete it instantly and re-roll
            if dice_value in [1, 2]:
                processed_dice.add(msg_id)
                print(f"[{msg_id}] Bad dice ({dice_value}) caught via MessageEdited! Re-rolling...")
                
                try:
                    await event.delete()
                except Exception as e:
                    print(f"Failed to delete message: {e}")
                
                try:
                    await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
                except Exception as e:
                    print(f"Failed to send new dice: {e}")
                    
            # Prevent memory bloat by clearing old tracked IDs periodically
            if len(processed_dice) > 1000:
                processed_dice.clear()
                
    except Exception as e:
        print(f"Error in dice_edit_handler: {e}")

async def main():
    # Start the keep-alive background server for 24/7 uptime
    asyncio.create_task(start_web_server())
    
    await client.connect()
    if not await client.is_user_authorized():
        print("Error: Session String is invalid or expired!")
        return
        
    print("🔥 Event-Driven Ultra-Fast Dice Guard is online and running!")
    
    # Startup notification in Saved Messages
    try:
        await client.send_message('me', "🔥 **Event-Driven Dice Guard Bot is successfully online!**")
    except Exception as e:
        print(f"Could not send startup message: {e}")
        
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
