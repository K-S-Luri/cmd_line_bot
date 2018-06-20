# 概要
バーチャルコンテスト用のbot(だけど，今のところはbot作成用のフレームワーク部分しかできてない)．
機能をいろいろ追加していきたい．

なお，botは
- 各自でbot用のユーザーを作成する
- botのプログラムは各自のPC上で動作する
という仕様となっているため，準備が少々面倒かも．

# 動作環境
- OSは多分何でも大丈夫(Ubuntu上で開発)
- `python3` (`version > 3.6`)
    * `Ubuntu 16.04`に`python 3.6`を(ソースからビルドして)インストールする際に，
      `make test`で`test_urllib2net`に失敗した．
      これは，`sudo apt install libssl-dev`することで解決した．
      参考: [Import Error: No module named _ssl](https://stackoverflow.com/questions/5128845/importerror-no-module-named-ssl)
- 以下のpythonライブラリが必要
    * `discord` (`python3 -m pip install -U discord.py`)
    * `pytypes` (`python3 -m pip install pytypes`)

# documentation
## main.py
名前の通り．`CmdLineBot`, `CLBFrontEnd`, `CLBBackEnd`の使い方はここを見ると良いかも．

## cmd_line_bot.py
frontendとbackendの間のインターフェースを規定している．
- `CmdLineBot`: bot本体
-  `CLBFrontEnd`: ユーザーとのインターフェースを与える．Abstract Classなので，継承して実装を与える必要がある．
   主にdiscordを想定．テスト用に，通信を介さずlocalで完結するfrontendも用意するつもり．
-  `CLBBackEnd`: bot本体の処理を行う．こちらもAbstract Class．
-  `CLBTask`, `CLBCmdLine`: `CLBFrontEnd`と`CLBBackEnd`の間でデータのやりとりをするためのclass．

## discord_frontend.py
discord用の`CLBFrontEnd`．

## cmd_arg_backend.py
shellっぽい感じでbotを操作する`CLBBackEnd`．
実際の使い方については`example_backend.py`を見てほしい．
コマンドラインのパースは`parser.py`が担当．

## trivial_ends.py
暫定的にテキトーに作っただけなので，多分そのうち消す．

# 利用方法
## botユーザーの準備
1. [Discordデベロッパーページ](https://discordapp.com/developers/applications/me)
   でbot用のユーザーを作成する
2. `bot-token`を取得(コピーしておく)
3. botを自分のチャンネルに追加する
4. `~/.clbconfig.json` に以下の形のjsonデータを作成
```json
{
    "discord": {
        "token": "上で取得したbot-token"
    }
}
```

## PCでのinstallとsetup(Windows)
1. `python3`をインストールする．
   その際，デフォルトの設定のままインストールするのが望ましい(特に`pip`のインストールは必須)．
   なお，`async`/`await`を使うために，バージョンは`3.5`以上が必要

## PCでのinstallとsetup(Ubuntu)
1. `sudo apt install python3 python3-pip wkhtmltopdf`

# TODO
## 大きなやつ
- type hints
- マルチスレッド化
- cron的なやつ(要マルチスレッド)
- バチャコン機能

## 細かいやつ
- `CLBTask` をサブクラスに分ける
- `!init` したときにbackendがエラーを吐くのを修正
- コマンドのエラーメッセージの調整
  (ルートコマンドなのに「サブコマンド名が不正」と出る)
- `discord.pyi`でclassのattributeのtype hintはどうやって書く？(e.g. `client.user.name`がstrだと知らせたい)
- `json`から読みとったデータを利用する際は，(特に実行時の)型チェックに気を使った方が良さそう．
  →`@typechecked`を利用する？
- `isinstance`はなるべく排除し，`@typechecked`を利用する．
- チャンネル名が不正だったときのエラーメッセージが，terminal上にしか出てこない
- `CmdLineBot.run()`で`sleep(10)`してるの，もうちょっとどうにかならない？
