import whisper
import os
import subprocess


# python run_asr.py
def mp4_to_wav(mp4_path, wav_path):
    subprocess.call(['ffmpeg', '-i', mp4_path, '-ar', '16000', '-ac', '1', wav_path])


def format_timestamp(seconds):
    """秒を mm:ss 形式に変換"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def transcribe_with_whisper(mp4_path):
    temp_wav = "temp.wav"
    mp4_to_wav(mp4_path, temp_wav)

    model = whisper.load_model("medium")  # 必要に応じて small / large に変更可
    result = model.transcribe(temp_wav, fp16=False)

    os.remove(temp_wav)
    return result["segments"]  # 各セグメントに start, end, text が含まれる


def main():
    mp4_file = "audio/20250714mini_va.mp4"
    segments = transcribe_with_whisper(mp4_file)

    output_file = "transcribed_text_with_timestamps.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for seg in segments:
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            text = seg["text"].strip()
            f.write(f"[{start} - {end}] {text}\n")

    print(f"時間付き文字起こしが {output_file} に保存されました。")


if __name__ == '__main__':
    main()