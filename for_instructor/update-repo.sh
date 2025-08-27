#!/bin/bash
# Script to sync specific files from template (B) to all student forks (C repos)
# For GitHub Classroom setup with selective file synchronization
set -e

# Configuration (must be provided as command-line arguments)
# Usage: bash update-repo.sh CLASSROOM_ORG REPO_A REPO_B BRANCH FILE_PATTERN1 [FILE_PATTERN2 ...]
if [[ $# -lt 5 ]]; then
  echo "Usage: bash update-repo.sh CLASSROOM_ORG REPO_A REPO_B BRANCH FILE_PATTERN1 [FILE_PATTERN2 ...]"
  echo "Example: bash update-repo.sh sk-classroom sk-classroom/starter sk-classroom/advnetsci-starter-starter main *.md requirements.txt src/"
  echo "FILE_PATTERNS: List of files/directories/patterns to sync (without quotes)"
  echo "              Supports relative paths: ../parent_file.txt ./current_dir/ subdir/file.txt"
  echo "              Supports absolute paths: /absolute/path/file.txt"
  echo "              Supports wildcards: *.py src/*.txt"
  exit 1
fi

CLASSROOM_ORG="$1" # GitHub Classroom organization
REPO_A="$2"        # Source repo
REPO_B="$3"        # Template repo
BRANCH="$4"        # Branch to propagate
shift 4            # Remove first 4 arguments
FILE_PATTERNS="$*" # All remaining arguments as file patterns

echo "Syncing specific files: $REPO_A -> $REPO_B -> all student forks"
echo "Files to sync: $FILE_PATTERNS"

# Function to sync specific files between repos
sync_files() {
    local source_dir="$1"
    local target_dir="$2"
    local patterns="$3"
    local original_dir="$4"  # Directory where script was originally run
    local current_dir=$(pwd)

    cd "$target_dir"

    # Copy each specified file/pattern
    for pattern in $patterns; do
        # Resolve the actual source path (handle relative paths)
        local source_path
        local target_pattern="$pattern"
        
        if [[ "$pattern" == /* ]]; then
            # Absolute path - use as is
            source_path="$pattern"
        elif [[ "$pattern" == ../* ]]; then
            # Relative path going up from source_dir
            source_path="$source_dir/$pattern"
            # Clean up the target pattern (remove ../ prefix)
            target_pattern="${pattern#../}"
        elif [[ "$pattern" == ./* ]]; then
            # Relative path from original directory where script was run
            source_path="$original_dir/$pattern"
            # Clean up the target pattern (remove ./ prefix)  
            target_pattern="${pattern#./}"
        else
            # Regular path relative to source_dir
            source_path="$source_dir/$pattern"
        fi
        
        # Try to resolve the path properly, but preserve the original logic for simple cases
        if [[ "$pattern" != /* && "$pattern" != ../* ]]; then
            # For simple relative paths, try to resolve them from source_dir
            if [[ -e "$source_dir/$pattern" || -d "$source_dir/$pattern" ]]; then
                source_path="$source_dir/$pattern"
            else
                # Try resolving from the original working directory
                original_resolved=$(cd "$original_dir" 2>/dev/null && realpath "$pattern" 2>/dev/null) || original_resolved=""
                if [[ -n "$original_resolved" && -e "$original_resolved" ]]; then
                    source_path="$original_resolved"
                fi
            fi
        fi

        if [[ -e "$source_path" || -d "$source_path" ]]; then
            echo "  Syncing: $pattern -> $target_pattern"
            # Handle directories
            if [[ -d "$source_path" ]]; then
                mkdir -p "$target_pattern"
                cp -r "$source_path"/* "$target_pattern"/ 2>/dev/null || true
            else
                # Handle files (including wildcards)
                mkdir -p "$(dirname "$target_pattern")" 2>/dev/null || true
                cp "$source_path" "$target_pattern" 2>/dev/null || true
            fi
        else
            echo "  Warning: $pattern not found (looked for $source_path)"
        fi
    done

    cd "$current_dir"
}

# First sync A into B
echo "Syncing files from $REPO_A into template $REPO_B..."
ORIGINAL_DIR=$(pwd)  # Store original directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Clone both repos
gh repo clone "$REPO_A" source-repo
gh repo clone "$REPO_B" template-repo

# Debug: Check what files exist in source
echo "Contents of source repo:"
ls -la source-repo/
if [[ -d "source-repo/grading" ]]; then
    echo "Contents of grading directory:"
    ls -la source-repo/grading/
fi

# Sync specific files
sync_files "$TEMP_DIR/source-repo" "$TEMP_DIR/template-repo" "$FILE_PATTERNS" "$ORIGINAL_DIR"

# Commit and push changes to template
cd "$TEMP_DIR/template-repo"
git add -A
if git diff --staged --quiet; then
    echo "No changes to sync to template"
else
    git commit -m "Sync specific files from $REPO_A: $FILE_PATTERNS"
    git push origin "$BRANCH"
    echo "Successfully synced files to $REPO_B"
fi

cd "$TEMP_DIR"
rm -rf source-repo

# Get all forks of B (student repos)
echo "Finding all student forks of $REPO_B..."
STUDENT_REPOS=$(gh api "repos/$REPO_B/forks" --jq '.[].full_name')

# Sync files to each student repo
for repo in $STUDENT_REPOS; do
    echo "Syncing files to student repo $repo..."

    cd "$TEMP_DIR"

    # Remove any existing student-repo directory first
    rm -rf student-repo

    # Clone student repo
    if ! gh repo clone "$repo" student-repo; then
        echo "Failed to clone $repo - skipping"
        continue
    fi

    # Check what directory was actually created
    echo "Debug: Contents of temp directory after clone:"
    ls -la "$TEMP_DIR/"
    
    # Find the actual directory name (in case it's not exactly "student-repo")
    ACTUAL_DIR=$(find "$TEMP_DIR" -maxdepth 1 -type d -name "*" ! -name "template-repo" ! -name "." ! -name ".." | head -1)
    if [[ -n "$ACTUAL_DIR" && "$ACTUAL_DIR" != "$TEMP_DIR/template-repo" ]]; then
        # Rename to expected name if different
        if [[ "$ACTUAL_DIR" != "$TEMP_DIR/student-repo" ]]; then
            mv "$ACTUAL_DIR" "$TEMP_DIR/student-repo" 2>/dev/null || true
        fi
    fi

    # Verify the directory was created
    if [[ ! -d "$TEMP_DIR/student-repo" ]]; then
        echo "Error: student-repo directory not found after clone - skipping $repo"
        continue
    fi

    # Sync specific files
    sync_files "$TEMP_DIR/template-repo" "$TEMP_DIR/student-repo" "$FILE_PATTERNS" "$ORIGINAL_DIR"

    # Navigate to student repo directory and perform git operations
    (
        cd "$TEMP_DIR/student-repo" || {
            echo "Error: Cannot access student-repo directory for $repo - skipping"
            exit 1
        }

        git add -A

        if git diff --staged --quiet; then
            echo "No changes needed for $repo"
        else
            # Check if there are any conflicts by trying to commit
            if git commit -m "Sync template files: $FILE_PATTERNS"; then
                git push origin "$BRANCH"
                echo "Successfully synced files to $repo"
            else
                echo "Failed to commit changes to $repo - may need manual intervention"
            fi
        fi
    ) || echo "Skipping $repo due to directory access issues"

    # Clean up - go back to temp dir and remove student repo
    cd "$TEMP_DIR"
    rm -rf student-repo
done

cd - > /dev/null
rm -rf "$TEMP_DIR"
echo "File synchronization complete!"