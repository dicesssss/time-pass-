import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Aapki credentials aur Session String yahan perfectly set hain
API_ID = 10079905
API_HASH = "e4a5fa251e2e055f26e5c2add8401530"
SESSION_STRING = "1BVtsOK4Bu4o006kWDA-KQT5fjsmJccXx90memRWsLMbFiKOh7SMXuZpAKTYwwozJBVfkxhfNCdudbTEw6-pBhP0sw-7VWDUR0KLgHKDP6Y0qZh-OKD5I3_zHsZ3uamEp6xmV8a87kTyg_7cKsVq6EzVP31fAjjWTqjNIK5EG5hrDsuGYqlgL2u3_jZ_n5A98f2El1guZLk5ieEUCVM7bCnSzaItqFMjnhH0ol-mmlTNNZmBdNqbect6NHwDjgd-DHkvOcsCo-E2aUcAm7PYdKDmX0EanXkGbWN5ljsWffTvcNWoAi2MEwKvcUkoKwjauW5VnIogacahqm-4FafF5jbX5fQu_19A="

# Client initialize ho raha hai
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.dice([1-6])'))
async def rigged_dice(event):
    desired_number = int(event.pattern_match.group(1))
    
    try:
        await event.delete()
    except Exception:
        pass
    
    msg = await event.respond('🎲')
    
    while True:
        await asyncio.sleep(0.35)
        
        try:
            current_msg = await client.get_messages(event.chat_id, ids=msg.id)
            
            if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                dice_value = current_msg.media.dice.value
                
                if dice_value == desired_number:
                    break
                
                msg = await client.send_message(event.chat_id, '🎲')
                await current_msg.delete()
                
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(0.5)
            continue

async def main():
    # StringSession ke sath bina interactive input ke connect karne ka sahi tarika
    await client.connect()
    if not await client.is_user_authorized():
        print("Error: Session String is invalid or expired!")
        return
    print("🔥 Legendary Ultra-Fast Rigged Dice Userbot is successfully online & running!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
