"""
YOLO Installation Fix Script
Fixes common YOLO installation issues
"""

import os
import sys
import subprocess

print("="*60)
print("YOLO Installation Fix Script")
print("="*60)
print()

def run_command(cmd):
    """Run command and show output"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(" Success")
        if result.stdout:
            print(result.stdout)
    else:
        print(" Failed")
        if result.stderr:
            print(result.stderr)
    print()
    return result.returncode == 0

print("🔧 Fixing YOLO installation...\n")

# Method 1: Install ultralytics (recommended)
print("Method 1: Installing ultralytics package...")
success1 = run_command("pip install ultralytics")

# Method 2: Install YOLOv5 requirements
print("Method 2: Installing YOLOv5 requirements...")
success2 = run_command("pip install yolov5")

# Method 3: Clone and install from source (if above fails)
if not (success1 or success2):
    print("Method 3: Installing from GitHub...")
    run_command("pip install gitpython")
    
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    print(f"Cloning to: {temp_dir}")
    
    os.chdir(temp_dir)
    if run_command("git clone https://github.com/ultralytics/yolov5"):
        os.chdir("yolov5")
        run_command("pip install -r requirements.txt")
    
    # Clean up
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    shutil.rmtree(temp_dir, ignore_errors=True)

# Test import
print("="*60)
print("Testing YOLO import...")
print("="*60)

try:
    import torch
    print(" PyTorch installed")
    print(f"   Version: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
except ImportError:
    print(" PyTorch not installed!")
    print("   Run: pip install torch torchvision")

try:
    print("\nTrying to load YOLOv5 model...")
    import torch
    
    # Test with minimal options
    model = torch.hub.load('ultralytics/yolov5', 'yolov5n',  # yolov5n is smallest
                          pretrained=True,
                          device='cpu',
                          trust_repo=True,
                          verbose=False)
    print(" YOLOv5 model loaded successfully!")
    print(f"   Model type: {type(model)}")
    
except Exception as e:
    print(" YOLOv5 load failed!")
    print(f"   Error: {e}")
    print("\n📝 Manual fix steps:")
    print("   1. pip uninstall torch torchvision yolov5 ultralytics")
    print("   2. pip install torch torchvision")
    print("   3. pip install ultralytics")
    print("   4. Run this script again")

print("\n" + "="*60)
print("Fix script completed!")
print("="*60)
print("\nNext steps:")
print("1. If YOLOv5 loaded successfully, you're good to go!")
print("2. If still failing, run: pip install --upgrade ultralytics")
print("3. Then test with: python test_components.py")
print()