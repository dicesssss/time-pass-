import asyncio
import os
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from telethon.sessions import StringSession
from telethon.tl.types import InputMediaDice

from config import API_ID, API_HASH, SESSION_STRING
from keep_alive import start_web_server

if not SESSION_STRING:
    print("Error: SESSION_STRING environment variable is missing!")
    exit(1)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Thread-safe tracking and memory management
processed_messages = set()
target_dice_goals = {}  # Tracks specific desired numbers for command calls (e.g., msg_id -> target_value)

async def cleanup_memory():
    """Periodically trims the tracking set to prevent unbounded memory growth."""
    while True:
        await asyncio.sleep(600)  # Clean every 10 minutes
        if len(processed_messages) > 2000:
            # Keep the most recent items roughly by clearing half
            processed_messages.clear()
            target_dice_goals.clear()

# 1. Command Handler (.dice or .dice [3-6])
@client.on(events.NewMessage(outgoing=True, pattern=r'\.dice(\s*([1-6]))?'))
async def cmd_dice(event):
    match_str = event.pattern_match.group(1)
    desired_number = int(match_str.strip()) if match_str else None

    try:
        await event.delete()
    except Exception:
        pass

    try:
        new_msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
        if desired_number:
            target_dice_goals[new_msg.id] = desired_number
    except Exception as e:
        print(f"Failed to send initial command dice: {e}")

# 2. Event-Driven MessageEdited Handler (Ultra-low latency detection)
@client.on(events.MessageEdited(outgoing=True))
async def dice_edit_handler(event):
    try:
        # Verify that the edited message contains a dice media object
        if event.media and hasattr(event.media, 'dice') and event.media.dice.emoticon == '🎲':
            msg_id = event.id
            chat_id = event.chat_id
            dice_value = event.media.dice.value

            # 0 indicates the animation is still rolling on the server side
            if dice_value == 0:
                return

            # Prevent duplicate processing of the exact same update event
            event_signature = f"{chat_id}-{msg_id}-{dice_value}"
            if event_signature in processed_messages:
                return
            processed_messages.add(event_signature)

            # Determine target condition (custom command goal or default guard rule: delete 1 and 2)
            desired_number = target_dice_goals.get(msg_id)
            
            should_reroll = False
            if desired_number:
                if dice_value != desired_number:
                    should_reroll = True
            else:
                if dice_value in [1, 2]:
                    should_reroll = True

            if should_reroll:
                print(f"[Guard] Unwanted dice value ({dice_value}) detected in chat {chat_id}. Deleting...")
                try:
                    await client.delete_messages(chat_id, [msg_id])
                except FloodWaitError as fw:
                    print(f"Rate limited! Sleeping for {fw.seconds} seconds.")
                    await asyncio.sleep(fw.seconds)
                except Exception as e:
                    print(f"Deletion failed for message {msg_id}: {e}")
                    return

                # Send replacement dice
                try:
                    new_msg = await client.send_file(chat_id, file=InputMediaDice(emoticon='🎲'))
                    if desired_number:
                        target_dice_goals[new_msg.id] = desired_number
                except Exception as e:
                    print(f"Failed to send replacement dice: {e}")
            else:
                # Target value achieved or safe result (3-6), clean up tracking goals if any
                if msg_id in target_dice_goals:
                    del target_dice_goals[msg_id]

    except Exception as e:
        print(f"Error inside dice_edit_handler: {e}")

async def main():
    # Start the keep-alive background server for 24/7 hosting uptime
    asyncio.create_task(start_web_server())
    asyncio.create_task(cleanup_memory())

    await client.connect()
    if not await client.is_user_authorized():
        print("Error: Session String is invalid, expired, or unauthorized!")
        return

    print("🔥 Ultra-Low-Latency Event-Driven Dice Guard is online and running!")

    try:
        await client.send_message('me', "🔥 **Dice Guard Bot successfully started and active (Event-Driven Mode)!**")
    except Exception as e:
        print(f"Could not send startup notification: {e}")

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
