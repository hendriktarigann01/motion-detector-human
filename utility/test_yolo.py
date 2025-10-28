"""
Simple YOLO Test Script
Quick test to verify YOLO installation
"""
import sys
import torch
from pathlib import Path

print("="*60)
print("YOLO Installation Test")
print("="*60)
print()

# Test 1: PyTorch
print("Test 1: Checking PyTorch...")
try:
    print(f"✅ PyTorch installed: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   CUDA version: {torch.version.cuda}")
        print(f"   GPU device: {torch.cuda.get_device_name(0)}")
    print()
except ImportError as e:
    print(f"❌ PyTorch not installed!")
    print(f"   Error: {e}")
    print(f"   Fix: pip install torch torchvision")
    sys.exit(1)

# Test 2: Ultralytics
print("Test 2: Checking Ultralytics...")
try:
    from ultralytics import YOLO
    import ultralytics
    print(f"✅ Ultralytics installed: {ultralytics.__version__}")
    print()
    use_ultralytics = True
except ImportError:
    print(f"⚠️  Ultralytics not installed")
    print(f"   Will use torch.hub method instead")
    print(f"   To install: pip install ultralytics")
    print()
    use_ultralytics = False

# Test 3: Load YOLOv5 model
print("Test 3: Loading YOLOv5 model...")
print("   (This may take a while on first run - downloading ~30MB)")
print()

try:
    # Try loading smallest model (yolov5n)
    print("   Loading yolov5n (smallest, fastest)...")
    model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)
    print("   ✅ Model loaded successfully!")
    print()
    
    # Test 4: Model info
    print("Test 4: Model Information...")
    print(f"   Model type: YOLOv5n")
    print(f"   Number of classes: {len(model.names)}")
    print(f"   Classes: {list(model.names.values())[:10]}... (showing first 10)")
    print()
    
    # Test 5: Simple inference test
    print("Test 5: Running inference test...")
    print("   Creating test image (640x640 random pixels)...")
    
    # Create a random test image
    import numpy as np
    test_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    print("   Running inference...")
    results = model(test_img)
    print("   ✅ Inference successful!")
    print(f"   Detections: {len(results.xyxy[0])} objects detected")
    print()
    
    # Test 6: Check available models
    print("Test 6: Available YOLOv5 models...")
    available_models = ['yolov5n', 'yolov5s', 'yolov5m', 'yolov5l', 'yolov5x']
    print("   Models you can use:")
    for m in available_models:
        print(f"     - {m}")
    print()
    
    # Summary
    print("="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print()
    print("Your YOLO installation is working correctly!")
    print()
    print("Next steps:")
    print("  1. Load a model: model = torch.hub.load('ultralytics/yolov5', 'yolov5n')")
    print("  2. Run inference: results = model('image.jpg')")
    print("  3. View results: results.show() or results.print()")
    print()
    
    if not use_ultralytics:
        print("💡 Tip: Install ultralytics for more features:")
        print("   pip install ultralytics")
        print()

except Exception as e:
    print(f"❌ Error during model loading/testing!")
    print(f"   Error: {e}")
    print()
    print("Troubleshooting:")
    print("  1. Check internet connection (model needs to download)")
    print("  2. Try: pip install --upgrade torch torchvision")
    print("  3. Try: pip install ultralytics")
    print("  4. Clear cache: rm -rf ~/.cache/torch/hub")
    sys.exit(1)

print("="*60)
print("Test completed successfully! 🎉")
print("="*60)