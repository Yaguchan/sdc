import cv2
import datetime
import numpy as np

# アラーム音
import chime
# 音再生中処理を行わないため、BAD
# from pydub import AudioSegment
# from pydub.playback import play
# 音再生中処理を行うことができるため、GOOD
import simpleaudio as sa


# python test1.py


def main():

    # 準備で確認したデバイスのインデックス番号
    DEVICE_ID = 0

    # 「黒」の判定条件
    BLACK_THRESHOLD = 5.0       # 輝度の平均値の閾値 (0〜255)
    # 「フリーズ」と判定
    FREEZE_THRESHOLD = 0.5      # 前フレームとの差分のフレーム平均値
    FREEZE_COUNT = 3            # 何フレームでアラームか

    # チェック間隔（秒） = フレームレート
    CHECK_INTERVAL = 1/60
    # waitKey用にミリ秒に変換
    WAIT_MSEC = int(CHECK_INTERVAL * 1000)
    
    # pydub
    # sound = AudioSegment.from_file("../wav/black.mp3", format="mp3")
    # simpleaudio
    wave_black = sa.WaveObject.from_wave_file("../wav/black.wav")
    wave_freeze = sa.WaveObject.from_wave_file("../wav/freeze.wav")

    cap = cv2.VideoCapture(DEVICE_ID)

    if not cap.isOpened():
        print(f"エラー: デバイスID {DEVICE_ID} を開けません。")
        exit()

    print(f"デバイス {DEVICE_ID} の監視を開始しました。輝度閾値: {BLACK_THRESHOLD}")
    
    window_name = 'UltraStudio Input'
    
    # 
    black_detected = False
    freeze_count = 0
    prev_frame = None

    while True:
        # フレームを読み込む
        ret, frame = cap.read()
        
        if not ret:
            continue
            # print("エラー: フレームをキャプチャできませんでした。")
            # break
        
        # 輝度の平均値
        mean_brightness = frame.mean()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_frame is not None:
            diff = np.mean(cv2.absdiff(gray, prev_frame))
            # 黒
            if mean_brightness < BLACK_THRESHOLD and not black_detected:
                now = datetime.datetime.now()
                timestamp = now.strftime("%Y-%m-%d %H:%M:%S")            
                print(f"{timestamp} - 画面が暗くなりました (輝度: {mean_brightness:.2f})")
                # chime.success()                       # chime
                # play(sound)                           # pydub
                play_black_obj = wave_black.play()    # simpleaudio
                black_detected = True

            # 黒以外
            elif mean_brightness >= BLACK_THRESHOLD:
                now = datetime.datetime.now()
                timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                
                # 黒み復帰
                if black_detected:
                    black_detected = False
                    print(f"{timestamp} - 画面が明るくなりました (輝度: {mean_brightness:.2f})")
                    
                # フリーズ検出
                if diff < FREEZE_THRESHOLD:
                    freeze_count += 1
                    if freeze_count == FREEZE_COUNT:
                        print(f"{timestamp} - 画面がフリーズしました")
                        play_freeze_obj = wave_freeze.play()
                else:
                    if freeze_count >= 3:
                        print(f"{timestamp} - 画面がフリーズから復旧しました")
                    freeze_count = 0
            
            
        # 3. 状態が変わらない (暗いまま or 明るいまま)
        # この場合は何もしない
        
        # 前のフレームの更新
        prev_frame = gray

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