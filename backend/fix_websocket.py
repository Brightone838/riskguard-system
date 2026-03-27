import asyncio 
from app.services.realtime_monitor import manager 
 
async def test(): 
    await manager.broadcast("test", "Test message") 
 
asyncio.run(test()) 
print("WebSocket fix applied") 
