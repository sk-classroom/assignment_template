#!/bin/bash

# Script to propagate changes from template (B) to all student forks (C repos)
# For GitHub Classroom setup

set -e

# Configuration (must be provided as command-line arguments)
# Usage: bash update-repo.sh CLASSROOM_ORG REPO_A REPO_B BRANCH

if [[ $# -ne 4 ]]; then
  echo "Usage: bash update-repo.sh CLASSROOM_ORG REPO_A REPO_B BRANCH"
  echo "Example: bash update-repo.sh sk-classroom sk-classroom/starter sk-classroom/advnetsci-starter-starter main"
  exit 1
fi

CLASSROOM_ORG="$1" # GitHub Classroom organization
REPO_A="$2"        # Source repo
REPO_B="$3"        # Template repo
BRANCH="$4"        # Branch to propagate

echo "Propagating changes: $REPO_A -> $REPO_B -> all student forks"

# First merge A into B
echo "Merging source $REPO_A into template $REPO_B..."
TEMP_DIR=$(mktemp -d)
#mkdir tmp
#TEMP_DIR=tmp
cd "$TEMP_DIR"
gh repo clone "$REPO_B"
cd "$(basename "$REPO_B")"
git remote add source "https://github.com/$REPO_A.git"
git fetch source
if git merge "source/$BRANCH" --no-edit --allow-unrelated-histories; then
  git push origin "$BRANCH"
  echo "Successfully merged $REPO_A into $REPO_B"
else
  echo "Merge conflict detected when merging $REPO_A into $REPO_B. Conflicting files:"
  git diff --name-only --diff-filter=U | sed 's/^/  - /' || true
  read -r -p "Force overwrite $REPO_B:$BRANCH with $REPO_A:$BRANCH? [y/N]: " FORCE_OVERWRITE
  if [[ "$FORCE_OVERWRITE" =~ ^[Yy](es)?$ ]]; then
    echo "Overwriting $REPO_B:$BRANCH with contents of $REPO_A:$BRANCH"
    git merge --abort || true
    git checkout -B "$BRANCH"
    git ls-files -z | xargs -0 git rm -f || true
    git clean -fdx
    git checkout "source/$BRANCH" -- .
    git add -A
    git commit -m "Overwrite template with source repository contents from $REPO_A@$BRANCH" || true
    git push origin "$BRANCH"
  else
    echo "Aborting for manual resolution."
    git merge --abort
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
    exit 1
  fi
fi
cd - > /dev/null
rm -rf "$TEMP_DIR"

# Get all forks of B (student repos)
echo "Finding all student forks of $REPO_B..."
STUDENT_REPOS=$(gh api "repos/$REPO_B/forks" --jq '.[].full_name')

# Merge B into each student repo
for repo in $STUDENT_REPOS; do
   echo "Merging $REPO_B into student repo $repo..."
   TEMP_DIR=$(mktemp -d)
   cd "$TEMP_DIR"

   # Clone student repo
   gh repo clone "$repo" || { echo "Failed to clone $repo"; continue; }
   cd "$(basename "$repo")"

   # Add template as remote and merge
   git remote add template "https://github.com/$REPO_B.git"
   git fetch template

   if git merge "template/$BRANCH" --no-edit --allow-unrelated-histories; then
      git push origin "$BRANCH"
      echo "Successfully merged into $repo"
   else
      echo "Merge conflict detected in $repo - creating PR instead. Conflicting files:"
      git diff --name-only --diff-filter=U | sed 's/^/  - /' || true
      # Abort the conflicted merge
      git merge --abort

      # Create a new branch for the update
      UPDATE_BRANCH="template-update-$(date +%Y%m%d-%H%M%S)"
      git checkout -b "$UPDATE_BRANCH"

      # Merge with conflict markers
      git merge "template/$BRANCH" --no-edit --allow-unrelated-histories || true

      # Add all files (including conflict markers)
      git add .
      git commit -m "Merge template updates (conflicts need resolution)"

      # Push the branch
      git push origin "$UPDATE_BRANCH"

      # Create PR
      gh pr create --repo "$repo" \
         --title "Template Update (Manual Resolution Required)" \
         --body "This PR contains updates from the template repository. Some files have merge conflicts that need manual resolution before merging." \
         --head "$UPDATE_BRANCH" \
         --base "$BRANCH"

      echo "Created PR for $repo with conflicts to resolve manually"
   fi

   cd - > /dev/null
   rm -rf "$TEMP_DIR"
done

echo "Propagation complete!"
