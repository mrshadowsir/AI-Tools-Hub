from huggingface_hub import HfApi
from pathlib import Path
import re

TARGET_PER_CATEGORY = 10000
SEARCH_LIMIT = 10000
MODEL_DIR = Path("models")
INDEX_FILE = Path("OPEN_SOURCE_AI_MODELS.md")

api = HfApi()

# Common SPDX-style open licenses. Individual model cards should still be checked.
OPEN_LICENSES = {
    "mit",
    "apache-2.0",
    "apache-2.0-openrail-m",
    "bsd-2-clause",
    "bsd-3-clause",
    "bsd",
    "mpl-2.0",
    "gpl-3.0",
    "lgpl-3.0",
    "agpl-3.0",
    "cc-by-4.0",
    "cc-by-sa-4.0",
    "cc0-1.0",
    "unlicense",
}

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

def get_license(model):
    card = getattr(model, "cardData", None)
    if isinstance(card, dict):
        return clean(card.get("license")).lower()
    try:
        return clean(getattr(card, "license", "")).lower()
    except Exception:
        return ""

def is_open_public(model):
    return (
        getattr(model, "gated", False) is not True
        and get_license(model) in OPEN_LICENSES
    )

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

    # Pipeline/task discovery
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

    # Keyword discovery improves specialist categories
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
        f"> **Best for:** {config['best_for']}",
        "",
        f"**Models found: {len(models)}**",
        "",
        "| S.No | Model | Family | License | Downloads | Likes | Official |",
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
    "# 🆓 Open-Source AI Model Directory",
    "",
    "> Category-wise directory of public, non-gated Hugging Face models with a declared license from this script's open-license allowlist.",
    "> Up to 10,000 models are collected per category when available.",
    "",
    "| S.No | Category | Models | Best for |",
    "|---:|---|---:|---|",
]

total = 0

for category_name, config in CATEGORIES.items():
    print(f"Collecting {category_name}...")

    models = collect_models(
        config["pipeline"],
        config["searches"],
    )

    path = write_category(category_name, config, models)
    total += len(models)

    relative = path.as_posix()
    index.append(
        f"| {len(index)} | [{category_name}]({relative}) | "
        f"{len(models):,} | {config['best_for']} |"
    )

index.extend([
    "",
    f"**Total category entries:** {total:,}",
    "",
    "### ⚠️ License note",
    "",
    "Public availability does not automatically mean every use is permitted. "
    "Check each model card and license before redistribution or commercial use.",
])

INDEX_FILE.write_text("\n".join(index) + "\n", encoding="utf-8")

print("=" * 60)
print(f"✅ Generated {total:,} category entries.")
print(f"✅ Index: {INDEX_FILE}")
print(f"✅ Category files: {MODEL_DIR}/")
print("=" * 60)
