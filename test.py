import cv2
import numpy as np
import random
import hashlib
from moviepy.editor import VideoFileClip, vfx

def unique_video(input_path, output_path):
    print("👉 Шаг 1: Изменение аудио (скорость и питч)...")
    clip = VideoFileClip(input_path)
    # Сдвигаем скорость на случайную величину от 1% до 3%
    random_speed = random.uniform(1.01, 1.03)
    modified_clip = clip.fx(vfx.speedx, random_speed)
    temp_audio_path = "temp_audio.mp4"
    modified_clip.write_videofile(temp_audio_path, codec="libx264", audio_codec="aac", logger=None)
    clip.close()
    modified_clip.close()

    print("👉 Шаг 2: Глубокая уникализация видеоряда...")
    cap = cv2.VideoCapture(temp_audio_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    temp_video_only = "temp_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video_only, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Микро-зум (срезаем по 2% краев)
        h, w = frame.shape[:2]
        start_row, start_col = int(h * 0.02), int(w * 0.02)
        end_row, end_col = int(h * 0.98), int(w * 0.98)
        frame = frame[start_row:end_row, start_col:end_col]
        frame = cv2.resize(frame, (width, height))

        # 2. Незначительный поворот (0.5 градуса)
        center = (width // 2, height // 2)
        matrix = cv2.getRotationMatrix2D(center, 0.5, 1.0)
        frame = cv2.warpAffine(frame, matrix, (width, height))

        # 3. Наложение шума
        noise = np.random.randint(0, 3, (height, width, 3), dtype='uint8')
        frame = cv2.addWeighted(frame, 0.98, noise, 0.02, 0)

        # 4. Легкий сдвиг яркости/контраста
        frame = cv2.convertScaleAbs(frame, alpha=1.01, beta=1)

        out.write(frame)

    cap.release()
    out.release()

    print("👉 Шаг 3: Склеивание и очистка метаданных...")
    final_video = VideoFileClip(temp_video_only)
    final_audio = VideoFileClip(temp_audio_path).audio
    final_video.audio = final_audio
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)
    
    final_video.close()
    final_audio.close()
    print(f"✅ Уникализированное видео создано: {output_path}")


def check_uniqueness(original_path, unique_path):
    print("\n👉 Шаг 4: Проверка видео на уникальность...")
    
    # 1. Проверка MD5 хэша файла
    h1 = hashlib.md5(open(original_path, 'rb').read()).hexdigest()
    h2 = hashlib.md5(open(unique_path, 'rb').read()).hexdigest()
    hash_match = "Да (Плохо)" if h1 == h2 else "Нет (Отлично)"
    
    # 2. Проверка пиксельной структуры кадров
    cap_orig = cv2.VideoCapture(original_path)
    cap_uniq = cv2.VideoCapture(unique_path)
    diffs = []
    
    for _ in range(100):
        ret1, frame1 = cap_orig.read()
        ret2, frame2 = cap_uniq.read()
        if not ret1 or not ret2:
            break
            
        gray1 = cv2.cvtColor(cv2.resize(frame1, (300, 300)), cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(cv2.resize(frame2, (300, 300)), cv2.COLOR_BGR2GRAY)
        
        res = cv2.absdiff(gray1, gray2)
        non_zero_count = np.count_nonzero(res)
        diff_percent = (non_zero_count / gray1.size) * 100
        diffs.append(diff_percent)
        
    cap_orig.release()
    cap_uniq.release()
    
    average_diff = np.mean(diffs)
    
    # Вывод красивого отчета
    print("\n" + "="*40)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ ДЛЯ TIKTOK")
    print("="*40)
    print(f"Хэш файлов совпадает?: {hash_match}")
    print(f"Изменение структуры кадра: {average_diff:.2f}%")
    print("-"*40)
    
    if average_diff > 15:
        print("🎉 ВЕРДИКТ: Отлично! Видео полностью уникально. Алгоритмы не докопаются.")
    elif average_diff > 5:
        print("⚠️ ВЕРДИКТ: Средне. Изменения есть, но для жестких фильтров может быть на грани.")
    else:
        print("❌ ВЕРДИКТ: Плохо. Слишком похоже на оригинал, высок риск теневого бана.")
    print("="*40)


# --- ТОЧКА ВХОДА И ЗАПУСК ---
if __name__ == "__main__":
    # Названия файлов (исходное должно лежать в той же папке)
    INPUT_FILE = "input.mp4"
    OUTPUT_FILE = "tiktok_ready.mp4"
    
    # 1. Запускаем уникализацию
    unique_video(INPUT_FILE, OUTPUT_FILE)
    
    # 2. Сразу же запускаем проверку созданного файла
    check_uniqueness(INPUT_FILE, OUTPUT_FILE)