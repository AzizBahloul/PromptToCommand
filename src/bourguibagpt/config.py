VERSION = "2.1.0"
# qwen2.5-coder:1.5b was benchmarked against qwen3.5:0.8b on this exact
# request-to-command task: same download size (~1GB), ~2x faster locally,
# and it correctly embeds every argument in "command" instead of splitting
# them into "target" the way smaller code models tend to.
MODEL_NAME = "qwen2.5-coder:1.5b"