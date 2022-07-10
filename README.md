# GCCP creator

由來：運用 GCP 服務的流程串接，建立 CC 字幕給影片編輯使用

Cloud Storage - Eventarc receive signal - Trigger CloudRun - Call Speech-To-Text API - CC generator - Save to Cloud Storage - Download!

Note:
- Cloud Run 需要設定 eventarc
- STT 不吃 mp4，檔案輸出時需要轉成 mp3 丟到 cloud storage 
- STT 轉出來會變成 datetime.timedelta 的格式，格式中不是 iterator，因此 API 回來後不能直接使用。[參考說明](https://stackoverflow.com/questions/3790848/fastest-way-to-convert-an-iterator-to-a-list)後要用 list 把它轉出來，才能抓到裡面的數值
- 原本打算用 WebVTT 格式操作，但在 [Youtube 文件](https://support.google.com/youtube/answer/2734698?hl=zh-Hant#zippy=%2C%E5%9F%BA%E6%9C%AC%E6%AA%94%E6%A1%88%E6%A0%BC%E5%BC%8F%2C%E9%80%B2%E9%9A%8E%E6%AA%94%E6%A1%88%E6%A0%BC%E5%BC%8F)中說明了`目前仍在初步實行階段`，因此在此專案中則是用 SRT 作為使用。
- videojs 中需要 Big5 才可以 generate，而在 SRT 中他需要 UTF-8，因此這邊就把Big5 拔除(TBC)

## 開發測試

上傳到 Cloud Storage 後，CloudRun 會收到訊號，內容很多，整理完主要使用為下列：

```json
{"name": "testing-1.mp3", "bucket": "my-bucket", "contentType": "audio/mpeg"}
```

## 參考

- [SRT format wiki](https://en.wikipedia.org/wiki/SubRip#SubRip_text_file_format)
- [YouTube 支援的字幕檔案](https://support.google.com/youtube/answer/2734698?hl=zh-Hant#zippy=%2C%E5%9F%BA%E6%9C%AC%E6%AA%94%E6%A1%88%E6%A0%BC%E5%BC%8F%2C%E9%80%B2%E9%9A%8E%E6%AA%94%E6%A1%88%E6%A0%BC%E5%BC%8F)
