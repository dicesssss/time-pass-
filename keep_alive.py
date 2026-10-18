import os
import asyncio
from aiohttp import web

async def handle(request):
    return web.Response(text="Bot is alive and running 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌍 Keep-Alive web server started on port {port}")
