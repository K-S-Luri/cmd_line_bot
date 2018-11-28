# はじめに
[examples/](../examples/) にある例を元にして解説する．
## 例の実行方法
module `cmd_line_bot` に path を通す必要がある．
例えば

```bash
export PYTHONPATH=/path/to/discord_bot:$PYTHONPATH
```

など．
Windowsでは「システムのプロパティ」から「環境変数」を設定すれば良い(？)

# example1.py
最も簡単な例が [example1.py](../examples/example1.py) にある．

上記のPATHの設定を済ませた上で `python example1.py` で実行すると，
以下のような出力が得られる．

```
ExampleInputFrontEnd starts
[msg to channel your_channel]
first msg

[msg to channel your_channel]
second msg

[msg to channel your_channel]
third msg
```

おおまかな動作の流れは以下の通り．

1. `ExampleInputFrontEnd` が `"first message"` というメッセージを
   backend へと送信する．
2. `ExampleBackEnd` がそのメッセージを受け取り，
   メッセージ中の `"message"` を `"msg"` に置換した上で，
   input frontend へと送信する．
3. `ExampleOutputFrontEnd` がそれを受け取り，
   メタ情報(送信先チャンネル)を付加して端末上に表示する．

# example2.py
次の例 [example2.py](../examples/example2.py) は example1 とほとんど同じだが，
frontend を discord 用のものにつけかえている．

まず，discord 上で bot を利用するために，
以下の手順で準備をする必要がある．

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

## to discord
この状態で `python example2.py` で実行すると，
以下の文字列が discord の general チャンネル上に表示される．

```
-------------------- New Session Start --------------------
first msg
second msg
third msg
```

input frontend と backend は example1 のものをそのまま使いつつ，
output frontend だけを変更することで出力先を discord に変えている．

## from discord
次に， `example2.py` の最後数行を次のように変更する．

```python
if __name__ == '__main__':
    # example2_to_discord()
    example2_from_discord()
```

この例は，先程とは逆に
output frontend と backend は example1 のものをそのまま使いつつ，
input frontend だけを変更したものになっている．

この状態で実行すると，

```
logged in as
[name] (botアカウントの名前)
[ id ] (botアカウントのid)
------
```

と表示される．
その後に discord 上で別の(botではない)アカウントからテキストチャットを投稿すると，
(example1 と同様に) `ExampleBackEnd` において `"message"` が `"msg"` に置換された上で，
端末上にそのメッセージが表示される．


# TODO
- `create_reply_task`
- `CmdArgBackEnd`
