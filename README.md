# sdc
SDCで開発したものに関するメモやソースコードを載せておきます！

## dengonban
Outlookのメール**技術統括局・回線ｾﾝﾀｰ伝言板**をNotebookLMで、[チャットボット](https://notebooklm.google.com/notebook/709daef8-6c52-40da-bc14-510a42f4a969?_gl=1*168fzga*_up*MQ..*_ga*ODYxMzg2NjYuMTc1MzA2MTA1Mg..*_ga_W0LDH41ZCB*czE3NTMwNjEwNTEkbzEkZzAkdDE3NTMwNjEwNTEkajYwJGwwJGgw&gclid=CjwKCAjwp_LDBhBCEiwAK7Fnkj4rpX0oFUnbRmr6T3lGEwmSEMW-AU9Nm8_aMYQr_d2KVMi0yuPrRxoC8VMQAvD_BwE&gbraid=0AAAAA-fwSscdvVyAnl6v62astCd5ITyZB)にする。
[dengonban.pdf](https://github.com/user-attachments/files/21849449/dengonban.pdf)

### Outlookのメールをテキストファイルにまとめる
ローカルPCのテキストファイルの保存場所`basePath`を設定してから実行。
(Alt+F11 でVBAエディタを起動し、Project1を右クリック、挿入＞標準モジュールにコードをペーストし、F5で実行)
```
dengonban/ExportPublicFolderEmails.bas
```

## log_fpu
FPU運用で得られたデータを自動で記録する。
### run_video_easyocr.py
FPU端末の動画を収録し、OCRで画像認識を行うことで、架台における電界を取得する。
```
sample/run_video_easyocr.py
```
### run_video_easyocr2.py
元動画に画像認識部分・認識結果を反映させた動画を出力する。
※日本語(架台名)を出力するには、`FONT_PATH`を指定する必要がある
```
sample/run_video_easyocr2.py
```

## vhf_asr
VHF(無線)の音声を取得し、音声認識を行う。
インターホンのoutをパソコンに入力し、Microsoft Teamsの会議で使用できる音声認識で文字起こしする。
