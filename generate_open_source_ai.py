from huggingface_hub import HfApi
from pathlib import Path
import re

TARGET_PER_CATEGORY = 10000
SEARCH_LIMIT = 10000
MODEL_DIR = Path("models")
INDEX_FILE = Path("OPEN_SOURCE_AI_MODELS.md")

api = HfApi()

# Conservative allowlist of OSI-approved software licenses.
# Non-OSI model licenses such as OpenRAIL and CC-BY-NC are intentionally excluded.
OPEN_LICENSES = {
    "0bsd",
    "afl-3.0",
    "apache-1.1",
    "apache-2.0",
    "artistic-2.0",
    "bsd-1-clause",
    "bsd-2-clause",
    "bsd-3-clause",
    "cddl-1.1",
    "cpl-1.0",
    "epl-1.0",
    "epl-2.0",
    "eupl-1.2",
    "gpl-2.0",
    "gpl-3.0",
    "agpl-3.0",
    "agpl-v3",
    "isc",
    "isc-license-txt",
    "lgpl-2.0",
    "lgpl-2.1",
    "lgpl-3.0",
    "mit",
    "mit-0",
    "mpl-1.0",
    "mpl-1.1",
    "mpl-2.0",
    "ms-pl",
    "ncsa",
    "osl-3.0",
    "postgresql",
    "upl-1.0",
    "unlicense",
    "zlib",
}

RESTRICTED_MARKERS = (
    "non-commercial",
    "noncommercial",
    "no-commercial-use",
    "not-for-commercial-use",
    "research-only",
    "research_only",
    "openrail",
    "cc-by-nc",
    "by-nc",
    "proprietary",
    "commercial-use-not-allowed",
    "license-restricted",
)

CATEGORIES = {
    "LLM / Chat / Reasoning": {
        "pipeline": "text-generation",
        "searches": ["chat", "instruct", "reasoning", "language-model"],
        "best_for": "General chat, writing, reasoning and text generation",
        "slug": "01-llm-chat-reasoning",
    },
    "Coding AI": {
        "pipeline": "text-generation",
        "searches": ["coder", "coding", "code", "programming"],
        "best_for": "Programming, code generation and software development",
        "slug": "02-coding-ai",
    },
    "Text Classification": {
        "pipeline": "text-classification",
        "searches": ["classification", "sentiment"],
        "best_for": "Classification, sentiment and text labeling",
        "slug": "03-text-classification",
    },
    "Question Answering": {
        "pipeline": "question-answering",
        "searches": ["question-answering", "qa"],
        "best_for": "Question answering and knowledge extraction",
        "slug": "04-question-answering",
    },
    "Translation": {
        "pipeline": "translation",
        "searches": ["translation", "translate"],
        "best_for": "Language translation",
        "slug": "05-translation",
    },
    "Summarization": {
        "pipeline": "summarization",
        "searches": ["summarization", "summary"],
        "best_for": "Summaries and document compression",
        "slug": "06-summarization",
    },
    "Image Classification": {
        "pipeline": "image-classification",
        "searches": ["image-classification"],
        "best_for": "Image classification and recognition",
        "slug": "07-image-classification",
    },
    "Image Generation": {
        "pipeline": "text-to-image",
        "searches": ["image-generation", "diffusion", "text-to-image"],
        "best_for": "Text-to-image generation and creative visuals",
        "slug": "08-image-generation",
    },
    "Image Segmentation": {
        "pipeline": "image-segmentation",
        "searches": ["segmentation"],
        "best_for": "Pixel-level image segmentation",
        "slug": "09-image-segmentation",
    },
    "Object Detection": {
        "pipeline": "object-detection",
        "searches": ["object-detection", "yolo"],
        "best_for": "Object detection and computer vision",
        "slug": "10-object-detection",
    },
    "Speech Recognition": {
        "pipeline": "automatic-speech-recognition",
        "searches": ["speech-recognition", "whisper", "asr"],
        "best_for": "Speech-to-text and transcription",
        "slug": "11-speech-recognition",
    },
    "Text To Speech": {
        "pipeline": "text-to-speech",
        "searches": ["text-to-speech", "tts", "voice"],
        "best_for": "Text-to-speech and voice synthesis",
        "slug": "12-text-to-speech",
    },
    "Audio / Music": {
        "pipeline": "text-to-audio",
        "searches": ["music", "audio", "sound"],
        "best_for": "Audio and music generation",
        "slug": "13-audio-music",
    },
    "Embeddings / RAG": {
        "pipeline": "feature-extraction",
        "searches": ["embedding", "retrieval", "reranker"],
        "best_for": "Embeddings, semantic search and RAG",
        "slug": "14-embeddings-rag",
    },
}

def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()

def normalize(value):
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return " ".join(normalize(v) for v in value)
    if isinstance(value, dict):
        return " ".join(f"{k}:{normalize(v)}" for k, v in value.items())
    return clean(value).lower()

def get_license(model):
    card = getattr(model, "cardData", None)

    if isinstance(card, dict):
        value = card.get("license", "")
        if isinstance(value, dict):
            value = value.get("spdx_id") or value.get("id") or value.get("name") or ""
        return normalize(value)

    try:
        value = getattr(card, "license", "")
        return normalize(value)
    except Exception:
        return ""

def is_open_public(model):
    gated = getattr(model, "gated", False)
    if gated:
        return False

    private = getattr(model, "private", False)
    if private:
        return False

    license_id = get_license(model)
    if license_id not in OPEN_LICENSES:
        return False

    metadata = " ".join(
        [
            normalize(getattr(model, "id", "")),
            normalize(getattr(model, "tags", []) or []),
            license_id,
        ]
    )

    return not any(marker in metadata for marker in RESTRICTED_MARKERS)

def model_family(model_id):
    name = model_id.lower()

    families = [
        ("deepseek", "DeepSeek"),
        ("qwen", "Qwen"),
        ("llama", "Llama"),
        ("mistral", "Mistral"),
        ("mixtral", "Mixtral"),
        ("gemma", "Gemma"),
        ("phi", "Phi"),
        ("dolphin", "Dolphin"),
        ("nous", "Nous"),
        ("hermes", "Hermes"),
        ("falcon", "Falcon"),
        ("yi", "Yi"),
        ("granite", "Granite"),
        ("olmo", "OLMo"),
        ("command", "Command"),
        ("whisper", "Whisper"),
        ("stable-diffusion", "Stable Diffusion"),
        ("flux", "FLUX"),
    ]

    for key, family in families:
        if key in name:
            return family

    return "Custom / Other"

def collect_models(pipeline, searches):
    found = {}

    try:
        for model in api.list_models(
            filter=pipeline,
            gated=False,
            sort="downloads",
            limit=SEARCH_LIMIT,
            cardData=True,
        ):
            if is_open_public(model):
                found[model.id] = model
    except Exception as exc:
        print(f"Pipeline error ({pipeline}): {exc}")

    for query in searches:
        try:
            for model in api.list_models(
                search=query,
                gated=False,
                sort="downloads",
                limit=SEARCH_LIMIT,
                cardData=True,
            ):
                if is_open_public(model):
                    found[model.id] = model
        except Exception as exc:
            print(f"Search error ({query}): {exc}")

    models = list(found.values())
    models.sort(
        key=lambda model: getattr(model, "downloads", 0) or 0,
        reverse=True,
    )
    return models[:TARGET_PER_CATEGORY]

def write_category(category_name, config, models):
    filename = MODEL_DIR / f"{config['slug']}.md"

    lines = [
        f"# {category_name}",
        "",
        f"> **Use:** {config['best_for']}",
        "",
        f"**Open-license models found: {len(models):,}**",
        "",
        "| S.No | Model | Family | OSI License | Downloads | Likes | Official |",
        "|---:|---|---|---|---:|---:|---|",
    ]

    for i, model in enumerate(models, 1):
        name = clean(model.id)
        family = model_family(name)
        license_id = get_license(model) or "unknown"
        downloads = getattr(model, "downloads", 0) or 0
        likes = getattr(model, "likes", 0) or 0
        url = f"https://huggingface.co/{name}"

        lines.append(
            f"| {i} | **{name}** | {family} | {license_id} | "
            f"{downloads:,} | {likes:,} | [Open]({url}) |"
        )

    filename.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return filename

MODEL_DIR.mkdir(parents=True, exist_ok=True)

index = [
    "# 🆓 Open-Source / Open-License AI Model Directory",
    "",
    "> Strict automated filter: public + non-gated + declared OSI-approved license.",
    "> Paid-only, trial-only, proprietary, OpenRAIL, non-commercial and other restricted model licenses are excluded.",
    "",
    "> **Important:** OSI's Open Source AI Definition requires more than a permissive weight license; it also covers training-data information and the training/runtime code. This directory is therefore a **license-qualified index**, not a certification that every listed model satisfies every OSAID requirement.",
    "",
    "| S.No | Category | Models | Use |",
    "|---:|---|---:|---|",
]

total = 0

for number, (category_name, config) in enumerate(CATEGORIES.items(), 1):
    print(f"Collecting {category_name}...")

    models = collect_models(
        config["pipeline"],
        config["searches"],
    )

    path = write_category(category_name, config, models)
    total += len(models)

    index.append(
        f"| {number} | [{category_name}]({path.as_posix()}) | "
        f"{len(models):,} | {config['best_for']} |"
    )

index.extend(
    [
        "",
        f"**Total category entries:** {total:,}",
        "",
        "## 🔍 What is excluded?",
        "",
        "- Paid-only or subscription-only hosted services",
        "- Trial-only services",
        "- Gated models",
        "- Proprietary/non-open licenses",
        "- Non-commercial / research-only model licenses",
        "- OpenRAIL and similar non-OSI model licenses",
        "- Models without a declared qualifying license",
        "",
        "Always read the individual model card and license before redistribution or commercial use.",
    ]
)

INDEX_FILE.write_text("\n".join(index) + "\n", encoding="utf-8")

print("=" * 60)
print(f"✅ Generated {total:,} license-qualified entries.")
print(f"✅ Index: {INDEX_FILE}")
print(f"✅ Category files: {MODEL_DIR}/")
print("=" * 60)
