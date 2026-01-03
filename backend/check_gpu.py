"""Check CUDA/GPU availability"""
import torch

print("="*60)
print("GPU/CUDA Check")
print("="*60)

print(f"\nPyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU device: {torch.cuda.get_device_name(0)}")
    print(f"GPU count: {torch.cuda.device_count()}")
    print(f"\n✅ Training will use GPU (FAST!)")
else:
    print(f"\n⚠️  CUDA not available")
    print(f"Training will use CPU (SLOW)")
    print(f"\nTo enable GPU:")
    print(f"1. Install NVIDIA GPU drivers")
    print(f"2. Install CUDA Toolkit")
    print(f"3. Install PyTorch with CUDA:")
    print(f"   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")

print("="*60)
