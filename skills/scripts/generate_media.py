#!/usr/bin/env python3
"""Generate creative image/video assets through a local OpenAI-compatible endpoint.

This script intentionally enforces fixed models and fixed quality tiers.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List

MODEL_MAP = {
    ("t2i", "portrait"): "nano-banana-2-portrait",
    ("t2i", "landscape"): "nano-banana-2-landscape",
    ("i2i", "portrait"): "nano-banana-2-portrait",
    ("i2i", "landscape"): "nano-banana-2-landscape",
    ("t2v", "portrait"): "veo_3_1_t2v_fast_portrait",
    ("t2v", "landscape"): "veo_3_1_t2v_fast_landscape",
    ("i2v", "portrait"): "veo_3_1_i2v_s_fast_portrait_fl",
    ("i2v", "landscape"): "veo_3_1_i2v_s_fast_fl",
}


def load_port_from_toml(config_path: str) -> int | None:
    """Best-effort parser for [server] port from setting.toml."""
    if not config_path or not os.path.isfile(config_path):
        return None

    in_server_block = False
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("[") and line.endswith("]"):
                    in_server_block = (line == "[server]")
                    continue
                if in_server_block and line.startswith("port"):
                    # Accept forms like: port = 18282
                    parts = line.split("=", 1)
                    if len(parts) != 2:
                        continue
                    value = parts[1].strip().split("#", 1)[0].strip().strip("\"'")
                    if value.isdigit():
                        return int(value)
    except OSError:
        return None

    return None


def endpoint_works(base_url: str, api_key: str, timeout: int = 3) -> bool:
    url = f"{base_url.rstrip('/')}/v1/models"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout):
            return True
    except Exception:
        return False


def discover_base_url(api_key: str) -> str:
    # 1) Explicit env override
    env_url = os.environ.get("MEDIA_API_BASE_URL")
    if env_url:
        return env_url

    # 2) Optional config path override
    config_candidates: List[str] = []
    env_cfg = os.environ.get("FLOW2API_CONFIG")
    if env_cfg:
        config_candidates.append(env_cfg)

    cwd = os.getcwd()
    config_candidates.extend(
        [
            os.path.join(cwd, "config", "setting.toml"),
            os.path.join(cwd, "..", "config", "setting.toml"),
            os.path.join(cwd, "..", "..", "config", "setting.toml"),
        ]
    )

    for cfg in config_candidates:
        port = load_port_from_toml(os.path.abspath(cfg))
        if port:
            candidate = f"http://127.0.0.1:{port}"
            if endpoint_works(candidate, api_key):
                return candidate

    # 3) Common local ports fallback
    for port in [8000, 38000, 18282]:
        candidate = f"http://127.0.0.1:{port}"
        if endpoint_works(candidate, api_key):
            return candidate

    # 4) Last resort
    return "http://127.0.0.1:8000"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate images/videos with fixed creative policy.")
    parser.add_argument("--mode", required=True, choices=["t2i", "i2i", "t2v", "i2v"])
    parser.add_argument("--direction", required=True, choices=["portrait", "landscape"])
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--image", action="append", default=[])
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--api-key", default=os.environ.get("MEDIA_API_KEY", "han1234"))
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Use non-stream validation request path (no media generation output expected).",
    )
    return parser.parse_args()


def to_image_url(value: str) -> str:
    if value.startswith("http://") or value.startswith("https://") or value.startswith("data:image"):
        return value

    path = os.path.abspath(value)
    if not os.path.isfile(path):
        raise ValueError(f"Image path not found: {value}")

    with open(path, "rb") as f:
        data = f.read()

    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = "image/png"

    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def build_messages(prompt: str, image_urls: List[str]) -> List[Dict[str, Any]]:
    if not image_urls:
        return [{"role": "user", "content": prompt}]

    content: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]
    for image_url in image_urls:
        content.append({"type": "image_url", "image_url": {"url": image_url}})
    return [{"role": "user", "content": content}]


def post_stream(
    *,
    base_url: str,
    api_key: str,
    payload: Dict[str, Any],
    timeout: int,
) -> str:
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail[:600]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Connection failed: {exc}") from exc


def extract_media_url(text: str) -> str | None:
    patterns = [
        r"!\[.*?\]\((.*?)\)",
        r"<video[^>]*\ssrc=['\"]([^'\"]+)['\"]",
        r"```html\s*<video[^>]*\ssrc=['\"]([^'\"]+)['\"]",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)

    if text.startswith("http://") or text.startswith("https://") or text.startswith("data:image"):
        return text

    fallback = re.search(r"https?://[^\s)\'\"]+", text)
    if fallback:
        return fallback.group(0)

    return None


def parse_stream_response(stream_text: str) -> Dict[str, Any]:
    final_content = ""
    reasoning_parts: List[str] = []
    errors: List[str] = []

    # Some servers may concatenate a raw JSON error object with the next SSE line
    # (for example: {"error":...}data: [DONE]). Normalize that case first.
    normalized_stream = re.sub(r"}\s*data:", "}\ndata:", stream_text)

    for raw_line in normalized_stream.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("data:"):
            payload = line[5:].strip()
            if payload == "[DONE]":
                continue
            try:
                obj = json.loads(payload)
            except json.JSONDecodeError:
                continue
        else:
            # Fallback: some error chunks may be emitted as raw JSON text.
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

        if isinstance(obj, dict) and "error" in obj:
            msg = obj.get("error", {}).get("message", "generation_failed")
            errors.append(str(msg))
            continue

        choices = obj.get("choices") if isinstance(obj, dict) else None
        if not choices:
            continue

        choice = choices[0] if choices else {}
        delta = choice.get("delta", {}) if isinstance(choice, dict) else {}

        reasoning_content = delta.get("reasoning_content")
        if isinstance(reasoning_content, str) and reasoning_content:
            reasoning_parts.append(reasoning_content)

        content = delta.get("content")
        if isinstance(content, str) and content:
            final_content += content

    media_url = extract_media_url(final_content)

    if media_url:
        return {
            "status": "success",
            "url": media_url,
            "content": final_content,
            "reasoning": "".join(reasoning_parts).strip(),
            "error": None,
        }

    if errors:
        return {
            "status": "error",
            "url": None,
            "content": final_content,
            "reasoning": "".join(reasoning_parts).strip(),
            "error": "; ".join(errors),
        }

    # Fallback: scan for raw error object if line-based parsing missed it.
    error_match = re.search(r'\{"error"\s*:\s*\{.*?\}\}', normalized_stream, flags=re.DOTALL)
    if error_match:
        try:
            error_obj = json.loads(error_match.group(0))
            msg = error_obj.get("error", {}).get("message", "generation_failed")
            return {
                "status": "error",
                "url": None,
                "content": final_content,
                "reasoning": "".join(reasoning_parts).strip(),
                "error": str(msg),
            }
        except json.JSONDecodeError:
            pass

    snippet = normalized_stream.strip()[:500]
    return {
        "status": "error",
        "url": None,
        "content": final_content,
        "reasoning": "".join(reasoning_parts).strip(),
        "error": f"No media URL found in response. Snippet: {snippet}",
    }


def parse_check_only_response(response_text: str) -> Dict[str, Any]:
    try:
        obj = json.loads(response_text)
    except json.JSONDecodeError:
        snippet = response_text.strip()[:500]
        return {
            "status": "error",
            "url": None,
            "content": "",
            "reasoning": "",
            "error": f"Invalid JSON response. Snippet: {snippet}",
        }

    if isinstance(obj, dict) and "error" in obj:
        msg = obj.get("error", {}).get("message", "generation_failed")
        return {
            "status": "error",
            "url": None,
            "content": "",
            "reasoning": "",
            "error": str(msg),
        }

    message = ""
    choices = obj.get("choices") if isinstance(obj, dict) else None
    if isinstance(choices, list) and choices:
        message = (
            choices[0]
            .get("message", {})
            .get("content", "")
        )

    if message:
        return {
            "status": "success",
            "url": None,
            "content": message,
            "reasoning": "",
            "error": None,
        }

    return {
        "status": "error",
        "url": None,
        "content": "",
        "reasoning": "",
        "error": "Missing completion content in check-only response.",
    }


def generate_once(
    *,
    mode: str,
    direction: str,
    prompt: str,
    image_urls: List[str],
    base_url: str,
    api_key: str,
    timeout: int,
    check_only: bool,
) -> Dict[str, Any]:
    model = MODEL_MAP[(mode, direction)]

    payload = {
        "model": model,
        "messages": build_messages(prompt, image_urls),
        "stream": not check_only,
    }

    raw = post_stream(base_url=base_url, api_key=api_key, payload=payload, timeout=timeout)
    if check_only:
        result = parse_check_only_response(raw)
    else:
        result = parse_stream_response(raw)
    result["model"] = model
    return result


def main() -> int:
    args = parse_args()

    if args.batch_size < 1:
        print("batch-size must be >= 1", file=sys.stderr)
        return 2

    image_inputs = args.image or []
    base_url = args.base_url or discover_base_url(args.api_key)

    if args.mode in {"i2i", "i2v"} and not image_inputs:
        print(f"mode '{args.mode}' requires at least one --image input", file=sys.stderr)
        return 2

    if args.mode == "i2v" and len(image_inputs) > 2:
        print("mode 'i2v' supports at most two --image inputs", file=sys.stderr)
        return 2

    if args.mode in {"t2i", "t2v"} and image_inputs:
        print(f"warning: mode '{args.mode}' ignores --image inputs", file=sys.stderr)
        image_inputs = []

    try:
        image_urls = [to_image_url(v) for v in image_inputs]
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    results: List[Dict[str, Any]] = []

    for idx in range(1, args.batch_size + 1):
        started = time.time()
        try:
            item = generate_once(
                mode=args.mode,
                direction=args.direction,
                prompt=args.prompt,
                image_urls=image_urls,
                base_url=base_url,
                api_key=args.api_key,
                timeout=args.timeout,
                check_only=args.check_only,
            )
        except Exception as exc:
            item = {
                "status": "error",
                "url": None,
                "content": "",
                "reasoning": "",
                "error": str(exc),
                "model": MODEL_MAP[(args.mode, args.direction)],
            }

        item["index"] = idx
        item["mode"] = args.mode
        item["direction"] = args.direction
        item["elapsed_seconds"] = round(time.time() - started, 2)
        results.append(item)

    success_count = sum(1 for item in results if item.get("status") == "success")
    failure_count = len(results) - success_count

    output = {
        "ok": success_count > 0,
        "summary": {
            "mode": args.mode,
            "direction": args.direction,
            "batch_size": args.batch_size,
            "succeeded": success_count,
            "failed": failure_count,
            "base_url": base_url,
            "check_only": bool(args.check_only),
        },
        "results": results,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
