"""pytest configuration: ensure project root is on sys.path."""
import sys
import os

# Insert project root so `qseries` package is importable without installing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
