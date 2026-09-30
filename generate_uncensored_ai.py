name: Update AI Models

on:
  workflow_dispatch:
  schedule:
    - cron: "0 0 * * 1"

permissions:
  contents: write

jobs:
  update:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v7
        with:
          persist-credentials: true

      - name: Setup Python
        uses: actions/setup-python@v7
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install huggingface_hub

      - name: Generate AI model list
        run: python generate_uncensored_ai.py

      - name: Commit and push updated list
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add UNCENSORED_AI.md
          git diff --cached --quiet || git commit -m "Update AI model list"
          git push origin HEAD:main
