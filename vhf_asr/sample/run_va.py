import os
from pydub import AudioSegment, silence
from moviepy.editor import VideoFileClip, concatenate_videoclips


# python run_va.py
NAME = '20250714mini'
input_path = f"audio/{NAME}.mp4"
output_path = f"audio/{NAME}_va.mp4"
temp_audio_path = "temp_audio.wav" # 一時ファイルパスを定義


def main():
    video = VideoFileClip(input_path)
    
    try:
        # 1. 一時的に音声をwavとして抽出
        # logger=Noneでコンソール出力を抑制
        video.audio.write_audiofile(temp_audio_path, logger=None)

        # 2. pydubで音声読み込み
        audio = AudioSegment.from_wav(temp_audio_path)

        # 3. 無音区間で分割（有声部分を取得）
        chunks = silence.detect_nonsilent(
            audio,
            min_silence_len=500,  # 無音と判定する最小長さ（ms）
            silence_thresh=-40    # 無音とみなす音量（dBFS）
        )

        # 4. 有声部分の前後1秒を拡張
        extended_chunks = []
        audio_duration = len(audio)
        for start, end in chunks:
            start_extended = max(0, start - 1000)
            end_extended = min(audio_duration, end + 1000)
            extended_chunks.append((start_extended, end_extended))

        # 5. 重複または連続する区間をまとめる
        merged_chunks = []
        if extended_chunks:
            # 最初のチャンクを追加
            merged_chunks.append(list(extended_chunks[0])) 
            for start, end in extended_chunks[1:]:
                # 前のチャンクと重なっているかチェック
                if start <= merged_chunks[-1][1]:
                    # 重なっていたら終了時刻を更新
                    merged_chunks[-1][1] = max(merged_chunks[-1][1], end)
                else:
                    # 重なっていなければ新しいチャンクとして追加
                    merged_chunks.append([start, end])

        # 6. 動画の有声区間だけを切り出して結合
        clips = []
        for start, end in merged_chunks:
            # moviepyのsubclipは秒単位なので1000で割る
            clip = video.subclip(start / 1000, end / 1000)
            clips.append(clip)

        if clips:
            # 7. 結合して出力
            final_clip = concatenate_videoclips(clips)
            # ★★★ 音声コーデック 'aac' を指定して書き出す ★★★
            final_clip.write_videofile(output_path, audio_codec='aac', logger=None)
            final_clip.close()
        else:
            print("有効な音声区間が見つかりませんでした。")

    finally:
        # 8. リソースの解放と一時ファイルの削除
        video.close()
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            print(f"一時ファイル {temp_audio_path} を削除しました。")


if __name__ == '__main__':
    main()