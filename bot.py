import asyncio
import os
import time
import random
from telethon import TelegramClient, functions
from telethon.errors import FloodWaitError
from flask import Flask
from threading import Thread

# --- Railway Keep-Alive Flask Server ---
app = Flask('')

@app.route('/')
def home():
    return "Single Account Userbot Sniper is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- Configuration ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
# Yahan hum ek hi session string ka use karenge
SESSION_STRING = os.environ.get("SESSION_STRING", "")

TARGET_USERNAME = "vipiya"

async def main():
    keep_alive()
    print("Starting Single Account Userbot Sniper...")
    
    # Client initialize karna single session string ke sath
    client = TelegramClient(SESSION_STRING, API_ID, API_HASH)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("❌ Session string unauthorized ya invalid hai!")
        return
        
    me = await client.get_me()
    print(f"✅ Logged in as: {me.first_name} (@{me.username or 'NoUsername'})")
    
    # Deploy hote hi Saved Messages mein notification bhejna
    try:
        await client.send_message("me", f"🚀 **Single Account Userbot Successfully Deploy Ho Gaya Hai!**\nTarget: `@{TARGET_USERNAME}`\nChecking chalu kar di gayi hai.")
        print("✅ Deploy notification sent to Saved Messages!")
    except Exception as e:
        print(f"⚠️ Could not send deploy notification: {e}")
        
    print(f"🚀 Sniper loop started for @{TARGET_USERNAME}...")
    total_checks = 0
    flood_till = 0
    
    try:
        while True:
            current_time = time.time()
            
            # FloodWait check
            if current_time < flood_till:
                remaining = int(flood_till - current_time)
                print(f"⏳ FloodWait active: sleeping for {remaining}s...")
                await asyncio.sleep(remaining)
                continue
                
            try:
                total_checks += 1
                print(f"[{total_checks}] Checking @{TARGET_USERNAME}...")
                
                # Check availability
                result = await client(functions.account.CheckUsernameRequest(
                    username=TARGET_USERNAME
                ))
                
                if result:
                    print(f"🔥 TARGET APPEARS FREE: @{TARGET_USERNAME}! Claiming on profile...")
                    
                    # Claiming directly to profile
                    try:
                        await client(functions.account.UpdateUsernameRequest(
                            username=TARGET_USERNAME
                        ))
                        
                        success_msg = f"🎉 **Username Successfully Claimed on Profile!**\n\nTarget: `@{TARGET_USERNAME}`"
                        print(success_msg)
                        await client.send_message("me", success_msg)
                        break
                        
                    except Exception as claim_err:
                        print(f"⚠️ Claim failed: {claim_err}")
                else:
                    print(f"🔴 @{TARGET_USERNAME} is still taken.")
                    
            except FloodWaitError as e:
                wait_sec = e.seconds
                flood_till = time.time() + wait_sec
                print(f"⚠️ Hit FloodWait! Pausing for {wait_sec} seconds.")
                await client.send_message("me", f"⚠️ **FloodWait Alert:** {wait_sec} seconds ka wait aa gaya hai.")
            except Exception as e:
                print(f"⚠️ Check error: {e}")
                
            # ~50 seconds base delay with random jitter (+/- 5 seconds)
            sleep_time = random.uniform(45.0, 55.0)
            await asyncio.sleep(sleep_time)
            
    except Exception as err:
        print(f"❌ Userbot crashed: {err}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
