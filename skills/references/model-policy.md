# Model Policy

This skill enforces a strict, non-configurable model policy.

## Fixed Direction Options

- `portrait`
- `landscape`

No other direction values are allowed.

## Fixed Image Policy

- Model family is fixed to `nano-banana-2-*` (NARWHAL / Gemini 3.1 Flash Image).

Mapping:

- `t2i + portrait` -> `nano-banana-2-portrait`
- `t2i + landscape` -> `nano-banana-2-landscape`
- `i2i + portrait` -> `nano-banana-2-portrait`
- `i2i + landscape` -> `nano-banana-2-landscape`

## Fixed Video Policy

- Model family is fixed to `veo_3_1_*`.

Mapping:

- `t2v + portrait` -> `veo_3_1_t2v_fast_portrait`
- `t2v + landscape` -> `veo_3_1_t2v_fast_landscape`
- `i2v + portrait` -> `veo_3_1_i2v_s_fast_portrait_fl`
- `i2v + landscape` -> `veo_3_1_i2v_s_fast_fl`

## Input Rules

- `t2i` and `t2v`: text prompt only.
- `i2i`: one or more input images.
- `i2v`: one or two input images.
- `batch_size`: integer >= 1.
