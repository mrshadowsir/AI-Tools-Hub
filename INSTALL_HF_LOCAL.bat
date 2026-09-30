@echo off
title Open-Source AI Lab - Hugging Face Local Setup
python -m pip install --upgrade pip
python -m pip install torch transformers accelerate sentencepiece
echo.
echo Hugging Face Local runtime installed.
pause
