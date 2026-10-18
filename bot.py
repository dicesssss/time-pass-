import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import InputMediaDice

API_ID = 10079905
API_HASH = "e4a5fa251e2e055f26e5c2add8401530"
SESSION_STRING = "1BVtsOK4Bu5L_eDXm__Exrhcovc5hd0pYwgfDp6Y0OpKuNp4rirKOvZUaOYxXSOruvJv715n3GwupxcQpMjx6YkV84WJFt0U1LTLs8nQUDx22fDHjKmxE47l5e0RniVmlRhUHXmqLDd1BIzSLhLjOF4DpWZPHomSwVGR7OFo1-KgFNa7TpXOrUCBGi3PvOLneNuvdy3E5ZwtMRpHt8WLCWsi59uCjDLPpYr9U8L-wvuz1gWk1w3okOq1Jqc7CG3TV7WJWgCZYoMkUQgMaiC_ACj09A654IZTpbta3WdRwal9FAJ-1GMJnK4a_2MRWP8DywBa-vK-v_8lT2805by6iN4Av4l5uJZ4="

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.dice\s*([1-6])'))
async def rigged_dice(event):
    desired_number = int(event.pattern_match.group(1))
    
    try:
        await event.delete()
    except Exception:
        pass
    
    # Yahan hum proper Interactive Animated Dice bhej rahe hain (Plain text '🎲' ki jagah)
    msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
    
    while True:
        # Dice animation poora hone ke liye 2.2 seconds ka wait zaroori hai
        await asyncio.sleep(2.2)
        
        try:
            current_msg = await client.get_messages(event.chat_id, ids=msg.id)
            
            if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                dice_value = current_msg.media.dice.value
                
                # Agar wahi number aa gaya jo aapne manga tha, toh yahin rok do
                if dice_value == desired_number:
                    break
                
                # Agar nahi aaya, toh purana delete karke naya animated dice feko
                await current_msg.delete()
                msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
                
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(1)
            continue

async def main():
    await client.connect()
    if not await client.is_user_authorized():
        print("Error: Session String is invalid!")
        return
    print("🎲 Animated Rigged Dice Bot is online and running!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
