import logging
from aiohttp import web
import hmac
import hashlib
import base64
import os
import asyncio


# 配置结构化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('websocket')

# 模拟存储 API Key 和 Client Secret 的数据库
credentials = {
    "SGVsbG8sIEkgYW0gdGhlIEFQSSBrZXkh": "TXlTdXBlclNlY3JldEtleVRlbGxOby0xITJAMyM0JDU="
}

async def websocket_handler(request):
    # 验证 API Key
    api_key = request.headers.get("X-API-KEY")
    if api_key not in credentials:
        return web.Response(text="Invalid API Key", status=401)

    client_secret = credentials[api_key]

    # 验证签名
    signature_header = request.headers.get("Signature")
    if not signature_header:
        return web.Response(text="Missing Signature", status=401)

    # 解析签名头
    signature_parts = {}
    for part in signature_header.split(","):
        key, value = part.strip().split("=", 1)
        signature_parts[key] = value.strip('"')

    required_headers = signature_parts.get("headers", "").split()
    algorithm = signature_parts.get("algorithm", "")
    signature = signature_parts.get("signature", "")

    # 构造签名字符串
    elements = []
    for h in required_headers:
        if h == "(request-target)":
            method = request.method.lower()
            path = request.path
            elements.append(f"(request-target): {method} {path}")
        elif h == "authority":
            elements.append(f"authority: {request.host}")
        else:
            header_value = request.headers.get(h.replace("-", "_").upper(), "")
            elements.append(f"{h}: {header_value}")

    signature_string = "\n".join(elements)

    # 计算 HMAC
    if algorithm != "hmac-sha256":
        return web.Response(text="Unsupported Algorithm", status=401)

    digest = hmac.new(
        client_secret.encode(), 
        signature_string.encode(), 
        hashlib.sha256
    ).digest()
    computed_signature = base64.b64encode(digest).decode()

    if computed_signature != signature:
        logger.info("Invalid signature for API Key: %s", api_key)
        return web.Response(text="Invalid Signature", status=401)

    # 验证通过，建立 WebSocket 连接
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            logger.info("Received message: %s", msg.data)
            await ws.send_str(f"Echo: {msg.data}")

    return ws

app = web.Application()
app.router.add_get("/ws", websocket_handler)

async def heartbeat():
    while True:
        logger.info("WebSocket 服务心跳正常")
        await asyncio.sleep(30)  # 每30秒打印一次心跳

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    logger.info(f"WebSocket 服务已启动，监听 0.0.0.0:{port}")

    async def main():
        asyncio.create_task(heartbeat())
        await web._run_app(app, host='0.0.0.0', port=port)

    asyncio.run(main())