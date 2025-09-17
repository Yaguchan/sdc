import whisper
import os
import subprocess


# python run_asr.py
NAME = '20250714mini_va'
mp4_file = f'audio/{NAME}.mp4'
output_file = f'text/{NAME}.txt'
WORDPATH = 'wordlist/vhf.txt'


def make_prompt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        custom_words = [line.strip() for line in f if line.strip()]
    initial_prompt = "この会話には " + "、".join(custom_words) + " などの固有名詞が出てきます。"
    return initial_prompt


def mp4_to_wav(mp4_path, wav_path):
    subprocess.call(['ffmpeg', '-i', mp4_path, '-ar', '16000', '-ac', '1', wav_path])


def format_timestamp(seconds):
    """秒を mm:ss 形式に変換"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def transcribe_with_whisper(mp4_path, options):
    temp_wav = "audio/temp.wav"
    mp4_to_wav(mp4_path, temp_wav)
    model = whisper.load_model("medium")  # 必要に応じて small / large に変更可
    result = model.transcribe(
        temp_wav,
        **options
    )
    os.remove(temp_wav)
    return result["segments"]  # 各セグメントに start, end, text が含まれる


def main():
    
    initial_prompt = make_prompt(WORDPATH)
    options = {
        "language": "ja", 
        "initial_prompt": initial_prompt,
        "task": "transcribe",
        "fp16": False
    }
    print(options)
    
    segments = transcribe_with_whisper(mp4_file, options)
    with open(output_file, "w", encoding="utf-8") as f:
        for seg in segments:
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            text = seg["text"].strip()
            f.write(f"[{start} - {end}] {text}\n")

    print(f"時間付き文字起こしが {output_file} に保存されました。")


if __name__ == '__main__':
    main()