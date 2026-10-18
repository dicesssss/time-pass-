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

# 1. Command Handler (.dice ya .dice [number])
@client.on(events.NewMessage(outgoing=True, pattern=r'\.dice(\s*([1-6]))?'))
async def rigged_dice_command(event):
    match_str = event.pattern_match.group(1)
    desired_number = int(match_str.strip()) if match_str else None
    
    if desired_number in [1, 2]:
        desired_number = None

    try:
        await event.delete()
    except Exception:
        pass
    
    msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
    chat_id = event.chat_id
    msg_id = msg.id
    
    while True:
        await asyncio.sleep(2.0)
        try:
            current_msg = await client.get_messages(chat_id, ids=msg_id)
            if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                dice_value = current_msg.media.dice.value
                print(f"[Command] Dice Value: {dice_value}")
                
                if dice_value == 0:
                    continue
                
                if (desired_number and dice_value == desired_number) or (not desired_number and dice_value in [3, 4, 5, 6]):
                    break
                
                if dice_value in [1, 2]:
                    print(f"[Command] Bad dice ({dice_value})! Deleting via ID...")
                    await client.delete_messages(chat_id, [msg_id])
                    new_msg = await client.send_file(chat_id, file=InputMediaDice(emoticon='🎲'))
                    msg_id = new_msg.id
        except Exception as e:
            print(f"Error in command loop: {e}")
            await asyncio.sleep(1.0)
            continue

# 2. Manual Dice Guard (Bina command ke fekne par)
@client.on(events.NewMessage(outgoing=True))
async def manual_dice_guard(event):
    if event.media and hasattr(event.media, 'dice') and event.media.dice.emoticon == '🎲':
        if event.raw_text and event.raw_text.startswith('.'):
            return
            
        chat_id = event.chat_id
        msg_id = event.message.id
        
        while True:
            await asyncio.sleep(2.0)
            try:
                current_msg = await client.get_messages(chat_id, ids=msg_id)
                if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                    dice_value = current_msg.media.dice.value
                    print(f"[Manual] Dice Value: {dice_value}")
                    
                    if dice_value == 0:
                        continue
                        
                    if dice_value in [1, 2]:
                        print(f"[Manual] Bad dice ({dice_value})! Deleting via ID...")
                        await client.delete_messages(chat_id, [msg_id])
                        new_msg = await client.send_file(chat_id, file=InputMediaDice(emoticon='🎲'))
                        msg_id = new_msg.id
                    else:
                        break
            except Exception as e:
                print(f"Error in manual loop: {e}")
                break

async def main():
    asyncio.create_task(start_web_server())
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Error: Session String is invalid or expired!")
        return
        
    print("🔥 Ultimate Bulletproof Dice Guard is online and running!")
    
    try:
        await client.send_message('me', "🔥 **Dice Guard Bot successfully start ho gaya hai aur active hai!**")
    except Exception as e:
        print(f"Could not send startup message: {e}")
        
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
