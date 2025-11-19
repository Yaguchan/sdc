import cv2
import chime
import datetime
import numpy as np


# python test1.py


def main():

    # 準備で確認したデバイスのインデックス番号
    DEVICE_ID = 0

    # 「黒」と判定する輝度の平均値の閾値 (0〜255)
    BLACK_THRESHOLD = 5.0 

    # チェック間隔（秒）
    CHECK_INTERVAL = 0.5 
    # waitKey用にミリ秒に変換
    WAIT_MSEC = int(CHECK_INTERVAL * 1000)

    cap = cv2.VideoCapture(DEVICE_ID)

    if not cap.isOpened():
        print(f"エラー: デバイスID {DEVICE_ID} を開けません。")
        exit()

    print(f"デバイス {DEVICE_ID} の監視を開始しました。輝度閾値: {BLACK_THRESHOLD}")
    
    window_name = 'UltraStudio Input'
    
    # 状態を記憶する変数（True: 現在暗い / False: 現在明るい）
    # 最初は明るい状態と仮定
    is_dark = False

    while True:
        # フレームを読み込む
        ret, frame = cap.read()
        
        if not ret:
            print("エラー: フレームをキャプチャできませんでした。")
            break
        
        # 輝度の平均値を計算
        mean_brightness = frame.mean()

        # 1. 暗くなった瞬間を検知 (以前は明るかった AND 今は暗い)
        if mean_brightness < BLACK_THRESHOLD and not is_dark:
            is_dark = True  # 状態を「暗い」に更新
            
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"{timestamp} - 画面が暗くなりました (輝度: {mean_brightness:.2f})")
            chime.success() # 音を1回だけ鳴らす

        # 2. 明るくなった瞬間を検知 (以前は暗かった AND 今は明るい)
        elif mean_brightness >= BLACK_THRESHOLD and is_dark:
            is_dark = False # 状態を「明るい」に更新
            # (必要であれば) 明るくなった時のログも追加
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{timestamp} - 画面が明るくなりました (輝度: {mean_brightness:.2f})")
            
        # 3. 状態が変わらない (暗いまま or 明るいまま)
        # この場合は何もしない

        # 読み込んだフレームをウィンドウに表示
        cv2.imshow(window_name, frame)

        # 'q'キーが押されたらループを抜ける
        # CHECK_INTERVAL (ミリ秒) 待機し、キー入力を受け付ける
        key = cv2.waitKey(WAIT_MSEC) & 0xFF
        if key == ord('q'):
            print("終了します。")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()