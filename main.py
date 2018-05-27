#!/usr/bin/python3

from discord import Client
from sjlib.sjerror import SJError
from sjlib.sjcmd import manage_msg, reply_to_msg
from sjlib.sjconfig import config
from sjlib.sjutil import add_wkhtmltoimage_to_path, add_xvfb_to_path
import os

# Windowsでのpathの設定
if os.name == "nt":
    add_wkhtmltoimage_to_path()
    add_xvfb_to_path()

config.load_default()
config.load(noerror=True)
config.load_auto()
client = Client()
config.set_client(client)

@client.event
async def on_ready():
    global config
    # ログイン情報
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("-------")
    # 拠点サーバーの情報
    set_server_success = config.set_server_byname()
    if set_server_success:
        print("サーバー: %s" % config.get_servername())
        set_channel_success = config.set_channel_byname()
        if set_channel_success:
            await client.send_message(config.get_channel(), "このサーバーを拠点にして，スマブラ人狼を開始します")
            await config.send_data_to_client()
        else:
            print("チャンネルの初期化に失敗しました．config/config.jsonのチャンネル名が間違ってるかも？")
    else:
        print("サーバーの初期化に失敗しました．サーバーのテキストチャンネルで!initして下さい")

@client.event
async def on_message(msg):
    try:
        await manage_msg(msg)
    except SJError as e:
        await reply_to_msg(e.get_msg_to_discord(), msg)
        raise e
    except Exception as e:
        import traceback
        await reply_to_msg(traceback.format_exc(), msg)
        raise e




if __name__ == '__main__':
    client.run(config.get_bot_token())
