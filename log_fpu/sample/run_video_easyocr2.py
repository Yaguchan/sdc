import cv2
import easyocr
import numpy as np
from PIL import Image, ImageDraw, ImageFont


# python run_video_easyocr2.py
# 入力する動画ファイルのパス
NAME = '2025-07-18 15-17-46'
VIDEO_PATH = f'data/{NAME}.mp4'
# 出力するログファイルのパス
LOG_FILE_PATH = f'data/log_{NAME}.txt'
# 出力する動画ファイルのパス
OUTPUT_VIDEO_PATH = f'data/output_{NAME}.mp4'
# OCRを実行する間隔（秒）
PROCESS_INTERVAL_SECONDS = 1.0
# 切り抜く座標のリスト (左, 上, 右, 下)
POSITIONS = [
    (1434, 396, 1529, 439), (1434, 451, 1505, 495), (1550, 451, 1603, 495), (1628, 451, 1696, 495),
    (1727, 67, 1905, 125), (1727, 137, 1905, 195), (476, 90, 587, 123), (1320, 81, 1410, 125), (476, 133, 587, 168), (1320, 133, 1410, 177)
]
# 枠線（画像認識部分）の設定
RECT_COLOR = (252, 15, 192) # (B, G, R) - ピンク色
RECT_THICKNESS = 3 # 枠線の太さ
# テキスト描画設定
FONT_PATH = '../font/Noto_Sans_JP/static/NotoSansJP-Regular.ttf'
FONT_SIZE = 32
TEXT_COLOR = (255, 15, 192) # 白色
# テキストボックス設定
BOX_COLOR = (255, 255, 255, 255) # (R, G, B, Alpha) - 半透明の黒(128)
BOX_PADDING = 5 # テキストと背景ボックスの間の余白


def result_to_ctext(results):
    """EasyOCRの結果を連結した文字列に変換する"""
    detected_text = " ".join([res[1] for res in results])
    ctext = detected_text.replace(' ', '')
    return ctext


def draw_text_on_frame(frame, text, font_path, font_size, text_color, box_color, box_padding):
    """Pillowを使ってフレームに背景付きの日本語テキストを描画する"""
    # OpenCVのフレーム(BGR)をPillowのImage(RGBA)に変換して透明度を扱えるようにする
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
    
    # 描画用の別レイヤーを作成（完全に透明）
    txt_layer = Image.new("RGBA", img_pil.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"フォントファイルが見つかりません: {font_path}")
        print("デフォルトフォントを使用します（日本語は表示されない可能性があります）。")
        font = ImageFont.load_default()

    # テキストの描画位置を計算（右下）
    frame_width, frame_height = img_pil.size
    
    # textbboxでテキストサイズを取得
    if hasattr(draw, 'textbbox'):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        # 古いバージョン用のフォールバック
        text_width, text_height = draw.textsize(text, font=font)

    margin = 15
    
    # 背景ボックスの座標を計算
    box_right = frame_width - margin
    box_bottom = frame_height - margin
    box_left = box_right - text_width - (box_padding * 2)
    box_top = box_bottom - text_height - (box_padding * 2)
    
    # 背景ボックスを描画
    draw.rectangle([(box_left, box_top), (box_right, box_bottom)], fill=box_color)
    
    # テキストを描画 (PillowはRGBAで色を指定)
    text_position = (box_left + box_padding, box_top + box_padding)
    # text_color(BGR)をRGBAに変換して描画
    draw.text(text_position, text, font=font, fill=text_color[::-1] + (255,))

    # 元の画像とテキストレイヤーをアルファブレンディングで合成
    out_img = Image.alpha_composite(img_pil, txt_layer)

    # OpenCVのフレーム(BGR)に変換して返す
    return cv2.cvtColor(np.array(out_img), cv2.COLOR_RGBA2BGR)


def main():
    # OCRリーダーの初期化
    reader = easyocr.Reader(['en', 'ja'], gpu=False, verbose=False)
    # reader = easyocr.Reader(['en'], gpu=False, verbose=False)

    # 動画ファイルの読み込み
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"エラー: 動画ファイル {VIDEO_PATH} を開けませんでした。")
        return

    # 動画のプロパティを取得
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # 出力用のVideoWriterを初期化
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_VIDEO_PATH, fourcc, fps, (width, height))

    process_interval_frames = int(fps * PROCESS_INTERVAL_SECONDS) if PROCESS_INTERVAL_SECONDS > 0 else 1
    print(f"動画処理を開始します。（{process_interval_frames}フレームごとに処理）")
    print(f"出力動画: {OUTPUT_VIDEO_PATH}")

    frame_count = 0
    last_log_data = "" # 描画する最後のテキストを保持

    # 基地局取り出しの際の色範囲（HSV）
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([100, 255, 255])

    try:
        with open(LOG_FILE_PATH, 'w', encoding='utf-8') as log_file:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break # 動画の終端に達した

                # --- OCR処理 ---
                if frame_count % process_interval_frames == 0:
                    all_texts_for_frame = []

                    # 基地局のOCR
                    cropped_frame_base = frame[0:50, 160:1120]
                    hsv = cv2.cvtColor(cropped_frame_base, cv2.COLOR_BGR2HSV)
                    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
                    masked_frame = cv2.bitwise_and(cropped_frame_base, cropped_frame_base, mask=mask)
                    results_base = reader.readtext(masked_frame)
                    all_texts_for_frame.append(result_to_ctext(results_base))

                    # 指定座標の文字読み取り
                    for p in POSITIONS:
                        left, upper, right, lower = p
                        cropped_frame_pos = frame[upper:lower, left:right]
                        results_pos = reader.readtext(cropped_frame_pos)
                        if not results_pos:
                            all_texts_for_frame.append('-1')
                        else:
                            all_texts_for_frame.append(result_to_ctext(results_pos))

                    # ログデータを更新
                    log_data_line = " ".join(all_texts_for_frame)
                    log_file.write(log_data_line + "\n")
                    print(log_data_line)
                    last_log_data = log_data_line # 描画用テキストを更新
                
                # --- 座標の枠線を描画 ---
                for p in POSITIONS:
                    left, upper, right, lower = p
                    cv2.rectangle(frame, (left, upper), (right, lower), RECT_COLOR, RECT_THICKNESS)

                # --- フレームへの描画と書き出し ---
                output_frame = frame
                if last_log_data: # 描画するテキストがあれば描画
                    output_frame = draw_text_on_frame(frame, last_log_data, FONT_PATH, FONT_SIZE, TEXT_COLOR, BOX_COLOR, BOX_PADDING)

                # 処理したフレームを動画ファイルに書き込む
                out.write(output_frame)

                frame_count += 1

    except KeyboardInterrupt:
        print("\n処理が中断されました。")
    finally:
        # リソースを解放
        cap.release()
        out.release()
        print(f"\n処理を終了しました。")
        print(f"ログは {LOG_FILE_PATH} を確認してください。")
        print(f"テキスト付き動画は {OUTPUT_VIDEO_PATH} に保存されました。")


if __name__ == '__main__':
    main()