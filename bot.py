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

@client.on(events.NewMessage(outgoing=True))
async def ultra_fast_dice_guard(event):
    if event.media and hasattr(event.media, 'dice') and event.media.dice.emoticon == '🎲':
        msg = event.message
        
        # Hyper-fast check loop (0.2s interval) taaki 1 ya 2 turant pakda jaye
        for _ in range(15):
            await asyncio.sleep(0.2)
            try:
                current_msg = await client.get_messages(event.chat_id, ids=msg.id)
                if current_msg and current_msg.media and hasattr(current_msg.media, 'dice'):
                    dice_value = current_msg.media.dice.value
                    
                    # Agar abhi animation load ho rahi hai (0), toh agla check karo
                    if dice_value == 0:
                        continue
                    
                    # Agar 1 ya 2 aaya, toh bina ek second gavaye turant delete karke naya feko!
                    if dice_value in [1, 2]:
                        await current_msg.delete()
                        new_msg = await client.send_file(event.chat_id, file=InputMediaDice(emoticon='🎲'))
                        msg = new_msg  # naye message ko track karne ke liye update karo
                        continue
                    else:
                        # Agar 3, 4, 5, 6 aaya toh yeh safe hai, loop tod do
                        break
            except Exception:
                continue

async def main():
    # Keep-Alive web server background mein chalao taaki bot sowe na
    asyncio.create_task(start_web_server())
    
    await client.connect()
    if not await client.is_user_authorized():
        print("Error: Session String is invalid or expired!")
        return
    print("🔥 Ultimate 24/7 Ultra-Fast Dice Guard Bot is online & running!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
