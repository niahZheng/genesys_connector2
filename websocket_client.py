import asyncio
import hmac
import hashlib
import base64
from aiohttp import ClientSession, WSMsgType

API_KEY = "SGVsbG8sIEkgYW0gdGhlIEFQSSBrZXkh"
CLIENT_SECRET = "TXlTdXBlclNlY3JldEtleVRlbGxOby0xITJAMyM0JDU="
# WS_URL = "wss://watson-stt-stream-connector-liping-1-b5fwckcngpe3enew.canadaeast-01.azurewebsites.net:443"
WS_URL="wss://genesys-connector-2-buhkgbfvfbeughe5.canadaeast-01.azurewebsites.net"

def generate_signature():
    signature_string = (
        "(request-target): get /ws\n"
    )
    digest = hmac.new(
        CLIENT_SECRET.encode(),
        signature_string.encode(),
        hashlib.sha256
    ).digest()
    return base64.b64encode(digest).decode()

async def websocket_client():
    signature = generate_signature()
    print(f"Generated Signature: {signature}")
    headers = {
        "X-API-KEY": API_KEY,
    }

    async with ClientSession() as session:
        try:
            async with session.ws_connect(WS_URL, headers=headers) as ws:
                print("successfully connected to WebSocket server")
                # 启动心跳协程
                async def heartbeat():
                    while True:
                        await ws.send_str("ping")
                        print("Sent heartbeat ping")
                        await asyncio.sleep(30)  # 每30秒发送一次心跳

                heartbeat_task = asyncio.create_task(heartbeat())

                await ws.send_str("Hello Server!1214")
                async for msg in ws:
                    if msg.type == WSMsgType.TEXT:
                        print(f"Got the result: {msg.data}")
                    elif msg.type == WSMsgType.CLOSED:
                        print("WebSocket closed by server")
                        break
                    elif msg.type == WSMsgType.ERROR:
                        print(f"WebSocket error: {ws.exception()}")
                        break
        except Exception as e:
            print(f"失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(websocket_client())