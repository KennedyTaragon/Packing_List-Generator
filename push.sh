
#!/bin/bash

# Colors for better terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for unstaged changes
echo -e "${YELLOW}Checking for changes...${NC}"
if [[ -z $(git status -s) ]]; then
    echo "No changes to commit."
    exit 0
fi

# Add all changes
echo -e "${YELLOW}Adding all changes...${NC}"
git add .

# Prompt for commit message
echo -e "${YELLOW}Enter commit message:${NC}"
read commit_message

# Check if commit message is empty
if [[ -z "$commit_message" ]]; then
    echo "Commit message cannot be empty. Aborting."
    exit 1
fi

# Commit with the provided message
echo -e "${YELLOW}Committing changes...${NC}"
git commit -m "$commit_message"

# Push to remote repository
echo -e "${YELLOW}Pushing to remote repository...${NC}"
git push

# Confirm successful push
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Successfully pushed to remote repository!${NC}"
else
    echo "Failed to push to remote repository."
fi