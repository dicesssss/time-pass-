import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import InputMediaDice

API_ID = 10079905
API_HASH = "e4a5fa251e2e055f26e5c2add8401530"
SESSION_STRING = "1BVtsOK4Bu4FuipP7TCAVqfx0fMmdjaw8y-LdYsbDG45g65nzh_w6OC4TLpmEQvwAjwEbcqg9LmMovFZAv6nO7gXoH7sfh4oBwDgtjA0MYHLzBFLT3SloenBQMZrA29BNmjNIwFwIIzlWppihChP_Ysc6xitBKfSeLksWJoCHcw2YttJCtIiSbMffG31GZtHeG7qHilHxKhIp8DtnJwrE45KXCHJcDm2q-ub65P6JYCAePw_huzethe02OJdahpZ-XF2aXq-m-D9-zSUAGo7dpou_URobjOYTzpbVbzayzzAjjYg4eO4xEw8lyTg242ForFdCoijLxZ5pFt3YtGwzxGZVr9kfPdY="

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

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
    
    # Pehla dice feko
    msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
    target_id = msg.id
    
    while True:
        # Turant check karne ke liye chhota sleep taaki fast detect ho
        await asyncio.sleep(1.0)
        
        try:
            # Chat ke last messages se exact target message ko uthao
            messages = await client.get_messages(event.chat_id, limit=5)
            current_msg = None
            for m in messages:
                if m.id == target_id:
                    current_msg = m
                    break
            
            if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                dice_value = current_msg.media.dice.value
                
                # Agar abhi tak animation chal rahi hai aur value 0 hai, toh skip karo
                if dice_value == 0:
                    continue
                
                # Agar 1 ya 2 aa gaya, toh bina ruke turant delete karke naya feko!
                if dice_value in [1, 2]:
                    await current_msg.delete()
                    new_msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
                    target_id = new_msg.id
                    continue
                
                # Agar user ne specific number manga hai aur wo match ho gaya -> Stop
                if desired_number and dice_value == desired_number:
                    break
                
                # Agar koi specific number nahi manga aur 3, 4, 5, 6 mein se kuch aa gaya -> Stop
                if not desired_number and dice_value in [3, 4, 5, 6]:
                    break
                    
        except Exception:
            await asyncio.sleep(0.5)
            continue

# Manual Dice ke liye bhi instant fast guard
@client.on(events.NewMessage(outgoing=True))
async def manual_dice_guard(event):
    if event.media and hasattr(event.media, 'dice') and event.media.dice.emoticon == '🎲':
        if event.raw_text and event.raw_text.startswith('.'):
            return
            
        msg = event.message
        target_id = msg.id
        
        while True:
            await asyncio.sleep(1.0)
            try:
                messages = await client.get_messages(event.chat_id, limit=5)
                current_msg = None
                for m in messages:
                    if m.id == target_id:
                        current_msg = m
                        break
                        
                if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                    dice_value = current_msg.media.dice.value
                    
                    if dice_value == 0:
                        continue
                        
                    # Agar manual roll mein bhi 1 ya 2 aaya, turant uda do
                    if dice_value in [1, 2]:
                        await current_msg.delete()
                        new_msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
                        target_id = new_msg.id
                    else:
                        break
            except Exception:
                break

async def main():
    await client.connect()
    if not await client.is_user_authorized():
        print("Error: Session String is invalid!")
        return
    print("⚡ Ultra-Fast Anti-1 & Anti-2 Guard is online!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
