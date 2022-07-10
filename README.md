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

## 部署

透過 gcloud 指令把專案推上去，方便在不需要本地透過 Docker 建立 container，推上去之後會在 GCP 上自動建立 Container 並提供給 CloudRUn 使用。

```shell
gcloud run deploy nijia-cloud-run-example-1 --source .
```

## 參考

- [SRT format wiki](https://en.wikipedia.org/wiki/SubRip#SubRip_text_file_format)
- [YouTube 支援的字幕檔案](https://support.google.com/youtube/answer/2734698?hl=zh-Hant#zippy=%2C%E5%9F%BA%E6%9C%AC%E6%AA%94%E6%A1%88%E6%A0%BC%E5%BC%8F%2C%E9%80%B2%E9%9A%8E%E6%AA%94%E6%A1%88%E6%A0%BC%E5%BC%8F)

<img width="982" alt="截圖 2022-07-10 下午4 55 54" src="https://user-images.githubusercontent.com/6940010/178138504-67322953-83c0-40d5-b2c0-b52c7bf23304.png">
<img width="843" alt="截圖 2022-07-10 下午4 58 07" src="https://user-images.githubusercontent.com/6940010/178138509-bc1346a1-cd32-4866-9ef8-94a542adcbda.png">
<img width="915" alt="截圖 2022-07-10 下午4 58 23" src="https://user-images.githubusercontent.com/6940010/178138510-98f9c361-7911-441e-8578-3da482d0cf37.png">
<img width="677" alt="截圖 2022-07-10 下午4 58 44" src="https://user-images.githubusercontent.com/6940010/178138513-3a91d96c-af10-4ed8-925b-5d22d879c063.png">
<img width="590" alt="截圖 2022-07-10 下午4 59 03" src="https://user-images.githubusercontent.com/6940010/178138514-8319e00b-81a1-486f-b841-7c3f1866c122.png">
<img width="905" alt="截圖 2022-07-10 下午5 02 05" src="https://user-images.githubusercontent.com/6940010/178138516-31b8ced1-8e69-454c-9b70-521b49cc0353.png">
<img width="570" alt="截圖 2022-07-10 下午5 03 18" src="https://user-images.githubusercontent.com/6940010/178138517-e77fa6f3-c74d-4d9a-8784-4b7aca9506a7.png">

