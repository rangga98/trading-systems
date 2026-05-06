"""Request logging middleware."""

import time

from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.logging import logger


class RequestLoggingMiddleware:
    """Pure ASGI middleware that logs all requests with timing."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        path = scope.get("path", "/")
        method = scope.get("method", "UNKNOWN")

        logger.info(f"Request started: {method} {path}")

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration = time.time() - start_time
                status_code = message.get("status", 0)
                logger.info(
                    f"Request completed: {method} {path} "
                    f"- Status: {status_code} - Duration: {duration:.3f}s"
                )
            await send(message)

        await self.app(scope, receive, send_wrapper)
