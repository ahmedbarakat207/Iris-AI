import torch

def check_pytorch_device():
    print(f"PyTorch Version: {torch.__version__}")
    
    
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    
    if cuda_available:
        
        device_count = torch.cuda.device_count()
        print(f"Number of GPUs detected: {device_count}")
        
        
        current_device = torch.cuda.current_device()
        gpu_name = torch.cuda.get_device_name(current_device)
        print(f"Current GPU Device ID: {current_device}")
        print(f"GPU Model: {gpu_name}")
        
        
        device = torch.device("cuda")
    else:
        print("CUDA is not available. PyTorch will run on the CPU.")
        
        device = torch.device("cpu")
        
    print(f"\nTarget device for tensors/models: {device}")

if __name__ == "__main__":
    check_pytorch_device()
