# 概要
バーチャルコンテスト用のbot．
機能をいろいろ追加していきたい．

なお，botは
- 各自でbot用のユーザーを作成する
- botのプログラムは各自のPC上で動作する
という仕様となっているため，準備が少々面倒かも．

(実は，別の所で作っていたbotを流用しているため，変なコードが混ざっているかもしれない)


# 対応OS
Windows, Ubuntu
(動作確認をしたのがこの2つというだけで，他のOSでも多分大丈夫)

# 準備
## botユーザーの準備
1. bot用のユーザーを作成する
2. `bot-token`を取得(コピーしておく)
3. `bot-token`を`config/config.json`の`bot_token`の項目に書く
4. botを自分のチャンネルに追加する

## PCでのinstallとsetup(Windows)
1. `python3`をインストールする．
   その際，デフォルトの設定のままインストールするのが望ましい(特に`pip`のインストールは必須)．
   なお，`async`/`await`を使うために，バージョンは`3.5`以上が必要
2. `wkhtmltopdf`をインストールする．
   公式webサイトからDLする(MinGW版で動作確認)．
   インストール先のディレクトリ(通常は`C:\Program Files\wkhtmltopdf`のはず)を覚えておく．
3. `virtual_contest`を(ディレクトリ丸ごと)ダウンロードし，(zipを解凍して)`setup.py`を実行する．
    - `python3`が適切にインストールできていれば，アイコンをダブルクリックすれば良いはず．
    - 「setupに成功しました」と出ていればOK．
    - setupに失敗した場合は，おそらく`wkhtmltopdf`のインストールあたりが原因．
        * まず，`wkhtmltopdf`がちゃんとインストールされているか確認．
        * インストールされていたら，実行ファイル(`wkhtmltopdf.exe`)のあるディレクトリにPathを通す．
          `wkhtmltopdf`のインストール時に表示されていたディレクトリにあるはず．

## PCでのinstallとsetup(Ubuntu)
1. `sudo apt install python3 python3-pip wkhtmltopdf`
2. `virtual_contest`をダウンロードして，そのディレクトリに移動し，`sudo python3 setup.py`


# 使い方
## 起動方法
- `main.py`をダブルクリックして起動する．
- 何らかの理由でそれが上手くいかない場合は，コマンドプロンプトで`python3 ssb_jinro.py`とすると上手くいくかも．
## discord上での操作方法
`!`で始まるメッセージがコマンドとして解釈される．
不正なコマンドを与えるとコマンドのヘルプが表示されるので，
とりあえず`!aiueo`などとしてみると良いかも．
(To be written...)
