#!/usr/bin/env python3
"""
main.py - Главный скрипт Generative Map.

Читает список подписчиков, генерирует тайлы, рендерит видео.
"""

import json
import sys
import os
from renderer import render_video


def load_subscribers(filepath: str = 'test_subscribers.json') -> list:
    """
    Загрузить список подписчиков из JSON.
    
    Args:
        filepath: Путь к JSON файлу
    
    Returns:
        list: Список username
    """
    if not os.path.exists(filepath):
        print(f"❌ Файл не найден: {filepath}")
        print("Создаю тестовый файл с 50 подписчиками...")
        create_test_subscribers(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('subscribers', [])


def create_test_subscribers(filepath: str = 'test_subscribers.json'):
    """Создать тестовый файл с подписчиками."""
    test_names = [
        "alex", "maria", "john", "anna", "david",
        "emma", "james", "sophia", "robert", "olivia",
        "michael", "isabella", "william", "ava", "richard",
        "mia", "joseph", "charlotte", "thomas", "amelia",
        "charles", "harper", "daniel", "evelyn", "matthew",
        "abigail", "anthony", "emily", "mark", "elizabeth",
        "donald", "sofia", "paul", "avery", "steven",
        "ella", "andrew", "chloe", "kenneth", "grace",
        "kevin", "victoria", "brian", "scarlett", "george",
        "madison", "edward", "lily", "ronald", "layla"
    ]
    
    data = {'subscribers': test_names}
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Создан файл: {filepath} ({len(test_names)} подписчиков)")


def main():
    """Главная функция."""
    print("=" * 50)
    print("  GENERATIVE MAP - Subscriber Visualizer")
    print("=" * 50)
    print()
    
    # Загрузить подписчиков
    subscribers_file = 'test_subscribers.json'
    if len(sys.argv) > 1:
        subscribers_file = sys.argv[1]
    
    print(f"Загрузка подписчиков из: {subscribers_file}")
    usernames = load_subscribers(subscribers_file)
    
    if not usernames:
        print("❌ Список подписчиков пуст!")
        sys.exit(1)
    
    print(f"✅ Загружено: {len(usernames)} подписчиков")
    print()
    
    # Параметры (фиксировано для быстрого теста)
    duration = 8
    fps = 30
    output_name = 'map_video.mp4'
    if not output_name.endswith('.mp4'):
        output_name += '.mp4'
    
    output_path = os.path.join('output', output_name)
    
    print()
    print("-" * 50)
    print(f"Настройки:")
    print(f"  Подписчиков: {len(usernames)}")
    print(f"  Длительность: {duration}s")
    print(f"  FPS: {fps}")
    print(f"  Выход: {output_path}")
    print("-" * 50)
    print()
    
    # Старт рендера
    try:
        render_video(usernames, output_path, duration, fps)
        print()
        print("=" * 50)
        print("✅ ГОТОВО!")
        print(f"Видео сохранено: {output_path}")
        print("=" * 50)
    except Exception as e:
        print()
        print("=" * 50)
        print(f"❌ ОШИБКА: {e}")
        print("=" * 50)
        sys.exit(1)


if __name__ == '__main__':
    main()