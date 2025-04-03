#!/usr/bin/env python3
import os
import sys
import shutil

def cleanup_project():
    """
    Clean up redundant files from the AudioTranscripY + Validation Engine project.
    """
    print("\n" + "="*70)
    print("AUDIOTRANSCRIPY PROJECT CLEANUP".center(70))
    print("="*70 + "\n")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Files to delete
    redundant_files = [
        # Integration files
        "integrated_demo.py",
        "setup_validation_integration.py",
        "connected_system.py",
        "integration_setup.py",
        "run_integration.sh",
        
        # Test files
        "test_with_transcripts.py",
        "test_enhanced_features.py", 
        "test_detailed_metrics.py",
        
        # Temporary files
        "addedfeatures.txt",
        "i.txt",
        ".DS_Store",
    ]
    
    # Files in validation engine
    validation_files = [
        "test_v2.py",
        "test_multiple.py",
        "test_address.py",
        "i.txt",
    ]
    
    # Directories to delete
    redundant_dirs = [
        "integration",
        "demo_outputs",
        "test_outputs",
        "interpretations",
    ]
    
    # Keep track of deletions
    deleted_files = []
    deleted_dirs = []
    skipped_files = []
    skipped_dirs = []
    
    # Ask for confirmation before proceeding
    print("This script will delete the following redundant files and directories:")
    
    print("\nFiles:")
    for file in redundant_files:
        print(f"  - {file}")
    
    print("\nFiles in validationengine/:")
    for file in validation_files:
        print(f"  - validationengine/{file}")
    
    print("\nDirectories:")
    for dir in redundant_dirs:
        print(f"  - {dir}/")
    
    confirm = input("\nProceed with cleanup? (y/n): ")
    if not confirm.lower().startswith('y'):
        print("Cleanup cancelled.")
        return
    
    # Delete redundant files
    print("\nDeleting redundant files...")
    for file in redundant_files:
        file_path = os.path.join(script_dir, file)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_files.append(file)
                print(f"  ✓ Deleted {file}")
            except Exception as e:
                print(f"  ✗ Failed to delete {file}: {e}")
                skipped_files.append(file)
        else:
            skipped_files.append(file)
    
    # Delete validation engine files
    validation_dir = os.path.join(script_dir, "validationengine")
    for file in validation_files:
        file_path = os.path.join(validation_dir, file)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_files.append(f"validationengine/{file}")
                print(f"  ✓ Deleted validationengine/{file}")
            except Exception as e:
                print(f"  ✗ Failed to delete validationengine/{file}: {e}")
                skipped_files.append(f"validationengine/{file}")
        else:
            skipped_files.append(f"validationengine/{file}")
    
    # Ask about validation_engine.py
    validation_engine_old = os.path.join(validation_dir, "validation_engine.py")
    validation_engine_new = os.path.join(validation_dir, "validation_engine_v2.py")
    
    if os.path.exists(validation_engine_old) and os.path.exists(validation_engine_new):
        print("\nBoth validation_engine.py and validation_engine_v2.py exist.")
        confirm = input("Delete the older validation_engine.py? (y/n): ")
        if confirm.lower().startswith('y'):
            try:
                os.remove(validation_engine_old)
                deleted_files.append("validationengine/validation_engine.py")
                print(f"  ✓ Deleted validationengine/validation_engine.py")
            except Exception as e:
                print(f"  ✗ Failed to delete validationengine/validation_engine.py: {e}")
                skipped_files.append("validationengine/validation_engine.py")
    
    # Delete redundant directories
    print("\nDeleting redundant directories...")
    for dir in redundant_dirs:
        dir_path = os.path.join(script_dir, dir)
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                deleted_dirs.append(dir)
                print(f"  ✓ Deleted {dir}/")
            except Exception as e:
                print(f"  ✗ Failed to delete {dir}/: {e}")
                skipped_dirs.append(dir)
        else:
            skipped_dirs.append(dir)
    
    # Summary
    print("\n" + "="*70)
    print("CLEANUP SUMMARY".center(70))
    print("="*70)
    
    print(f"\nDeleted {len(deleted_files)} files:")
    for file in deleted_files:
        print(f"  - {file}")
    
    print(f"\nDeleted {len(deleted_dirs)} directories:")
    for dir in deleted_dirs:
        print(f"  - {dir}/")
    
    print(f"\nSkipped {len(skipped_files)} files (not found or error):")
    for file in skipped_files:
        print(f"  - {file}")
    
    print(f"\nSkipped {len(skipped_dirs)} directories (not found or error):")
    for dir in skipped_dirs:
        print(f"  - {dir}/")
    
    print("\nCleanup complete!")
    
    # Remind about requirements
    print("\nDon't forget to ensure you have all required dependencies installed:")
    print("pip install fuzzywuzzy python-Levenshtein pandas numpy scikit-learn\n")

if __name__ == "__main__":
    try:
        cleanup_project()
    except KeyboardInterrupt:
        print("\nCleanup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during cleanup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 