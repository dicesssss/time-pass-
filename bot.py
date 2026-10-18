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
    
    while True:
        await asyncio.sleep(2.0)
        try:
            # Message ko directly reload karo server se latest value lene ke liye
            await msg.reload()
            if msg.media and hasattr(msg.media, 'dice'):
                dice_value = msg.media.dice.value
                print(f"Dice Value Checked: {dice_value}")
                
                if dice_value == 0:
                    continue
                
                if (desired_number and dice_value == desired_number) or (not desired_number and dice_value in [3, 4, 5, 6]):
                    break
                
                if dice_value in [1, 2]:
                    print(f"Bad dice ({dice_value}) detected! Deleting and re-rolling...")
                    await msg.delete()
                    msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
        except Exception as e:
            print(f"Error in command dice loop: {e}")
            await asyncio.sleep(0.5)
            continue

# 2. Manual Dice Guard (Bina command ke fekne par bhi)
@client.on(events.NewMessage(outgoing=True))
async def manual_dice_guard(event):
    if event.media and hasattr(event.media, 'dice') and event.media.dice.emoticon == '🎲':
        if event.raw_text and event.raw_text.startswith('.'):
            return
            
        msg = event.message
        while True:
            await asyncio.sleep(2.0)
            try:
                # Message ko directly reload karo server se latest value lene ke liye
                await msg.reload()
                if msg.media and hasattr(msg.media, 'dice'):
                    dice_value = msg.media.dice.value
                    print(f"Manual Dice Value Checked: {dice_value}")
                    
                    if dice_value == 0:
                        continue
                        
                    if dice_value in [1, 2]:
                        print(f"Bad dice ({dice_value}) detected! Deleting and re-rolling...")
                        await msg.delete()
                        msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
                    else:
                        break
            except Exception as e:
                print(f"Error in manual dice loop: {e}")
                break

async def main():
    asyncio.create_task(start_web_server())
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Error: Session String is invalid or expired!")
        return
        
    print("🔥 Fixed Dice Guard with .reload() is online and running!")
    
    try:
        await client.send_message('me', "🔥 **Dice Guard Bot successfully start ho gaya hai aur active hai!**")
    except Exception as e:
        print(f"Could not send startup message: {e}")
        
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
