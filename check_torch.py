import sys
import os

try:
    import torch
    import torch_geometric
    print("PyTorch and PyTorch Geometric are available.")
except ImportError as e:
    print(f"Import error: {e}")
    print("PyTorch Geometric is not installed.")
