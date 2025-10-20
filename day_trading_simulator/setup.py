"""
Setup script for the Day Trading Simulator
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages with better error handling"""
    print("Installing required packages...")
    
    # List of packages to install individually
    packages = [
        "yfinance>=0.2.18",
        "pandas>=1.5.0", 
        "numpy>=1.21.0",
        "openpyxl>=3.0.0",
        "requests>=2.25.0",
        "schedule>=1.1.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0"
    ]
    
    failed_packages = []
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package, "--upgrade", "--user"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✓ {package}")
        except subprocess.CalledProcessError:
            print(f"✗ {package} - trying alternative installation...")
            try:
                # Try without --user flag
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package, "--upgrade"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✓ {package} (alternative method)")
            except subprocess.CalledProcessError:
                print(f"✗ {package} - failed to install")
                failed_packages.append(package)
    
    if failed_packages:
        print(f"\nFailed to install: {', '.join(failed_packages)}")
        print("You may need to install these manually or use conda instead of pip.")
        return False
    
    print("\n✓ All packages installed successfully!")
    return True

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    directories = ["data", "logs"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory already exists: {directory}")

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    required_modules = [
        "yfinance",
        "pandas", 
        "numpy",
        "openpyxl",
        "ta",
        "requests",
        "schedule"
    ]
    
    failed_imports = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\nFailed to import: {', '.join(failed_imports)}")
        return False
    
    print("✓ All imports successful!")
    return True

def main():
    """Main setup function"""
    print("Day Trading Simulator Setup")
    print("=" * 40)
    print()
    
    # Create directories
    create_directories()
    print()
    
    # Install requirements
    if not install_requirements():
        print("\nSetup failed. Please check the error messages above.")
        return False
    print()
    
    # Test imports
    if not test_imports():
        print("\nSetup failed. Some packages could not be imported.")
        return False
    print()
    
    print("=" * 40)
    print("✓ Setup completed successfully!")
    print()
    print("You can now run the simulator with:")
    print("  python main_simulator.py")
    print("  or")
    print("  python run_simulator.py")
    print()
    print("For more information, see README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
