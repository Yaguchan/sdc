# sdc
SDCで開発したものに関するメモやソースコードを載せておきます！

## dengonban
Outlookのメール**技術統括局・回線ｾﾝﾀｰ伝言板**をNotebookLMで、[チャットボット](https://notebooklm.google.com/notebook/709daef8-6c52-40da-bc14-510a42f4a969?_gl=1*168fzga*_up*MQ..*_ga*ODYxMzg2NjYuMTc1MzA2MTA1Mg..*_ga_W0LDH41ZCB*czE3NTMwNjEwNTEkbzEkZzAkdDE3NTMwNjEwNTEkajYwJGwwJGgw&gclid=CjwKCAjwp_LDBhBCEiwAK7Fnkj4rpX0oFUnbRmr6T3lGEwmSEMW-AU9Nm8_aMYQr_d2KVMi0yuPrRxoC8VMQAvD_BwE&gbraid=0AAAAA-fwSscdvVyAnl6v62astCd5ITyZB)にする。
![Image](https://github.com/user-attachments/assets/d750a289-9443-4269-aac0-65845309bda0)

### Outlookのメールをテキストファイルにまとめる
ローカルPCのテキストファイルの保存場所`basePath`を設定してから実行。  
(`Alt+F11`でVBAエディタを起動。`Project1`を右クリック、`挿入＞標準モジュール`にコードをペースト。`F5`で実行)
```
dengonban/ExportPublicFolderEmails.bas
```

## log_fpu
FPU運用で得られたデータを自動で記録する。（[デモ映像](https://drive.google.com/file/d/1p79cPBcLg5ipJp6whAltpFlXx_I5oAG-/view?usp=sharing)）
![Image](https://github.com/user-attachments/assets/930c1340-723d-4b90-813d-841e163d69b0)
### run_video_easyocr.py
FPU端末の動画を収録し、OCRで画像認識を行うことで、架台における電界を取得する。
```
python log_fpu/sample/run_video_easyocr.py
```
### run_video_easyocr2.py
元動画に画像認識部分・認識結果を反映させた動画を出力する。  
※日本語(架台名)を出力するには、`FONT_PATH`を指定する必要がある
```
python log_fpu/sample/run_video_easyocr2.py
```

## alarm_moni
MTX出力の1本(HD-AUX)をPCに取り込み、PC上で黒を認識したらアラーム音が鳴るような試作品です。（[デモ映像](https://drive.google.com/file/d/1KKdxOOdOs7ReH4y6OafO6wANqJtSF8jW/view?usp=sharing)）  
(HD-AUX→TD卓TRKのSDIを、ブラマジの変換器を使い、USB typeC でPCに取り込む。  
取り込んだ信号をpythonのOpenCVを使用して、ストリーミング処理でアラーム条件を確認)  
ちなみに、[音読さん](https://ondoku3.com/ja/)でアラーム音(wav)生成を行なっています。  
![Image](https://github.com/user-attachments/assets/d36f1daa-2d56-4eec-8c3e-4f0e3feaf83e)
### 黒/フリーズ検知
```
python alarm_moni/sample/test1.py
```

## vhf_asr
VHF(無線)の音声を取得し、音声認識を行う。  
インターホンのoutをパソコンに入力し、Microsoft Teamsの会議で使用できる音声認識で文字起こしする。
