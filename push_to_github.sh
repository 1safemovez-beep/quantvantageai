#!/bin/bash
# QuantVantage AI - GitHub Automation
# Usage: ./push_to_github.sh <YOUR_GITHUB_TOKEN>

TOKEN=$1
REPO_URL="https://1safemovez-beep:${TOKEN}@github.com/1safemovez-beep/quantvantageai.git"

git init
git config --global user.email "1safemovez@gmail.com"
git config --global user.name "1safemovez-beep"
git add streamlit_app.py index.html requirements.txt examples/streamlit_app.py
git commit -m "Sync examples/streamlit_app.py and add Pro features"
git branch -M main
git remote add origin "${REPO_URL}" || git remote set-url origin "${REPO_URL}"
git push -u origin main --force
