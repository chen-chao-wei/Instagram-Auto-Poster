# Instagram Auto Poster

此腳本自動化產生貼文圖片並可配合 Google Trends 熱門關鍵字產生貼文文字，協助使用者快速建立 Instagram 貼文素材。

## 依賴安裝

請先安裝 Python 3，接著執行：

```bash
pip install -r requirements.txt
```

## 使用方式

1. 在 `.env` 或 `settings.py` 中設定 Canva Cookie 與模板連結。
2. 執行 `python main.py` 產生貼文圖片與文字。

產出檔案將存於 `output/` 目錄。

## 自動發佈至 Instagram

若要在產生內容後直接發佈貼文，需再於 `.env` 設定：

```
IG_USER_ID=<你的 IG 使用者 ID>
IG_ACCESS_TOKEN=<長效存取權杖>
GH_TOKEN=<你的 GitHub Token>
GH_REPO=chen-chao-wei/Image
```

腳本會將下載的圖片上傳到指定的 GitHub 儲存庫，再使用產生的連結發佈 IG 貼文，可直接呼叫 `instagram_api.upload_and_publish()`。
