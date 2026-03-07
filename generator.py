#!/usr/bin/env python3
"""
generator.py - Генератор тайлов из username.

Каждый подписчик = уникальный тайл 200x200px.
Имя определяет: биом, цвет, декорации.
"""

import hashlib
import os
from PIL import Image, ImageDraw
from typing import Tuple

# Биомы и их базовые цвета (HSL)
BIOMES = {
    'ocean': {'hue_range': (180, 220), 'decor': 'waves'},
    'forest': {'hue_range': (100, 140), 'decor': 'trees'},
    'mountain': {'hue_range': (0, 40), 'decor': 'peaks'},
    'desert': {'hue_range': (40, 60), 'decor': 'cacti'},
    'plains': {'hue_range': (60, 100), 'decor': 'flowers'},
    'snow': {'hue_range': (200, 260), 'decor': 'flakes'}
}

TILE_SIZE = 200
TILES_DIR = 'tiles'


def ensure_tiles_dir():
    """Создать папку для тайлов если не существует."""
    os.makedirs(TILES_DIR, exist_ok=True)


def username_to_hash(username: str) -> int:
    """Преобразовать username в числовой хеш."""
    return int(hashlib.md5(username.encode()).hexdigest(), 16)


def hash_to_biome(hash_val: int) -> str:
    """Определить биом из хеша."""
    biomes = list(BIOMES.keys())
    return biomes[hash_val % len(biomes)]


def hash_to_color(hash_val: int, username: str) -> Tuple[int, int, int]:
    """
    Сгенерировать цвет из хеша username.
    Hue из первых 2 букв, saturation из длины имени.
    """
    # Hue: первые 2 буквы → 0-360
    first_chars = username[:2].lower()
    hue_base = (ord(first_chars[0]) + ord(first_chars[1])) % 360 if len(first_chars) == 2 else hash_val % 360
    
    # Saturation: длина имени → 40-80%
    sat = 40 + (len(username) % 40)
    
    # Lightness: фиксировано 50%
    light = 50
    
    return hsl_to_rgb(hue_base, sat, light)


def hsl_to_rgb(h: int, s: int, l: int) -> Tuple[int, int, int]:
    """Конвертировать HSL в RGB."""
    s /= 100
    l /= 100
    
    def hue_to_rgb(p, q, t):
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
        return p
    
    if s == 0:
        r = g = b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h/360 + 1/3)
        g = hue_to_rgb(p, q, h/360)
        b = hue_to_rgb(p, q, h/360 - 1/3)
    
    return (int(r * 255), int(g * 255), int(b * 255))


def draw_decorations(draw: ImageDraw.Draw, biome: str, color: Tuple[int, int, int], hash_val: int):
    """Нарисовать декорации для биома."""
    base_color = color
    dark_color = tuple(int(c * 0.7) for c in base_color)
    light_color = tuple(min(255, int(c * 1.3)) for c in base_color)
    
    if biome == 'forest':
        # Деревья (треугольники)
        for i in range(3 + (hash_val % 3)):
            x = 30 + (i * 50) + (hash_val % 20)
            y = 80 + (hash_val % 30)
            size = 30 + (hash_val % 15)
            draw.polygon([(x, y), (x - size//2, y + size), (x + size//2, y + size)], 
                        fill=dark_color)
            draw.rectangle([x - 3, y + size, x + 3, y + size + 20], fill=dark_color)
    
    elif biome == 'mountain':
        # Горы (треугольники снизу)
        for i in range(2 + (hash_val % 2)):
            x = 50 + (i * 80) + (hash_val % 30)
            size = 60 + (hash_val % 30)
            points = [(x, 50), (x - size//2, 180), (x + size//2, 180)]
            draw.polygon(points, fill=light_color)
            # Снежная шапка
            draw.polygon([(x, 50), (x - 15, 100), (x + 15, 100)], fill=(255, 255, 255))
    
    elif biome == 'ocean':
        # Волны (кривые линии)
        for i in range(4):
            y = 50 + (i * 35)
            for x in range(10, 190, 20):
                offset = (hash_val + i + x) % 10
                draw.arc([x, y + offset, x + 20, y + offset + 15], 0, 180, 
                        fill=light_color, width=3)
    
    elif biome == 'desert':
        # Кактусы
        for i in range(2 + (hash_val % 2)):
            x = 60 + (i * 70) + (hash_val % 20)
            y = 100
            # Ствол
            draw.ellipse([x - 10, y, x + 10, y + 60], fill=dark_color)
            # Руки
            draw.ellipse([x - 25, y + 20, x - 5, y + 35], fill=dark_color)
            draw.ellipse([x + 5, y + 25, x + 25, y + 40], fill=dark_color)
    
    elif biome == 'plains':
        # Цветы/трава (маленькие кружки)
        for i in range(10 + (hash_val % 10)):
            x = 20 + ((i * 17 + hash_val) % 160)
            y = 100 + ((i * 23 + hash_val) % 60)
            size = 4 + (hash_val % 6)
            flower_color = light_color if i % 2 == 0 else (255, 255, 200)
            draw.ellipse([x - size, y - size, x + size, y + size], fill=flower_color)
    
    elif biome == 'snow':
        # Снежинки
        for i in range(8 + (hash_val % 5)):
            cx = 30 + ((i * 21 + hash_val) % 140)
            cy = 40 + ((i * 19 + hash_val) % 100)
            size = 8 + (hash_val % 6)
            # Крестообразная снежинка
            draw.line([(cx - size, cy), (cx + size, cy)], fill=(255, 255, 255), width=2)
            draw.line([(cx, cy - size), (cx, cy + size)], fill=(255, 255, 255), width=2)
            draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 255, 255))


def generate_tile(username: str, size: int = TILE_SIZE) -> Image.Image:
    """
    Сгенерировать тайл из username.
    
    Args:
        username: Имя подписчика
        size: Размер тайла (default 200)
    
    Returns:
        PIL.Image: Тайл с уникальным дизайном
    """
    hash_val = username_to_hash(username)
    biome = hash_to_biome(hash_val)
    color = hash_to_color(hash_val, username)
    
    # Создать изображение
    img = Image.new('RGB', (size, size), color)
    draw = ImageDraw.Draw(img)
    
    # Градиент/текстура
    for y in range(size):
        for x in range(size):
            noise = (hash_val + x * y) % 20 - 10
            if noise > 5:
                current = img.getpixel((x, y))
                new_color = tuple(min(255, max(0, c + noise)) for c in current)
                img.putpixel((x, y), new_color)
    
    # Декорации
    draw = ImageDraw.Draw(img)
    draw_decorations(draw, biome, color, hash_val)
    
    return img


def save_tile(username: str, force: bool = False) -> str:
    """
    Сохранить тайл в файл.
    
    Args:
        username: Имя подписчика
        force: Пересоздать если файл существует
    
    Returns:
        str: Путь к файлу тайла
    """
    ensure_tiles_dir()
    
    filepath = os.path.join(TILES_DIR, f"{username}.png")
    
    if os.path.exists(filepath) and not force:
        return filepath
    
    tile = generate_tile(username)
    tile.save(filepath, 'PNG')
    
    return filepath


def generate_tiles(usernames: list) -> list:
    """
    Сгенерировать тайлы для списка username.
    
    Args:
        usernames: Список имён
    
    Returns:
        list: Пути к созданным файлам
    """
    paths = []
    for username in usernames:
        path = save_tile(username)
        paths.append(path)
        print(f"✓ Тайл создан: {username}")
    
    return paths


if __name__ == '__main__':
    # Тестирование
    test_names = ['alex', 'maria', 'john', 'anna', 'test_user_123']
    for name in test_names:
        save_tile(name)
        print(f"Создан тайл для: {name}")
