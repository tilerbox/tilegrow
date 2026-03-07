"""
Spiralmaker - Алгоритм спирали Улама для размещения тайлов.

Спираль Улама строится по следующему правилу:
- Начинаем в точке (0, 0)
- Идем вправо, потом вверх, влево, вниз и т.д.
- На каждом круге количество шагов увеличивается
"""

from typing import Iterator, Tuple


def ulam_spiral() -> Iterator[Tuple[int, int]]:
    """
    Генератор координат спирали Улама.
    
    Yields:
        Tuple[int, int]: Координаты (x, y) для каждой позиции в спирали
    
    Example:
        >>> spiral = ulam_spiral()
        >>> [next(spiral) for _ in range(5)]
        [(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1)]
    """
    x, y = 0, 0
    yield (x, y)
    
    layer = 1
    while True:
        # Право (1 шаг вправо)
        x += 1
        yield (x, y)
        
        # Вверх (layer шагов)
        for _ in range(layer):
            y += 1
            yield (x, y)
        
        # Влево (layer * 2 шагов)
        for _ in range(layer * 2):
            x -= 1
            yield (x, y)
        
        # Вниз (layer * 2 шагов)
        for _ in range(layer * 2):
            y -= 1
            yield (x, y)
        
        # Вправо (layer шагов)
        for _ in range(layer):
            x += 1
            yield (x, y)
        
        layer += 1


def get_spiral_positions(count: int) -> list[Tuple[int, int]]:
    """
    Получить первые N позиций спирали Улама.
    
    Args:
        count: Количество позиций
    
    Returns:
        list[Tuple[int, int]]: Список координат (x, y)
    """
    spiral = ulam_spiral()
    return [next(spiral) for _ in range(count)]


def spiral_to_grid(positions: list[Tuple[int, int]]) -> Tuple[list[list[int]], int, int]:
    """
    Преобразовать координаты спирали в сетку с отсчетом от 0.
    
    Args:
        positions: Список координат (x, y)
    
    Returns:
        Tuple[list[list[int]], int, int]: 
            - сетка с индексами позиций
            - смещение по X
            - смещение по Y
    """
    if not positions:
        return [], 0, 0
    
    min_x = min(p[0] for p in positions)
    max_x = max(p[0] for p in positions)
    min_y = min(p[1] for p in positions)
    max_y = max(p[1] for p in positions)
    
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    
    # Создаем сетку с -1 (пустые клетки)
    grid = [[-1 for _ in range(width)] for _ in range(height)]
    
    # Заполняем индексами позиций
    for idx, (x, y) in enumerate(positions):
        grid_y = y - min_y
        grid_x = x - min_x
        grid[grid_y][grid_x] = idx
    
    return grid, min_x, min_y


def get_spiral_bounds(positions: list[Tuple[int, int]]) -> Tuple[int, int, int, int]:
    """
    Получить границы спирали.
    
    Args:
        positions: Список координат (x, y)
    
    Returns:
        Tuple[int, int, int, int]: (min_x, max_x, min_y, max_y)
    """
    if not positions:
        return 0, 0, 0, 0
    
    min_x = min(p[0] for p in positions)
    max_x = max(p[0] for p in positions)
    min_y = min(p[1] for p in positions)
    max_y = max(p[1] for p in positions)
    
    return min_x, max_x, min_y, max_y


if __name__ == "__main__":
    # Тестирование
    positions = get_spiral_positions(25)
    print("First 25 positions:")
    for i, pos in enumerate(positions):
        print(f"{i}: {pos}")
    
    print("\nGrid representation:")
    grid, offset_x, offset_y = spiral_to_grid(positions)
    for row in reversed(grid):  # Переворачиваем для визуализации
        print(' '.join(f'{cell:2d}' if cell >= 0 else ' .' for cell in row))
