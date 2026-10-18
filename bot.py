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

# Thread-safe sets and maps to manage concurrency and prevent duplicate processing
processed_events = set()
target_dice_goals = {}  # Tracks custom command goals (e.g., msg_id -> target value)

async def memory_cleanup_daemon():
    """Background task to clear tracking memory and prevent unbounded growth."""
    while True:
        await asyncio.sleep(600)  # Clean every 10 minutes
        if len(processed_events) > 2000:
            processed_events.clear()
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
        print(f"Failed to dispatch command dice: {e}")

# 2. Ultra-Low-Latency Event-Driven MessageEdited Handler
@client.on(events.MessageEdited(outgoing=True))
async def dice_edit_handler(event):
    try:
        # Verify message contains valid dice media
        if event.media and hasattr(event.media, 'dice') and event.media.dice.emoticon == '🎲':
            msg_id = event.id
            chat_id = event.chat_id
            dice_value = event.media.dice.value

            # 0 signifies the server is still processing the dice roll animation
            if dice_value == 0:
                return

            # Construct unique event signature to block duplicate MTProto duplicate pushes
            event_sig = f"{chat_id}-{msg_id}-{dice_value}"
            if event_sig in processed_events:
                return
            processed_events.add(event_sig)

            # Evaluate target criteria (command goal vs default guard rule)
            desired_number = target_dice_goals.get(msg_id)
            should_reroll = False

            if desired_number:
                if dice_value != desired_number:
                    should_reroll = True
            else:
                if dice_value in [1, 2]:
                    should_reroll = True

            if should_reroll:
                print(f"[Guard] Unwanted roll ({dice_value}) intercepted in chat {chat_id}. Deleting...")
                try:
                    await client.delete_messages(chat_id, [msg_id])
                except FloodWaitError as fw:
                    print(f"Rate limit encountered! Pausing for {fw.seconds} seconds.")
                    await asyncio.sleep(fw.seconds)
                    return
                except Exception as e:
                    print(f"Deletion error for message {msg_id}: {e}")
                    return

                # Send fresh replacement dice
                try:
                    new_msg = await client.send_file(chat_id, file=InputMediaDice(emoticon='🎲'))
                    if desired_number:
                        target_dice_goals[new_msg.id] = desired_number
                except Exception as e:
                    print(f"Failed to send replacement dice: {e}")
            else:
                # Safe outcome achieved; purge tracking goal if present
                if msg_id in target_dice_goals:
                    del target_dice_goals[msg_id]

    except Exception as e:
        print(f"Error within dice_edit_handler: {e}")

async def main():
    # Initialize background web server and memory cleanup daemons
    asyncio.create_task(start_web_server())
    asyncio.create_task(memory_cleanup_daemon())

    await client.connect()
    if not await client.is_user_authorized():
        print("Error: Session String is unauthorized, invalid, or expired!")
        return

    print("🔥 Ultra-Low-Latency Event-Driven Dice Guard is online and running!")

    try:
        await client.send_message('me', "🔥 **Dice Guard Bot successfully online (Event-Driven Mode)!**")
    except Exception as e:
        print(f"Could not dispatch startup notification: {e}")

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
