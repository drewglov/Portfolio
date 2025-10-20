"""
Alternative package installer with multiple options
"""

import subprocess
import sys
import os

def install_with_pip():
    """Install packages using pip"""
    print("Installing packages with pip...")
    packages = [
        "yfinance",
        "pandas", 
        "numpy",
        "openpyxl",
        "requests",
        "schedule",
        "matplotlib",
        "seaborn"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package}")
        except subprocess.CalledProcessError:
            print(f"✗ {package}")

def install_with_conda():
    """Install packages using conda"""
    print("Installing packages with conda...")
    packages = [
        "pandas",
        "numpy", 
        "matplotlib",
        "seaborn"
    ]
    
    # Install with conda first
    for package in packages:
        try:
            print(f"Installing {package} with conda...")
            subprocess.check_call(["conda", "install", "-y", package])
            print(f"✓ {package}")
        except subprocess.CalledProcessError:
            print(f"✗ {package}")
    
    # Install remaining with pip
    pip_packages = ["yfinance", "openpyxl", "requests", "schedule"]
    for package in pip_packages:
        try:
            print(f"Installing {package} with pip...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package}")
        except subprocess.CalledProcessError:
            print(f"✗ {package}")

def manual_install_instructions():
    """Provide manual installation instructions"""
    print("\n" + "="*60)
    print("MANUAL INSTALLATION INSTRUCTIONS")
    print("="*60)
    print()
    print("If automatic installation failed, try these steps:")
    print()
    print("1. UPDATE PIP FIRST:")
    print("   python -m pip install --upgrade pip")
    print()
    print("2. INSTALL PACKAGES ONE BY ONE:")
    print("   pip install yfinance")
    print("   pip install pandas")
    print("   pip install numpy") 
    print("   pip install openpyxl")
    print("   pip install requests")
    print("   pip install schedule")
    print("   pip install matplotlib")
    print("   pip install seaborn")
    print()
    print("3. IF YOU HAVE CONDA:")
    print("   conda install pandas numpy matplotlib seaborn")
    print("   pip install yfinance openpyxl requests schedule")
    print()
    print("4. IF STILL FAILING, TRY:")
    print("   pip install --user yfinance pandas numpy openpyxl requests schedule matplotlib seaborn")
    print()
    print("5. FOR WINDOWS USERS:")
    print("   Download pre-compiled wheels from:")
    print("   https://www.lfd.uci.edu/~gohlke/pythonlibs/")
    print()

def check_installations():
    """Check if packages are installed"""
    print("Checking installations...")
    packages = {
        "yfinance": "yfinance",
        "pandas": "pandas", 
        "numpy": "numpy",
        "openpyxl": "openpyxl",
        "requests": "requests",
        "schedule": "schedule",
        "matplotlib": "matplotlib",
        "seaborn": "seaborn"
    }
    
    installed = []
    missing = []
    
    for display_name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✓ {display_name}")
            installed.append(display_name)
        except ImportError:
            print(f"✗ {display_name}")
            missing.append(display_name)
    
    return installed, missing

def main():
    print("Day Trading Simulator - Package Installer")
    print("="*50)
    print()
    
    # Check what's already installed
    installed, missing = check_installations()
    
    if not missing:
        print("\n✓ All packages are already installed!")
        return
    
    print(f"\nMissing packages: {', '.join(missing)}")
    print()
    print("Choose installation method:")
    print("1. pip (recommended)")
    print("2. conda + pip (if you have conda)")
    print("3. Show manual instructions")
    print("4. Skip installation")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        install_with_pip()
    elif choice == "2":
        install_with_conda()
    elif choice == "3":
        manual_install_instructions()
        return
    elif choice == "4":
        print("Skipping installation.")
        return
    else:
        print("Invalid choice.")
        return
    
    # Check again
    print("\nChecking installations again...")
    installed, missing = check_installations()
    
    if missing:
        print(f"\nStill missing: {', '.join(missing)}")
        manual_install_instructions()
    else:
        print("\n✓ All packages installed successfully!")

if __name__ == "__main__":
    main()
