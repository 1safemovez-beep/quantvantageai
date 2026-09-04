#!/bin/bash

# Initialize git if needed
if [ ! -d .git ]; then
    git init
    git remote add origin https://github.com/1safemovez-beep/quantvantageai.git
fi

# Final commit with Share features and design restoration
git add .
git commit -m "Final: Bold Chrome design + Robust Share & Print features"

# Push
echo "Attempting to push to GitHub..."
echo "If you are asked for a password, you MUST use your GitHub 'Personal Access Token'."
git push -u origin main
