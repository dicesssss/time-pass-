import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import InputMediaDice

API_ID = 10079905
API_HASH = "e4a5fa251e2e055f26e5c2add8401530"
SESSION_STRING = "1BVtsOK4Bu5nS6iyCYjxlc77y2M932ktHhen3yvKESEJOQ-LvspjGA4VNkoMpywJliwoNWdZzDJPF_nYEvjvSZLZYB12ded5zo02j_l0683nx9S4NxMLUPkxVpbc3ZTBKZjmd20fngY1QAWZHypCZPHHgpE1TR9TISLLn5oKD-HSuCwotrdhLKx_65If7Hnc_mc3wP73r5B4K2L9R-KEOwWJfdoSZiCm6B1X0zyhYnzKQiyAAlEFilUpPXQfve3bR7GaKrcnrzNo-uu6omQhxWUfxQR3a9daxZbGrOqi4ClZtoV9PBo629L7mRb9B1WnbepNXkLBXb84WgLrH0qdBjVSuGfMAFEQ="

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
