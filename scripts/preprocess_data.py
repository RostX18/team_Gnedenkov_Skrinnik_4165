import os
import numpy as np
import chess.pgn
from tqdm import tqdm
import yaml

# Загрузка конфига
with open("configs/default.yaml", "r") as f:
    config = yaml.safe_load(f)

def extract_moves_from_pgn(pgn_file_path, max_games=None):
    """
    Извлекает последовательности ходов из PGN файла
    """
    all_sequences = []
    game_count = 0
    
    with open(pgn_file_path) as pgn_file:
        while True:
            # Читаем одну партию
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
                
            game_count += 1
            if max_games and game_count > max_games:
                break
                
            # Извлекаем ходы из партии
            moves = []
            node = game
            while node.variations:
                next_node = node.variation(0)
                moves.append(str(next_node.move))
                node = next_node
            
            # Разбиваем на последовательности длины sequence_length
            seq_len = config['data']['sequence_length']
            for i in range(len(moves) - seq_len):
                sequence = moves[i:i + seq_len + 1]  # +1 потому что последний ход - target
                all_sequences.append(sequence)
    
    return all_sequences

def save_sequences(sequences, output_path):
    """
    Сохраняет последовательности в numpy формат
    """
    # Преобразуем в numpy array
    sequences_array = np.array(sequences, dtype=object)
    
    # Сохраняем
    np.save(output_path, sequences_array)
    print(f"Сохранено {len(sequences)} последовательностей в {output_path}")
    
    return sequences_array

def main():
    # Путь к PGN файлу 
    pgn_path = "data/raw/lichess_games.pgn"
    
    # Проверяем существование файла
    if not os.path.exists(pgn_path):
        print(f"Файл {pgn_path} не найден!")
        print("Скачай тестовый файл с https://database.lichess.org и положи в data/raw/")
        return
    
    print("Извлечение ходов из PGN...")
    sequences = extract_moves_from_pgn(pgn_path, max_games=100)  # Для теста 100 партий
    
    # Создаём папку processed если её нет
    os.makedirs("data/processed", exist_ok=True)
    
    # Сохраняем
    output_path = "data/processed/move_sequences.npy"
    save_sequences(sequences, output_path)
    
    # Выводим статистику
    print(f"\nСтатистика:")
    print(f"Всего последовательностей: {len(sequences)}")
    print(f"Пример последовательности: {sequences[0]}")
    print(f"Длина последовательности: {len(sequences[0])}")

if __name__ == "__main__":
    main()
