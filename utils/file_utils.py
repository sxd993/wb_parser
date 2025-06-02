import json

def save_to_json(data, output_file):
    """Сохранение данных в JSON файл."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)