import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import InputMediaDice

API_ID = 10079905
API_HASH = "e4a5fa251e2e055f26e5c2add8401530"
# Teri nayi fresh session string yahan set hai
SESSION_STRING = "1BVtsOK4Bu5bgSNU5dl9jvi9dwlD7fV4DamP4abaDKjYjlEPbie836YnPxD6EJVOiKu6zClNm_zlJfpSyMKg_ZvS2cu1IpTFoNOH_ZiZbgg9OWbokdoTKwQ3BUcjwgORUcX0KJFJhR1zroNP5-Utu-WwJosSjjV3MUKMsNvHwpgEARVDGmVpGHrsoThnRmo59Uij4ynPr0RMxG8EwwHgn_bvYs7KBgajTLvZvj4t1e7L_pwoG4tm8u4QpHyLIQ5sQYInQXNC4AyjSeY9lkGgBxyjCxWy5U-QiMNK_DwNvy4xEVSBoXiG8ZKWVzXFc6PvcWMv89ONjnNUNy0ozuyjxCbuaUakkSYY="

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# 1. Command ke liye (.dice ya .dice6)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.dice(\s*[1-6])?'))
async def rigged_dice(event):
    match_str = event.pattern_match.group(1)
    desired_number = int(match_str.strip()) if match_str else None
    
    try:
        await event.delete()
    except Exception:
        pass
    
    msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
    
    while True:
        # Telegram server ke animation complete hone ka proper wait
        await asyncio.sleep(2.0)
        
        try:
            current_msg = await client.get_messages(event.chat_id, ids=msg.id)
            
            if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                dice_value = current_msg.media.dice.value
                
                # Agar specific number manga hai aur wo aa gaya, ya phir bina number ke 1 ke alawa kuch aa gaya -> Stop!
                if (desired_number and dice_value == desired_number) or (not desired_number and dice_value != 1):
                    break
                
                # Agar 1 aa gaya ya match nahi hua, toh delete karke naya feko
                await current_msg.delete()
                msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
                
        except Exception as e:
            await asyncio.sleep(0.5)
            continue

# 2. Global Anti-1 Guard: Agar tu bina command ke bhi manually dice fekega aur 1 aaya, toh bot hata dega!
@client.on(events.NewMessage(outgoing=True))
async def manual_dice_guard(event):
    if event.media and hasattr(event.media, 'dice') and event.media.dice.emoticon == '🎲':
        # Agar yeh command message nahi hai (matlab manual roll hai)
        if event.raw_text.startswith('.'):
            return
            
        msg = event.message
        while True:
            await asyncio.sleep(2.0)
            try:
                current_msg = await client.get_messages(event.chat_id, ids=msg.id)
                if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                    dice_value = current_msg.media.dice.value
                    
                    # Agar manual roll mein bhi 1 aa gaya, toh turant badal do!
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
    print("🛡️ Anti-1 Absolute Guard Bot is online & running!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
