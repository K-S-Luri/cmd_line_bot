# 概要
主に discord を念頭に置いた bot framework．

## frontend
  ユーザーとのやりとりを取り扱う部分．
  現状では discord を介するものと，terminal 上で完結するもの(test 用)がある．
  例えば slack に対応させるのも容易なはず．
## backend
  bot の内部処理を行う部分．
  現状では AtCoder バーチャルコンテストの AC 通知を行うものだけ．
  バチャコンそのものの開催ができる backend を開発中．


# 動作環境
- OSは多分何でも大丈夫(Ubuntu上で開発)
- `python3.6` を推奨．
  多分 `3.7` でも動くはず． `3.5` では動作しない．

# 利用方法
botは

- 各自でbot用のユーザーを作成する
- botのプログラムは各自のPC上で動作する

という仕様となっているため，準備が少々面倒かも．

## botユーザーの準備
1. [Discordデベロッパーページ](https://discordapp.com/developers/applications/me)
   でbot用のユーザーを作成する
2. `bot-token`を取得(コピーしておく)
3. botを自分のサーバーに追加する
4. `~/.clb.d/config.yaml` に以下の形のyamlデータを作成
```yaml
discord:
    token: "上で取得したbot-token"
    servername: "あなたのサーバーの名前"
```

## install python3 (and wkhtmltopdf)
### Windows
1. `python3`をインストールする．
   その際，デフォルトの設定のままインストールするのが望ましい(特に`pip`のインストールは必須)．
   なお，`async`/`await`を使うために，バージョンは`3.5`以上が必要
2. [wkhtmltopdf](https://wkhtmltopdf.org/) から wkhtmltopdf をインストール．
    - これは入れなくても大半のコマンドは動作する．
    - インストール先は変えない方が望ましい．
      どうしても変えたいなら，ちゃんと PATH を通すこと．

### Ubuntu
1. `sudo apt install python3 python3-pip wkhtmltopdf`

## install `cmd_line_bot`
`setup.py` があるディレクトリで
```bash
pip install .
```
を実行する．

- ある程度新しいバージョンの `pip` が必要なので，予め `pip install -U pip` しておく．
- 権限で怒られるなら `sudo pip install .` か `pip install --user .`
- `python` のバージョンが複数あったりする場合は `python3.6 -m pip install .` みたいな感じで．
- 以下の warning が出るかもしれないけど，気にしない
```
discord-py 0.16.12 has requirement aiohttp<1.1.0,>=1.0.0, but you'll have aiohttp 3.5.4 which is incompatible.
discord-py 0.16.12 has requirement websockets<4.0,>=3.1, but you'll have websockets 7.0 which is incompatible.
```

## 設定項目一覧
    `~/.clb.d/config.yaml`の例
```yaml
discord:
    token: "上記参照"
    servername: "上記参照"
ipc_frontend:
    port: 12345
```

# development
- [tutorial.md](doc/tutorial.md) に簡単な tutorial が書いてあるので，参考にすると良いかも．
- [cmd_line_bot.svg](cmd_line_bot.svg) に依存関係のグラフがある．
  (`pydeps cmd_line_bot` で生成した)

以下は古い情報です．

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

# 動作環境に関する古いメモ
- `python3` (`3.6 >= version >= 3.5`)
    * 一時 `typing.Coroutine` を使っていたので，`3.6` 以上のバージョンが必要だった
    * `Ubuntu 16.04`に`python 3.6`を(ソースからビルドして)インストールする際に，
      `make test`で`test_urllib2net`に失敗した．
      これは，`sudo apt install libssl-dev`することで解決した．
      参考: [Import Error: No module named _ssl](https://stackoverflow.com/questions/5128845/importerror-no-module-named-ssl)
    * `3.7`だと`import discord`中に謎の`SyntaxError`が起きる
- 以下のpythonライブラリが必要．環境によっては`sudo`が必要(`sudo -H`の方が良い場合も？)
    * `discord` (`python3 -m pip install -U discord.py`)
    (`discord.py`公式で`-U`って書いてあったからつけてるけど，本当に必要？)
    * `pytypes`, `pyyaml`, `imgkit`, `pyquery`, `pygments`
    (`python3 -m pip install pytypes pyyaml imgkit pyquery pygments`)
- `python3.7`でも色々とアップデートすれば使えるっぽい
    * `python3 -m pip install -U git+https://github.com/Rapptz/discord.py websockets aiohttp pytypes`



# TODO
## 大事なやつ
- `CLBTask`に`cmdline`を設定していない状態で`send()`中にエラーが起きると，エラーを吐いてbotが死ぬ．
    * botが死ぬのは絶対に避けたいから，`while`ループの中身全体を`try:`で囲っておく？
    * `task.cmdline`は必須属性にする？その場合はデフォルトのcmdlineみたいのがあった方が良いかも？
    * 少なくとも，`task.cmdline`に`None`を代入するよりは`CLBTask_None()`みたいなのを代入した方が色々と良さそう？
- `CLBData`が利用するファイルにて，衝突が起きないようにする
    * 「ユーザー用の設定ファイル」(ReadOnly)と「botが利用する記録ファイル」を分ける
    * singleton にする
    * ファイルのロックとかの機構
- テスト用のフロントエンドへ機能追加
    * `author`を指定したり，`DM`に切り替えたりする機能

## 細かいやつ
- `!init` したときにbackendがエラーを吐くのを修正
    * initした際はバックエンドには渡さない方が良いかも？
    * バックエンドに渡している場合は，「フロントエンドのinitコマンド」をバックエンドが認識している必要があって，
      疎結合性に反する．
    * そもそも`!init`は不要では？(`servername`の設定も`config.json`で行うようにした)
- コマンドのエラーメッセージの調整
  (ルートコマンドなのに「サブコマンド名が不正」と出る)
- `json`から読みとったデータを利用する際は，(特に実行時の)型チェックに気を使った方が良さそう．
  →`@typechecked`を利用する？
- `isinstance`はなるべく排除し，`@typechecked`を利用する．
- `CmdLineBot.run()`で`sleep(10)`してるの，もうちょっとどうにかならない？
- `send_msg`, `send_dm`あたりのコードの整理
- 複数の`msg`,`dm`の並列送信
- `CLBCmd`で引数の個数を自動チェックする機構をつくる
    * とりあえずできた
    * せっかくだから`get_usage`にも反映させる (subcmdを取るかどうかも反映させる)
- AC 通知の際に，部分点のみの取得でも AC 扱いになってしまう．
    * 例: ARC074D 3N Numbers
- (新しい環境で)`!dl`する前に`!show`した際のエラーメッセージが不親切
    * `FileNotFoundError`がそのまま出てきてる
- `wkhtmltopdf`がないときのエラーも不親切
