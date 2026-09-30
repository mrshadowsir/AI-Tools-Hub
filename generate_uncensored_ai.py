from huggingface_hub import HfApi
from pathlib import Path
import html
import re

MAX_MODELS = 1000
OUTPUT_FILE = "UNCENSORED_AI.md"

api = HfApi()

models = list(
    api.list_models(
        search="uncensored",
        sort="downloads",
        direction=-1,
        limit=MAX_MODELS,
        expand=["downloads", "likes", "pipeline_tag", "library_name", "tags"]
    )
)

def clean(text):
    if not text:
        return ""
    text = html.unescape(str(text))
    return re.sub(r"\s+", " ", text).strip()

def work_for(model):
    tags = " ".join(model.tags or []).lower()
    pipe = (model.pipeline_tag or "").lower()

    if "code" in tags or "code" in pipe:
        return "💻 Coding / programming"
    if "image" in tags or "text-to-image" in pipe:
        return "🎨 Image generation"
    if "audio" in tags or "text-to-speech" in pipe:
        return "🎙️ Voice / audio"
    if "video" in tags or "text-to-video" in pipe:
        return "🎬 Video"
    if "embedding" in tags or "feature-extraction" in pipe:
        return "🔎 Embeddings / search"
    if "summarization" in pipe:
        return "📝 Summarization"
    if "translation" in pipe:
        return "🌍 Translation"
    return "🧠 General chat / reasoning"

def model_family(model_id):
    x = model_id.lower()

    families = [
        "deepseek", "qwen", "llama", "mistral", "mixtral",
        "gemma", "phi", "yi", "nous", "dolphin",
        "hermes", "wizardlm", "falcon", "vicuna",
        "command", "granite", "olmo"
    ]

    for name in families:
        if name in x:
            return name.title()

    return "Other / Custom"

lines = [
    "# 🔓 Uncensored / Less-Filtered AI Models",
    "",
    "> Automatically collected from Hugging Face. Ranked by current downloads.",
    "> \"Best for\" is a heuristic based on model metadata/tags, not a benchmark winner.",
    "",
    f"**Models collected:** {len(models)}",
    "",
    "| S.No | Model | Family | Main Work | Downloads | Likes | Official |",
    "|---:|---|---|---|---:|---:|---|"
]

for i, m in enumerate(models, 1):
    model_id = clean(m.id)
    family = model_family(model_id)
    work = work_for(m)
    downloads = getattr(m, "downloads", 0) or 0
    likes = getattr(m, "likes", 0) or 0

    url = f"https://huggingface.co/{model_id}"

    lines.append(
        f"| {i} | **{model_id}** | {family} | {work} | "
        f"{downloads:,} | {likes:,} | [Open](<{url}>) |"
    )

Path(OUTPUT_FILE).write_text("\n".join(lines), encoding="utf-8")

print(f"Done! {len(models)} models saved to {OUTPUT_FILE}")
