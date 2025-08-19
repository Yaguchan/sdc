import cv2
import easyocr
import numpy as np


# python run_video_easyocr.py
# 入力する動画ファイルのパス
NAME = '2025-07-18 15-17-46'
VIDEO_PATH = f'data/{NAME}.mp4'
# 出力するログファイルのパス
LOG_FILE_PATH = f'data/log_{NAME}.txt'
# OCRを実行する間隔（秒）
PROCESS_INTERVAL_SECONDS = 1.0
# 切り抜く座標のリスト (左, 上, 右, 下)
POSITIONS = [
    (1434, 396, 1529, 439), (1434, 451, 1505, 495), (1550, 451, 1603, 495), (1628, 451, 1696, 495),
    (1727, 67, 1905, 125), (1727, 137, 1905, 195), (476, 90, 587, 123), (1320, 81, 1410, 125), (476, 133, 587, 168), (1320, 133, 1410, 177)
]


def result_to_ctext(results):
    detected_text = " ".join([res[1] for res in results])
    ctext = detected_text.replace(' ', '')
    return ctext


def main():

    reader = easyocr.Reader(['en', 'ja'], gpu=False, verbose=False)
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"エラー: 動画ファイル {VIDEO_PATH} を開けませんでした。")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    process_interval_frames = int(fps * PROCESS_INTERVAL_SECONDS) if PROCESS_INTERVAL_SECONDS > 0 else 1
    print(f"動画処理を開始します。（{process_interval_frames}フレームごとに処理）")
    frame_count = 0
    
    # 基地局取り出しの際の下限/上限
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([100, 255, 255])

    try:
        with open(LOG_FILE_PATH, 'w', encoding='utf-8') as log_file:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_count % process_interval_frames == 0:
                    all_texts_for_frame = [] #[f'{frame_count // process_interval_frames}[s]']
                    # 基地局
                    cropped_frame = frame[0:50, 160:1120]
                    hsv = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)
                    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
                    # cv2.imwrite('./mask_.jpg', mask)
                    masked_frame = cv2.bitwise_and(cropped_frame, cropped_frame, mask=mask)
                    #cv2.imwrite('./img.jpg', masked_frame)
                    results = reader.readtext(masked_frame)
                    all_texts_for_frame.append(result_to_ctext(results))
                    # 文字読み取り
                    for p in POSITIONS:
                        left, upper, right, lower = p
                        cropped_frame = frame[upper:lower, left:right]
                        results = reader.readtext(cropped_frame)
                        if not results: all_texts_for_frame.append('-1')
                        else: all_texts_for_frame.append(result_to_ctext(results))
                    log_data = " ".join(all_texts_for_frame) + "\n"
                    log_file.write(log_data)
                    print(log_data, end='')
                frame_count += 1
    except KeyboardInterrupt:
        print("\n処理が中断されました。")
    finally:
        cap.release()
        print(f"処理を終了しました。ログは {LOG_FILE_PATH} を確認してください。")


if __name__ == '__main__':
    main()