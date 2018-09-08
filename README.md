# 同志社大学の休講情報取得API

## 開発環境
* Python3.6
* Flask

## 動作環境
* Heroku

## 機能
* 指定した日時・キャンパスの休講情報を取得
  * API URL  
    ```http://hack.doshisha.work/cancell/api/v1/'campusID'/'target_day'```
  * Response
  
    ```
    "data": {
        "campus": "キャンパス名",
        "date": "取得したときの時刻"
    },
    "cancelled_classes": {
        "Index": {
            "class_teacher": "担当教授",
            "class_cause": "休講理由",
            "class_hour": "時間",
            "class_name": "授業名"
        }
    }
    ```