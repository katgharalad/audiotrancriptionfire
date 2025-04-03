#!/usr/bin/env python3
import os
import subprocess
import sys
import platform

def setup_validation_engine_venv():
    """
    Sets up a virtual environment for the validation engine with all required dependencies.
    """
    print("\n" + "="*70)
    print("VALIDATION ENGINE VIRTUAL ENVIRONMENT SETUP".center(70))
    print("="*70 + "\n")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define venv path
    venv_dir = os.path.join(script_dir, "venv")
    
    # Check if venv already exists
    if os.path.exists(venv_dir):
        print(f"Virtual environment already exists at: {venv_dir}")
        overwrite = input("Do you want to remove it and create a new one? (y/n): ").lower()
        if overwrite == 'y':
            try:
                import shutil
                shutil.rmtree(venv_dir)
                print("Existing virtual environment removed.")
            except Exception as e:
                print(f"Error removing existing venv: {e}")
                return False
        else:
            print("Using existing virtual environment.")
            return True
    
    print(f"Creating virtual environment at: {venv_dir}")
    
    # Create venv
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment: {e}")
        return False
    
    # Determine the pip path based on OS
    if platform.system() == "Windows":
        pip_path = os.path.join(venv_dir, "Scripts", "pip")
    else:
        pip_path = os.path.join(venv_dir, "bin", "pip")
    
    # Upgrade pip
    try:
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error upgrading pip: {e}")
        return False
    
    # Install requirements
    requirements_path = os.path.join(script_dir, "requirements.txt")
    if not os.path.exists(requirements_path):
        print(f"Warning: requirements.txt not found at {requirements_path}")
        print("Creating basic requirements.txt file...")
        with open(requirements_path, "w") as f:
            f.write("pandas\nnumpy\nfuzzywuzzy\npython-Levenshtein\npathlib\n")
    
    print(f"Installing requirements from: {requirements_path}")
    try:
        subprocess.run([pip_path, "install", "-r", requirements_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False
    
    # Print activation instructions
    print("\n" + "="*70)
    print("VIRTUAL ENVIRONMENT SETUP COMPLETE".center(70))
    print("="*70 + "\n")
    
    print("To activate the virtual environment:")
    if platform.system() == "Windows":
        print(f"    {venv_dir}\\Scripts\\activate")
    else:
        print(f"    source {venv_dir}/bin/activate")
    
    print("\nTo use the validation engine with the virtual environment:")
    print("1. Activate the virtual environment")
    print("2. Run: python validation_engine_v2.py")
    
    return True

if __name__ == "__main__":
    if setup_validation_engine_venv():
        print("\nSetup completed successfully!")
    else:
        print("\nSetup failed. Please check the errors above.")
        sys.exit(1) 