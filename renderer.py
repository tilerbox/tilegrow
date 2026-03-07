#!/usr/bin/env python3
"""
renderer.py - Рендер карты и видео.

Склеивает тайлы по спирали, создаёт видео с зум-аутом.
"""

import os
import subprocess
import tempfile
from PIL import Image
from typing import List, Tuple
from spiralmaker import get_spiral_positions, get_spiral_bounds
from generator import save_tile

TILE_SIZE = 200
OUTPUT_DIR = 'output'
FRAMES_DIR = 'frames'
TEMP_VIDEO_DURATION = 5  # секунд


def ensure_dirs():
    """Создать необходимые папки."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(FRAMES_DIR, exist_ok=True)


def render_map(usernames: List[str], tile_size: int = TILE_SIZE) -> Image.Image:
    """
    Склеить все тайлы в одну карту.
    
    Args:
        usernames: Список имён подписчиков
        tile_size: Размер одного тайла
    
    Returns:
        PIL.Image: Полная карта
    """
    ensure_dirs()
    
    # Получить позиции по спирали
    positions = get_spiral_positions(len(usernames))
    min_x, max_x, min_y, max_y = get_spiral_bounds(positions)
    
    # Размеры карты
    width = (max_x - min_x + 1) * tile_size
    height = (max_y - min_y + 1) * tile_size
    
    print(f"Размер карты: {width}x{height} ({len(usernames)} тайлов)")
    
    # Создать карту
    map_img = Image.new('RGB', (width, height), (30, 30, 40))
    
    # Разместить тайлы
    for idx, username in enumerate(usernames):
        x, y = positions[idx]
        # Инвертируем Y для правильной ориентации
        grid_y = height - (y - min_y + 1) * tile_size
        grid_x = (x - min_x) * tile_size
        
        # Получить или создать тайл
        tile_path = save_tile(username)
        tile = Image.open(tile_path)
        
        # Вставить тайл
        map_img.paste(tile, (grid_x, grid_y))
        
        if (idx + 1) % 10 == 0:
            print(f"  Размещено {idx + 1}/{len(usernames)} тайлов")
    
    return map_img


def create_zoom_frames(map_img: Image.Image, usernames: List[str], 
                       duration: int = 15, fps: int = 30) -> List[str]:
    """
    Создать кадры для зум-анимации.
    
    Args:
        map_img: Полная карта
        usernames: Список имён (для пошаговой анимации)
        duration: Длительность видео
        fps: Кадров в секунду
    
    Returns:
        List[str]: Пути к кадрам
    """
    ensure_dirs()
    
    total_frames = duration * fps
    
    # Очистить старые кадры
    for f in os.listdir(FRAMES_DIR):
        os.remove(os.path.join(FRAMES_DIR, f))
    
    frame_paths = []
    
    # Целевой размер для Reels (1080x1920, но квадратная карта в центре)
    target_width = 1080
    target_height = 1920
    
    map_width, map_height = map_img.size
    
    print(f"Создание {total_frames} кадров...")
    
    for frame_idx in range(total_frames):
        progress = frame_idx / (total_frames - 1)  # 0.0 → 1.0
        
        # Зум: начинаем с близкого и отдаляемся
        # Начальный зум: 3x (крупный план центра)
        # Конечный зум: вся карта вписана в экран
        
        start_zoom = 3.0
        end_zoom = 1.0
        zoom = start_zoom - (start_zoom - end_zoom) * progress
        
        # Вычислить размер кропа
        crop_width = int(target_width / zoom)
        crop_height = int(target_height / zoom)
        
        # Центр карты
        center_x = map_width // 2
        center_y = map_height // 2
        
        # Координаты кропа
        left = max(0, center_x - crop_width // 2)
        top = max(0, center_y - crop_height // 2)
        right = min(map_width, left + crop_width)
        bottom = min(map_height, top + crop_height)
        
        # Корректировка если вышли за границы
        if right - left < crop_width:
            left = right - crop_width
        if bottom - top < crop_height:
            top = bottom - crop_height
        
        # Кроп и ресайз
        cropped = map_img.crop((left, top, right, bottom))
        resized = cropped.resize((target_width, target_height), Image.LANCZOS)
        
        # Добавить рамку/фон если карта не заполняет экран
        final = Image.new('RGB', (target_width, target_height), (20, 20, 30))
        
        # Центрировать
        paste_x = (target_width - resized.width) // 2
        paste_y = (target_height - resized.height) // 2
        final.paste(resized, (paste_x, paste_y))
        
        # Сохранить кадр
        frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx:05d}.png")
        final.save(frame_path, 'PNG')
        frame_paths.append(frame_path)
        
        if (frame_idx + 1) % 60 == 0 or frame_idx == 0:
            print(f"  Кадр {frame_idx + 1}/{total_frames}")
    
    return frame_paths


def render_video(usernames: List[str], output_path: str = None, 
                 duration: int = 15, fps: int = 30) -> str:
    """
    Создать видео с зум-анимацией карты.
    
    Args:
        usernames: Список имён подписчиков
        output_path: Путь для сохранения (default: output/map_video.mp4)
        duration: Длительность в секундах
        fps: Кадров в секунду
    
    Returns:
        str: Путь к созданному видео
    """
    ensure_dirs()
    
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, 'map_video.mp4')
    
    print("=" * 50)
    print("GENERATIVE MAP VIDEO RENDERER")
    print("=" * 50)
    
    # Шаг 1: Создать тайлы
    print(f"\n[1/4] Генерация {len(usernames)} тайлов...")
    for username in usernames:
        save_tile(username)
    
    # Шаг 2: Склеить карту
    print("\n[2/4] Создание карты...")
    map_img = render_map(usernames)
    map_path = os.path.join(OUTPUT_DIR, 'map_full.png')
    map_img.save(map_path)
    print(f"  Карта сохранена: {map_path}")
    
    # Шаг 3: Создать кадры
    print(f"\n[3/4] Рендер кадров ({duration}s @ {fps}fps)...")
    frame_paths = create_zoom_frames(map_img, usernames, duration, fps)
    
    # Шаг 4: Собрать видео через FFmpeg
    print(f"\n[4/4] Сборка видео...")
    
    # FFmpeg команда
    cmd = [
        'ffmpeg',
        '-y',  # Перезаписать если существует
        '-framerate', str(fps),
        '-i', os.path.join(FRAMES_DIR, 'frame_%05d.png'),
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-crf', '18',  # Качество (меньше = лучше)
        '-preset', 'medium',
        '-movflags', '+faststart',  # Для веб
        '-vf', 'format=yuv420p',  # Совместимость
        output_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"FFmpeg stderr: {result.stderr}")
            raise RuntimeError(f"FFmpeg failed: {result.returncode}")
    except FileNotFoundError:
        print("❌ FFmpeg не найден! Установи: sudo apt install ffmpeg")
        raise
    
    print(f"\n✅ Видео создано: {output_path}")
    print(f"   Размер: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")
    
    # Очистить временные кадры
    for f in frame_paths:
        os.remove(f)
    
    return output_path


if __name__ == '__main__':
    # Тестирование
    test_names = [f'user_{i}' for i in range(1, 21)]
    render_video(test_names, duration=5)
