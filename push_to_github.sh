#!/bin/bash

# Initialize git if needed
if [ ! -d .git ]; then
    git init
    git remote add origin https://github.com/1safemovez-beep/quantvantageai.git
fi

# Add the new Vercel config and luxury design
git add .
git commit -m "Launch: Sophisticated UI and Vercel deployment config"

# Push
echo "Pushing to GitHub..."
git push -u origin main
