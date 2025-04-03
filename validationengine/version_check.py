#!/usr/bin/env python3
import os
import json
import sys
import shutil

def check_validation_engine_versions():
    """
    Check for redundant validation engine files and ensure latest version is used.
    """
    print("\n" + "="*70)
    print("VALIDATION ENGINE VERSION CHECK".center(70))
    print("="*70 + "\n")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check for different versions
    validation_engine_path = os.path.join(script_dir, "validation_engine.py")
    validation_engine_v2_path = os.path.join(script_dir, "validation_engine_v2.py")
    
    if os.path.exists(validation_engine_path) and os.path.exists(validation_engine_v2_path):
        print("Multiple versions of validation engine detected:")
        print(f"1. validation_engine.py ({os.path.getsize(validation_engine_path) / 1024:.1f} KB)")
        print(f"2. validation_engine_v2.py ({os.path.getsize(validation_engine_v2_path) / 1024:.1f} KB)")
        
        # Check if __init__.py imports v2
        init_file = os.path.join(script_dir, "__init__.py")
        if os.path.exists(init_file):
            with open(init_file, "r") as f:
                init_content = f.read()
                
            if "validation_engine_v2" in init_content:
                print("\nThe __init__.py file is configured to use validation_engine_v2.py")
                print("This is the recommended configuration.")
            else:
                print("\nThe __init__.py file is NOT configured to use validation_engine_v2.py")
                print("Updating __init__.py to use the latest version...")
                
                with open(init_file, "w") as f:
                    f.write("""# Delaware County Address Validation Engine Module
# Provides address validation, landmark resolution, and jurisdiction assignment

from .validation_engine_v2 import AddressValidationEngine

__all__ = ['AddressValidationEngine']
""")
                print("__init__.py updated to use validation_engine_v2.py")
        
        # Ask if user wants to clean up redundant files
        user_choice = input("\nDo you want to create a backup of validation_engine.py and use only v2? (y/n): ").lower()
        
        if user_choice == 'y':
            # Create backup directory if it doesn't exist
            backup_dir = os.path.join(script_dir, "backup")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Create backup of original file
            backup_path = os.path.join(backup_dir, "validation_engine_backup.py")
            shutil.copy2(validation_engine_path, backup_path)
            
            # Remove the original file
            os.remove(validation_engine_path)
            
            print(f"\nBackup created at: {backup_path}")
            print(f"Removed redundant file: {validation_engine_path}")
            print("The system is now configured to use only validation_engine_v2.py")
        else:
            print("\nNo changes made. Both versions will be kept.")
            print("Note: The system will use the version specified in __init__.py")
    elif os.path.exists(validation_engine_v2_path):
        print("Only validation_engine_v2.py found. This is the recommended configuration.")
        
        # Check if __init__.py imports v2
        init_file = os.path.join(script_dir, "__init__.py")
        if os.path.exists(init_file):
            with open(init_file, "r") as f:
                init_content = f.read()
                
            if "validation_engine_v2" in init_content:
                print("The __init__.py file is correctly configured.")
            else:
                print("Updating __init__.py to use the latest version...")
                
                with open(init_file, "w") as f:
                    f.write("""# Delaware County Address Validation Engine Module
# Provides address validation, landmark resolution, and jurisdiction assignment

from .validation_engine_v2 import AddressValidationEngine

__all__ = ['AddressValidationEngine']
""")
                print("__init__.py updated to use validation_engine_v2.py")
    elif os.path.exists(validation_engine_path):
        print("Only validation_engine.py found. This is an older version.")
        print("It is recommended to use validation_engine_v2.py for better results.")
        
        # Ask if user wants to rename the file
        user_choice = input("\nDo you want to create a copy as validation_engine_v2.py? (y/n): ").lower()
        
        if user_choice == 'y':
            # Copy the file as v2
            shutil.copy2(validation_engine_path, validation_engine_v2_path)
            
            # Update __init__.py
            init_file = os.path.join(script_dir, "__init__.py")
            with open(init_file, "w") as f:
                f.write("""# Delaware County Address Validation Engine Module
# Provides address validation, landmark resolution, and jurisdiction assignment

from .validation_engine_v2 import AddressValidationEngine

__all__ = ['AddressValidationEngine']
""")
            
            print(f"\nCopied to: {validation_engine_v2_path}")
            print("__init__.py updated to use validation_engine_v2.py")
        else:
            print("\nNo changes made.")
    else:
        print("No validation engine file found!")
        print("This is an issue and needs to be resolved.")
        return False
    
    return True

if __name__ == "__main__":
    if check_validation_engine_versions():
        print("\nVersion check completed.")
    else:
        print("\nVersion check failed.")
        sys.exit(1) 