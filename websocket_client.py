import asyncio
import hmac
import hashlib
import base64
from aiohttp import ClientSession, WSMsgType

API_KEY = "SGVsbG8sIEkgYW0gdGhlIEFQSSBrZXkh"
CLIENT_SECRET = "TXlTdXBlclNlY3JldEtleVRlbGxOby0xITJAMyM0JDU="
WS_URL = "wss://webapp.74.179.236.185.sslip.io/ws"

def generate_signature():
    signature_string = (
        "(request-target): get /ws\n"
        "authority: webapp.74.179.236.185.sslip.io"
    )
    digest = hmac.new(
        CLIENT_SECRET.encode(),
        signature_string.encode(),
        hashlib.sha256
    ).digest()
    return base64.b64encode(digest).decode()

async def websocket_client():
    signature = generate_signature()
    
    headers = {
        "X-API-KEY": API_KEY,
        "Signature": f'headers="(request-target) authority", '
                    f'algorithm="hmac-sha256", '
                    f'signature="{signature}"',
        "Host": "webapp.74.179.236.185.sslip.io"
    }

    async with ClientSession() as session:
        try:
            async with session.ws_connect(WS_URL, headers=headers) as ws:
                print("连接成功")
                await ws.send_str("Hello Server!1214")
                async for msg in ws:
                    if msg.type == WSMsgType.TEXT:
                        print(f"收到响应: {msg.data}")
                        break
        except Exception as e:
            print(f"失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(websocket_client())