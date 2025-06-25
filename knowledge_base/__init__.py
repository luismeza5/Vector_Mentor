"""VectorMentor - Base de conocimientos de álgebra lineal"""

try:
    from .data_loader import DataLoader
except ImportError:
    DataLoader = None

__all__ = ['DataLoader']