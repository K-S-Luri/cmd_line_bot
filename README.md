# 概要
バーチャルコンテスト用のbot(だけど，今のところはbot作成用のフレームワーク部分しかできてない)．
機能をいろいろ追加していきたい．

なお，botは
- 各自でbot用のユーザーを作成する
- botのプログラムは各自のPC上で動作する
という仕様となっているため，準備が少々面倒かも．

# 動作環境
- OSは多分何でも大丈夫(Ubuntu上で開発)
- `python3` (`version > 3.5`)

# documentation
## `main.py`
名前の通り．`CmdLineBot`, `CLBFrontEnd`, `CLBBackEnd`の使い方はここを見ると良いかも．

## `cmd_line_bot.py`
frontendとbackendの間のインターフェースを規定している．
- `CmdLineBot`: bot本体
-  `CLBFrontEnd`: ユーザーとのインターフェースを与える．Abstract Classなので，継承して実装を与える必要がある．
   主にdiscordを想定．テスト用に，通信を介さずlocalで完結するfrontendも用意するつもり．
-  `CLBBackEnd`: bot本体の処理を行う．こちらもAbstract Class．
-  `CLBTask`, `CLBCmdLine`: `CLBFrontEnd`と`CLBBackEnd`の間でデータのやりとりをするためのclass．

## `discord_frontend.py`
discord用の`CLBFrontEnd`．

## `cmd_arg_backend.py`
shellっぽい感じでbotを操作する`CLBBackEnd`．
実際の使い方については`example_backend.py`を見てほしい．
コマンドラインのパースは`parser.py`が担当．

## `trivial_ends.py`
暫定的にテキトーに作っただけなので，多分そのうち消す．

# 利用方法
## botユーザーの準備
1. bot用のユーザーを作成する
2. `bot-token`を取得(コピーしておく)
3. botを自分のチャンネルに追加する

## PCでのinstallとsetup(Windows)
1. `python3`をインストールする．
   その際，デフォルトの設定のままインストールするのが望ましい(特に`pip`のインストールは必須)．
   なお，`async`/`await`を使うために，バージョンは`3.5`以上が必要

## PCでのinstallとsetup(Ubuntu)
1. `sudo apt install python3 python3-pip wkhtmltopdf`
