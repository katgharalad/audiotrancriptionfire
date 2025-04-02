#!/usr/bin/env python3
"""
This script finalizes preparation for GitHub upload by:
1. Removing unnecessary directories
2. Cleaning up temporary files
3. Providing git commands to commit and push
"""

import os
import shutil
import sys
import subprocess

def print_step(message):
    """Print a step message with formatting"""
    print("\n" + "="*80)
    print(message.center(80))
    print("="*80)

def cleanup_directories():
    """Remove unnecessary directories"""
    print_step("CLEANING UP DIRECTORIES")
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Directories to remove
    dirs_to_remove = [
        "audiotranscript copy",
        "__pycache__",
        "audio/__pycache__",
        "ml_interpretation/__pycache__"
    ]
    
    for dir_path in dirs_to_remove:
        full_path = os.path.join(root_dir, dir_path)
        if os.path.exists(full_path):
            print(f"Removing directory: {full_path}")
            try:
                shutil.rmtree(full_path)
            except Exception as e:
                print(f"Error removing {full_path}: {e}")
    
    print("Directories cleanup complete.")

def cleanup_files():
    """Remove unnecessary files"""
    print_step("CLEANING UP FILES")
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Files to remove
    files_to_remove = [
        ".DS_Store",
        "audio/.DS_Store",
        "ml_interpretation/.DS_Store",
        "prepare_for_upload.py", # Remove the preparation script itself
        "README_INTEGRATED.md",  # These will be replaced by the new README.md
        "README_ML_ONLY.md"
    ]
    
    for file_path in files_to_remove:
        full_path = os.path.join(root_dir, file_path)
        if os.path.exists(full_path):
            print(f"Removing file: {full_path}")
            try:
                os.remove(full_path)
            except Exception as e:
                print(f"Error removing {full_path}: {e}")
    
    print("Files cleanup complete.")

def print_git_instructions():
    """Print instructions for git commit and push"""
    print_step("GIT UPLOAD INSTRUCTIONS")
    
    print("""
To upload your files to GitHub, run the following commands:

# Add all files to git
git add .

# Commit your changes
git commit -m "Complete overhaul of AudioTranscripY with ML integration"

# Push to GitHub
git push origin main  # or 'master' depending on your branch name

Alternatively, if this is a new repository:

# Initialize a new repository
git init

# Add all files
git add .

# Commit your changes
git commit -m "Initial commit of AudioTranscripY with ML integration"

# Add your GitHub repository as remote
git remote add origin https://github.com/katgharalad/audiotrancriptionfire.git

# Push to GitHub
git push -u origin main  # or 'master' depending on your branch name
""")

def confirm_with_user():
    """Confirm with the user before proceeding"""
    print("\nWARNING: This script will permanently delete files and directories.")
    print("Make sure you have a backup if needed.")
    confirmation = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    
    if confirmation != "yes":
        print("Operation cancelled by user.")
        sys.exit(0)

def main():
    """Main function to finalize preparation for GitHub upload"""
    print_step("FINALIZING PREPARATION FOR GITHUB UPLOAD")
    
    # Confirm with user
    confirm_with_user()
    
    try:
        # Clean up directories
        cleanup_directories()
        
        # Clean up files
        cleanup_files()
        
        # Print git instructions
        print_git_instructions()
        
        print_step("PREPARATION FINALIZED")
        print("Your files are now ready for GitHub upload.")
        print("After running this script, you can delete it with: rm finalize_upload.py")
        
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 