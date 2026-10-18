import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import InputMediaDice

API_ID = 10079905
API_HASH = "e4a5fa251e2e055f26e5c2add8401530"
# Teri nayi fresh session string yahan daal di hai
SESSION_STRING = "1BVtsOK4Bu8BknyYLNe3RrGussXd8fu40aNF3tI7xcNAkCC_UZuu7dB7vupafNRtNL8LaTaZTMOjv0iMR01SsECSUgjQfvFg-nSwpRQg61NCUKequXbc-bODnunLWYrH-8ysWs6LvHCRs-xteMwfwi2PpUVyOAvBOuGyPHdNW0XsQQ1GkiwxZXMF1blXvcI0rvSRalTgSqjmVjUjNl4NOilQ58B40oVOeSXzdO_M2o1cMiTwhvoL4ehVF2JclNf9GWEVMvVEz1QCqi_JYPmijs9L1qMBwh2hbqeCbrxR0m4WODpocrv3NdG-4uv0gN70eD2IckFhs0wd2dviJUkNmMK99aW4p-3A="

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# 1. Command handler (.dice ya .dice[3-6])
@client.on(events.NewMessage(outgoing=True, pattern=r'\.dice(\s*([1-6]))?'))
async def rigged_dice(event):
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
        await asyncio.sleep(2.2)
        try:
            current_msg = await client.get_messages(event.chat_id, ids=msg.id)
            if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                dice_value = current_msg.media.dice.value
                
                if (desired_number and dice_value == desired_number) or (not desired_number and dice_value not in [1, 2]):
                    break
                
                await current_msg.delete()
                msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
        except Exception:
            await asyncio.sleep(0.5)
            continue

# 2. Manual Guard (Bina command ke bhi agar dice fekoge toh 1 aur 2 hat jayega)
@client.on(events.NewMessage(outgoing=True))
async def manual_dice_guard(event):
    if event.media and hasattr(event.media, 'dice') and event.media.dice.emoticon == '🎲':
        if event.raw_text and event.raw_text.startswith('.'):
            return
            
        msg = event.message
        while True:
            await asyncio.sleep(2.2)
            try:
                current_msg = await client.get_messages(event.chat_id, ids=msg.id)
                if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                    dice_value = current_msg.media.dice.value
                    if dice_value in [1, 2]:
                        await current_msg.delete()
                        msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
                    else:
                        break
            except Exception:
                break

async def main():
    await client.connect()
    if not await client.is_user_authorized():
        print("Error: Session String is invalid!")
        return
    print("🚀 Perfect Anti-1 & Anti-2 Bot is online!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
