---
name: flow2api
description: Generate creative images and videos for users with strict defaults and minimal controls. Use this skill when the user asks to create visual assets through text or image prompts, including text-to-image (T2I), image-to-image (I2I), text-to-video (T2V), and image-to-video (I2V). Supports batch generation. Keep user controls limited to direction (portrait or landscape), prompt, batch size, and input image files when required.
---

# Flow2API

## Overview

Use this skill to create images and videos with a strict policy: fixed model families, fixed quality tiers, and fixed direction options. Expose only simple creative controls to the user.

## Workflow

1. Identify the mode from user intent:
- `t2i`: text-to-image
- `i2i`: image-to-image
- `t2v`: text-to-video
- `i2v`: image-to-video

2. Collect only required inputs:
- `prompt` (required)
- `direction` (`portrait` or `landscape`)
- `batch_size` (default `1`)
- `image` inputs only for `i2i` and `i2v`

3. Run the bundled script:

```bash
python3 scripts/generate_media.py \
  --mode <t2i|i2i|t2v|i2v> \
  --direction <portrait|landscape> \
  --prompt "<user prompt>" \
  --batch-size <n> \
  [--image /absolute/path/to/image1] \
  [--image /absolute/path/to/image2]
```

Low-cost contract validation (no media output expected):

```bash
python3 scripts/generate_media.py \
  --mode <t2i|i2i|t2v|i2v> \
  --direction <portrait|landscape> \
  --prompt "<user prompt>" \
  --check-only
```

Environment overrides:
- `MEDIA_API_BASE_URL` to set the endpoint base URL.
- `MEDIA_API_KEY` to set the bearer token.
- `FLOW2API_CONFIG` (optional) to point to a specific `setting.toml` for automatic port discovery.

Default endpoint behavior:
- If `--base-url` is omitted, the script auto-discovers the endpoint in this order:
1. `MEDIA_API_BASE_URL` environment variable
2. `FLOW2API_CONFIG` or nearby `config/setting.toml`
3. common local ports (`8000`, `38000`, `18282`)

4. Read JSON output and report concise results:
- Return successful URLs first.
- If partial failure exists, include the failed indices and reasons.
- Avoid discussing backend service names or internal model routing.

## Mode Examples

```bash
# T2I
python3 scripts/generate_media.py --mode t2i --direction portrait --prompt "A cinematic poster" --batch-size 2

# I2I
python3 scripts/generate_media.py --mode i2i --direction landscape --prompt "Convert to watercolor" --image /abs/input.png

# T2V
python3 scripts/generate_media.py --mode t2v --direction landscape --prompt "Aerial city flythrough" --batch-size 1

# I2V (one or two images)
python3 scripts/generate_media.py --mode i2v --direction portrait --prompt "Transition from day to night" --image /abs/start.png --image /abs/end.png
```

## Behavior Rules

- Enforce `portrait` or `landscape` only.
- Do not offer model selection.
- Do not offer quality selection.
- Respect batch generation requests.
- For `i2v`, allow at most two images.
- Treat upstream generation as potentially unstable.
- If generation fails with HTTP 500, timeout, or transient upstream errors, retry by re-running the same request.
- For single generation, retry up to 2 additional attempts before returning a final failure.
- For batch generation, keep successful items and retry only failed items.
- If all batch items fail, surface a compact error summary and suggest a prompt or input-image retry.

## Output Format

- For success: provide a numbered list with each generated asset URL.
- For partial success: include a short `Failed:` section with index and reason.
- Keep responses concise and production-oriented.

## Resources

- Model and routing policy: `references/model-policy.md`
- Execution script: `scripts/generate_media.py`
