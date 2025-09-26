from __future__ import annotations

import os
import time
from typing import Optional

try:
    from aiohttp import web  # type: ignore
except Exception:  # pragma: no cover
    web = None  # type: ignore

try:
    import aiohttp_cors  # type: ignore
except Exception:  # pragma: no cover
    aiohttp_cors = None  # type: ignore

# Import handlers and constants from the monolith. This keeps behavior identical
# while allowing a modular import surface.
from e8_mind_server_M24 import (  # type: ignore
    BASE_DIR,
    shutdown_sse,
    shutdown_market_feed,
    shutdown_ws,
    handle_memory_search,
    handle_get_state,
    handle_trigger_dream,
    handle_get_qeng_telemetry,
    handle_get_qeng_ablation,
    handle_get_qeng_probabilities,
    handle_get_metrics_summary,
    handle_get_metrics_live,
    handle_post_quantizer,
    handle_post_snapshot,
    handle_get_telemetry,
    handle_get_blueprint,
    handle_stream_telemetry,
    handle_ws_telemetry,
    handle_get_graph,
    handle_get_graph_summary,
    handle_get_node,
    handle_get_bh_panel,
    handle_get_sdi_branch,
    handle_get_sdi_commits,
    handle_get_sdi_capsules,
    handle_get_metrics_recent,
    handle_add_concept,
    handle_add_concept_legacy,
    handle_index,
)


def create_app(mind, console: Optional[object] = None):
    """Create and configure the aiohttp web.Application.

    Mirrors the monolith's inline setup to preserve behavior while providing
    a stable import boundary for future extraction.
    """
    if web is None:
        if console is not None:
            try:
                console.log("[bold yellow]aiohttp not installed. Skipping server startup; core mind initialized headlessly.[/bold yellow]")
            except Exception:
                pass
        return None

    app = web.Application()

    # Lightweight CORS middleware (only active if aiohttp_cors is not available)
    @web.middleware
    async def _simple_cors_middleware(request, handler):
        resp = None
        if aiohttp_cors is None:
            if request.method == "OPTIONS":
                resp = web.Response(status=204)
                resp.headers["Access-Control-Allow-Origin"] = "*"
                resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "*"
                return resp
        resp = await handler(request)
        if aiohttp_cors is None:
            try:
                resp.headers.setdefault("Access-Control-Allow-Origin", "*")
                resp.headers.setdefault("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
                resp.headers.setdefault("Access-Control-Allow-Headers", "*")
            except Exception:
                pass
        return resp

    connection_tracker: dict[str, float] = {}

    @web.middleware
    async def _connection_rate_limiter(request, handler):
        if "/ws" in request.path or "/telemetry" in request.path:
            client_ip = request.remote or "unknown"
            now = time.time()
            # Cleanup old entries (older than 30s)
            to_remove = [ip for ip, t in list(connection_tracker.items()) if now - t > 30]
            for ip in to_remove:
                connection_tracker.pop(ip, None)
            # Simple rate limit: 1 connection/sec/IP
            last = connection_tracker.get(client_ip)
            if last is not None and (now - last) < 1.0:
                if console is not None:
                    try:
                        console.log(f"[RATE LIMIT] Blocking rapid connection from {client_ip}")
                    except Exception:
                        pass
                return web.Response(text="Rate limited", status=429)
            connection_tracker[client_ip] = now
        return await handler(request)

    app.middlewares.append(_simple_cors_middleware)
    app.middlewares.append(_connection_rate_limiter)

    app["mind"] = mind
    app["sse_clients"] = set()
    mind.sse_clients = app["sse_clients"]
    app["ws_clients"] = set()
    mind.ws_clients = app["ws_clients"]

    app.on_shutdown.append(shutdown_sse)
    app.on_shutdown.append(shutdown_market_feed)
    app.on_shutdown.append(shutdown_ws)

    # Setup CORS when available, otherwise provide a no-op shim
    if aiohttp_cors is not None:
        cors = aiohttp_cors.setup(
            app,
            defaults={"*": aiohttp_cors.ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*")},
        )
    else:
        class _NoCors:
            def add(self, *a, **k):
                return None

        cors = _NoCors()

    # Routes (mirroring monolith)
    app.router.add_get("/api/memory/search", handle_memory_search)
    app.router.add_get("/api/state", handle_get_state)
    app.router.add_post("/api/action/dream", handle_trigger_dream)
    app.router.add_get("/api/qeng/telemetry", handle_get_qeng_telemetry)
    app.router.add_get("/api/qeng/ablation", handle_get_qeng_ablation)
    app.router.add_get("/api/qeng/probabilities", handle_get_qeng_probabilities)
    app.router.add_get("/metrics/summary", handle_get_metrics_summary)
    app.router.add_get("/metrics/live", handle_get_metrics_live)
    app.router.add_post("/quantizer", handle_post_quantizer)
    app.router.add_post("/snapshot", handle_post_snapshot)
    app.router.add_get("/api/telemetry", handle_get_telemetry)
    app.router.add_get("/api/blueprint", handle_get_blueprint)
    app.router.add_get("/api/telemetry/stream", handle_stream_telemetry)
    app.router.add_get("/api/telemetry/ws", handle_ws_telemetry)
    app.router.add_get("/ws/telemetry", handle_ws_telemetry)
    app.router.add_get("/ws", handle_ws_telemetry)
    app.router.add_get("/api/graph", handle_get_graph)
    app.router.add_get("/api/graph/summary", handle_get_graph_summary)
    app.router.add_get("/api/node/{node_id}", handle_get_node)
    app.router.add_get("/api/bh/panel", handle_get_bh_panel)
    app.router.add_get("/api/sdi/branch", handle_get_sdi_branch)
    app.router.add_get("/api/sdi/commits", handle_get_sdi_commits)
    app.router.add_get("/api/sdi/capsules", handle_get_sdi_capsules)
    app.router.add_get("/api/metrics/recent", handle_get_metrics_recent)
    app.router.add_post("/api/concept/add", handle_add_concept)
    app.router.add_post("/api/concept", handle_add_concept_legacy)
    app.router.add_get("/", handle_index)

    static_path = os.path.join(BASE_DIR, "static")
    if os.path.exists(static_path):
        try:
            app.router.add_static("/", static_path, show_index=True)
        except Exception:
            pass

    for route in list(app.router.routes()):
        cors.add(route)

    return app

