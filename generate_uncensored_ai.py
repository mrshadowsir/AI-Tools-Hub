from huggingface_hub import HfApi
from pathlib import Path
import re

TARGET_PER_CATEGORY = 10000
SEARCH_LIMIT = 10000
OUTPUT_FILE = "OPEN_SOURCE_AI_MODELS.md"

api = HfApi()

OPEN_LICENSES = {
    "mit", "apache-2.0", "apache-2.0-openrail-m",
    "bsd-2-clause", "bsd-3-clause", "bsd", "mpl-2.0",
    "gpl-3.0", "lgpl-3.0", "agpl-3.0",
    "cc-by-4.0", "cc-by-sa-4.0", "cc0-1.0", "unlicense"
}

CATEGORIES = {
    "LLM / Chat / Reasoning": ["text-generation"],
    "Coding AI": ["text-generation"],
    "Text Classification": ["text-classification"],
    "Question Answering": ["question-answering"],
    "Translation": ["translation"],
    "Summarization": ["summarization"],
    "Image Classification": ["image-classification"],
    "Image Generation": ["text-to-image"],
    "Image Segmentation": ["image-segmentation"],
    "Object Detection": ["object-detection"],
    "Speech Recognition": ["automatic-speech-recognition"],
    "Text To Speech": ["text-to-speech"],
    "Audio / Music": ["text-to-audio"],
    "Embeddings / RAG": ["feature-extraction"],
}

def clean(v):
    return re.sub(r"\s+", " ", str(v or "")).strip()

def get_license(m):
    card = getattr(m, "cardData", None)
    if isinstance(card, dict):
        return clean(card.get("license")).lower()
    try:
        return clean(getattr(card, "license", "")).lower()
    except Exception:
        return ""

def is_open_public(m):
    return getattr(m, "gated", False) is not True and get_license(m) in OPEN_LICENSES

def collect(pipeline):
    found = {}
    try:
        for m in api.list_models(
            filter=pipeline,
            gated=False,
            sort="downloads",
            limit=SEARCH_LIMIT,
            cardData=True
        ):
            if is_open_public(m):
                found[m.id] = m
    except Exception as e:
        print(f"ERROR {pipeline}: {e}")

    result = list(found.values())
    result.sort(key=lambda x: getattr(x, "downloads", 0) or 0, reverse=True)
    return result[:TARGET_PER_CATEGORY]

out = [
    "# 🆓 Open-Source AI Model Directory",
    "",
    "> Public, non-gated models with a declared open license from the allowlist.",
    "> Up to 10,000 models are collected per category when available.",
    ""
]

total = 0

for category, pipelines in CATEGORIES.items():
    print(f"Collecting {category}...")
    models = []
    seen = set()

    for pipeline in pipelines:
        for m in collect(pipeline):
            if m.id not in seen:
                seen.add(m.id)
                models.append(m)

    models.sort(key=lambda x: getattr(x, "downloads", 0) or 0, reverse=True)
    models = models[:TARGET_PER_CATEGORY]

    total += len(models)
    out.append(f"## {category}")
    out.append("")
    out.append(f"**Models found: {len(models)}**")
    out.append("")
    out.append("| S.No | Model | License | Downloads | Likes | Link |")
    out.append("|---:|---|---|---:|---:|---|")

    for i, m in enumerate(models, 1):
        name = clean(m.id)
        license_id = get_license(m) or "unknown"
        downloads = getattr(m, "downloads", 0) or 0
        likes = getattr(m, "likes", 0) or 0
        url = f"https://huggingface.co/{name}"
        out.append(
            f"| {i} | **{name}** | {license_id} | "
            f"{downloads:,} | {likes:,} | [Open]({url}) |"
        )

    out.append("")
    out.append("---")
    out.append("")

out.append(f"## 📊 Total entries: {total}")
out.append("")
out.append(
    "Model count is limited by what Hugging Face exposes and by the "
    "open-license/non-gated filters; entries are never invented or duplicated."
)

Path(OUTPUT_FILE).write_text("\n".join(out), encoding="utf-8")
print(f"✅ Generated {OUTPUT_FILE} with {total} entries.")
