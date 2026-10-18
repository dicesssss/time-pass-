import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import InputMediaDice

API_ID = 10079905
API_HASH = "e4a5fa251e2e055f26e5c2add8401530"
SESSION_STRING = "1BVtsOK4Bu5x1x_UUYagKfCcVkZ01mSJvR9RAHZHpl8P0581ggzsGj_SZfE2_nBztplT6s8qfD1C8XPBPry97DXcVUmWvcb1vVQON63j6HB5g8v5H4FR2Nt8-XZv3Q-dFGIvQgT9UDH9tACr4J9zi8-n4kTeVj85ys_dnP37qdFH61fmgMNwpezNZGwudbppw7x8Uh56J4_s9WG5_DJAYuEwhtCgBVKFSqEL2d7a3l5BvrZkQIZVja8eVQtr3XxPv6gGBmKoYXe6hVb856pRTKwrDL8gG2AbMisu6CJBaezb0HlRCKOEgnDzUiPwJ1qRDYYQJrpgalIvRczeOio038t1CA3aXXH0="

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# 1. Command handler: .dice ya .dice6 ke liye
@client.on(events.NewMessage(outgoing=True, pattern=r'\.dice(\s*[1-6])?'))
async def rigged_dice(event):
    match_str = event.pattern_match.group(1)
    desired_number = int(match_str.strip()) if match_str else None
    avoid_one = True if not desired_number else False
    
    try:
        await event.delete()
    except Exception:
        pass
    
    msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
    
    while True:
        await asyncio.sleep(1.2)
        try:
            current_msg = await client.get_messages(event.chat_id, ids=msg.id)
            if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                dice_value = current_msg.media.dice.value
                if (desired_number and dice_value == desired_number) or (avoid_one and dice_value != 1):
                    break
                await current_msg.delete()
                msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
        except Exception:
            await asyncio.sleep(0.5)
            continue

# 2. Background guard: Agar tu manually bhi koi dice fekega aur 1 aa gaya, toh bot use turant hata dega!
@client.on(events.NewMessage(outgoing=True))
async def manual_dice_guard(event):
    # Agar message me dice media hai (aur koi command nahi hai)
    if event.media and hasattr(event.media, 'dice') and event.media.dice.emoticon == '🎲':
        msg = event.message
        while True:
            await asyncio.sleep(1.2)
            try:
                current_msg = await client.get_messages(event.chat_id, ids=msg.id)
                if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                    dice_value = current_msg.media.dice.value
                    # Agar manual fekne par bhi 1 aa gaya, toh delete karke naya feko jab tak 1 na hate
                    if dice_value == 1:
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
    print("🛡️ Anti-1 Background Guard & Rigged Dice Bot is online!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
