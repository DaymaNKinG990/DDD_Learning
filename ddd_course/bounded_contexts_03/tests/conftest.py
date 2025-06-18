"""
Конфигурация тестов для pytest.
Добавляет корневую директорию проекта в PYTHONPATH.
"""
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
root_dir = str(Path(__file__).parent.parent / "booking_platform_solution" / "src")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
