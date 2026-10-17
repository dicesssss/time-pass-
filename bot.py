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
    # User ne jo number manga hai (jaise .dice6 se 6)
    desired_number = int(event.pattern_match.group(1))
    
    # Sabse pehle command message (.dice6) ko turant uda do taaki koi trace na rahe
    try:
        await event.delete()
    except Exception:
        pass
    
    # Pehla dice bhej kar process shuru karo
    msg = await event.respond('🎲')
    
    # Ultra-fast loop jo tab tak chalega jab tak man-chaha number na aa jaye
    while True:
        # Telegram server ko dice state update karne ke liye minimal optimal pause
        await asyncio.sleep(0.35)
        
        try:
            # Message ki current live state fetch karo
            current_msg = await client.get_messages(event.chat_id, ids=msg.id)
            
            if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                dice_value = current_msg.media.dice.value
                
                # Agar wahi number aa gaya jo aapko chahiye, toh loop yahin rok do (ruk jao)
                if dice_value == desired_number:
                    break
                
                # Agar galat number hai, toh bina ek bhi second waste kiye naya bhejo aur purana delete karo
                msg = await client.send_message(event.chat_id, '🎲')
                await current_msg.delete()
                
        except Exception as e:
            print(f"Network/Runtime Exception caught: {e}")
            await asyncio.sleep(0.5)
            continue

print("🔥 Legendary Ultra-Fast Rigged Dice Userbot is successfully online & running!")
client.start()
client.run_until_disconnected()
