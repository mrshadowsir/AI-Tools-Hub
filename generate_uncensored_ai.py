from huggingface_hub import HfApi
from pathlib import Path
import html
import re

MAX_MODELS = 1000
OUTPUT_FILE = "UNCENSORED_AI.md"

api = HfApi()

# Fetch models containing "uncensored", sorted by downloads
models = list(
    api.list_models(
        search="uncensored",
        sort="downloads",
        limit=MAX_MODELS
    )
)

def clean(value):
    if not value:
        return ""
    value = html.unescape(str(value))
    return re.sub(r"\s+", " ", value).strip()

def get_family(model_id):
    name = model_id.lower()

    families = {
        "deepseek": "DeepSeek",
        "qwen": "Qwen",
        "llama": "Llama",
        "mistral": "Mistral",
        "mixtral": "Mixtral",
        "gemma": "Gemma",
        "phi": "Phi",
        "dolphin": "Dolphin",
        "nous": "Nous",
        "hermes": "Hermes",
        "wizard": "Wizard",
        "falcon": "Falcon",
        "yi": "Yi",
        "granite": "Granite",
        "olmo": "OLMo",
        "command": "Command"
    }

    for key, family in families.items():
        if key in name:
            return family

    return "Other"

def get_work(model):
    text = (
        clean(getattr(model, "id", "")) + " " +
        clean(getattr(model, "pipeline_tag", "")) + " " +
        " ".join(getattr(model, "tags", []) or [])
    ).lower()

    if "code" in text or "coder" in text:
        return "💻 Coding / Programming"

    if "image" in text or "text-to-image" in text:
        return "🎨 Image Generation"

    if "video" in text or "text-to-video" in text:
        return "🎬 Video Generation"

    if "audio" in text or "speech" in text or "tts" in text:
        return "🎙️ Voice / Audio"

    if "embedding" in text:
        return "🔎 Embeddings / Search"

    if "translation" in text:
        return "🌍 Translation"

    if "summarization" in text:
        return "📝 Summarization"

    return "🧠 General Chat / Reasoning"

def get_best_for(model):
    work = get_work(model)

    mapping = {
        "💻 Coding / Programming": "Coding, programming and technical tasks",
        "🎨 Image Generation": "AI image creation and editing",
        "🎬 Video Generation": "AI video generation",
        "🎙️ Voice / Audio": "Voice, speech and audio",
        "🔎 Embeddings / Search": "Semantic search and RAG",
        "🌍 Translation": "Translation",
        "📝 Summarization": "Summaries and document processing",
        "🧠 General Chat / Reasoning": "General chat, reasoning and writing"
    }

    return mapping.get(work, "General AI tasks")

lines = [
    "# 🔓 Uncensored / Less-Filtered AI Models",
    "",
    "> Automatically collected from Hugging Face.",
    "> Models are sorted by current download count.",
    "",
    f"**Total Models Found:** {len(models)}",
    "",
    "| S.No | Model | Family | Main Work | Best For | Downloads | Likes | Official |",
    "|---:|---|---|---|---|---:|---:|---|"
]

# Ensure highest downloads appear first
models.sort(
    key=lambda x: getattr(x, "downloads", 0) or 0,
    reverse=True
)

for number, model in enumerate(models, 1):
    model_id = clean(getattr(model, "id", "Unknown"))
    family = get_family(model_id)
    work = get_work(model)
    best_for = get_best_for(model)

    downloads = getattr(model, "downloads", 0) or 0
    likes = getattr(model, "likes", 0) or 0

    url = f"https://huggingface.co/{model_id}"

    lines.append(
        f"| {number} | **{model_id}** | {family} | "
        f"{work} | {best_for} | {downloads:,} | "
        f"{likes:,} | [Open](<{url}>) |"
    )

Path(OUTPUT_FILE).write_text(
    "\n".join(lines),
    encoding="utf-8"
)

print(f"✅ Done: {len(models)} models saved to {OUTPUT_FILE}")
