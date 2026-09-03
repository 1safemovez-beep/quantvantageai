#!/bin/bash

# Initialize git if needed
if [ ! -d .git ]; then
    git init
    git remote add origin https://github.com/1safemovez-beep/quantvantageai.git
fi

# Add the amazing peacock triangle design
git add index.html
git commit -m "Launch: Amazing Peacock Triangle Design and Accio Badge"

# Push
echo "Pushing final amazing design to GitHub..."
git push -u origin main
