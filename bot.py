import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import InputMediaDice

API_ID = 10079905
API_HASH = "e4a5fa251e2e055f26e5c2add8401530"
SESSION_STRING = "1BVtsOK4BuzlXZbH99COnFMh1eppsdRy8dQekURrL8NJl1NdQJrHNgrEOSqCGrOs1ZU7FGVrXUCoPz3iTADEul5sGo_OU2ZXvoWwvXtngi2How4EkXQbEo4156FmFHVl_ZP2HtcyAsLjyofu-hROudqcEyezd9XmcoQJRgi1l_zJaxGGMq2-LO2t_kdLHiywnHi-rWIGO-QUZ03gosNp16bzwIFGpLj9pgMHmYNZJO-UVIy7zJbBcMGRYORDXG4lY3pF3b_QCX1m_2ok0yu8sy53Kteuq1vdEl9smICTQcG9CvJJP6OwE3tVtHSRD9s31nV-EpYkyN_W_FmwL-cY6UjtMIPV_aP8="

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.dice\s*([1-6])'))
async def rigged_dice(event):
    desired_number = int(event.pattern_match.group(1))
    
    try:
        await event.delete()
    except Exception:
        pass
    
    # Pehla dice feko
    msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
    
    while True:
        # Ultra-fast check interval (almost instant)
        await asyncio.sleep(0.08)
        
        try:
            # Chat state refresh karne ke liye dialogue/messages fetch karo
            current_msg = await client.get_messages(event.chat_id, ids=msg.id)
            
            if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                dice_value = current_msg.media.dice.value
                
                # Agar target number mil gaya, toh loop break karo (final result wahi ruk jayega)
                if dice_value == desired_number:
                    break
                
                # Agar nahi mila toh bina animation ke turant delete karke naya feko
                await current_msg.delete()
                msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
                
        except Exception as e:
            await asyncio.sleep(0.05)
            continue

async def main():
    await client.connect()
    if not await client.is_user_authorized():
        print("Error: Session String is invalid!")
        return
    print("⚡ Instant Stealth Dice Bot is online & running!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
