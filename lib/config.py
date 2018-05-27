from .error import DCError
import json, os, copy, re

# 設定を保持するclass．global変数として利用する．
class DCConfig:
    attrname_jsonkey_list = [("_output_dir", "output_dir"),
                             ("_bot_token", "bot_token"),
                             ("_servername", "servername"),
                             ("_channelname", "channelname"),]
    jsonkeys_to_show = ["servername", "channelname"]
    def __init__(self):
        self._config_dir = "config"
        self._user_config_name = "config"
        self._server = None
        self._servername = None
        self._channel = None
        self._channelname = None
        self._client = None
        self._output_dir = "outputs"
    def to_dict(self):
        data = {}
        for attrname_jsonkey in self.__class__.attrname_jsonkey_list:
            attrname = attrname_jsonkey[0]
            jsonkey = attrname_jsonkey[1]
            data[jsonkey] = getattr(self, attrname)
        return data
    def to_json(self, public=True):
        if public:
            return json.dumps({jsonkey:self.to_dict()[jsonkey] for jsonkey in self.__class__.jsonkeys_to_show},
                              indent=4)
        else:
            return json.dumps(self.to_dict(), indent=4)
    async def send_data_to_client(self):
        json_str = self.to_json()
        client = self._client
        try:
            await client.send_message(self.get_channel(), json_str)
        except DCError:
            pass
    def list_config_names(self):
        files_in_config_dir = os.listdir(self._config_dir)
        config_names = []
        for filename in files_in_config_dir:
            if filename.endswith(".json"):
                config_names.append(re.sub("\.json$", "", filename))
        return config_names
    def save(self, name):
        data = self.to_dict()
        with open(self.get_config_file_path(name), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    def merge_config(self, config_file, data):
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                data_in_file = json.load(f)
        else:
            data_in_file = {}
        for key in data.keys():
            data_in_file[key] = data[key]
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(data_in_file, f, indent=4)
    def save_server_channel(self):
        config_file = self.get_config_file_path(self._user_config_name)
        data = {}
        for key in ["servername", "channelname"]:
            data[key] = self.to_dict()[key]
        self.merge_config(config_file, data)
    def _load(self, config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for attrname_jsonkey in self.__class__.attrname_jsonkey_list:
            attrname = attrname_jsonkey[0]
            jsonkey = attrname_jsonkey[1]
            if jsonkey not in data.keys():
                continue
            setattr(self, attrname, data[jsonkey])
        print("%sを読み込みました" % config_file)
        return True
    def load(self, name=None, noerror=False):
        """設定ファイルを読み込む．"""
        if name is None:
            name = self._user_config_name
        config_file = self.get_config_file_path(name)
        if not os.path.exists(config_file):
            # config_file = self._default_config_file
            if not noerror:
                raise DCError("設定ファイル%sが見つかりません" % config_file)
            else:
                return False
        self._load(config_file)
        return True
    def get_config_file_path(self, name):
        if not os.path.exists(self._config_dir):
            os.makedirs(self._config_dir)
        return os.path.join(self._config_dir,
                            name+".json")
    def get_user_config_file(self):
        return self.get_config_file_path(self._user_config_name)
    def get_output_dir(self):
        if not os.path.exists(self._output_dir):
            os.mkdir(self._output_dir)
        return self._output_dir
    def get_client(self):
        return self._client
    def set_client(self, client):
        self._client = client
    def get_bot_token(self):
        return self._bot_token
    def set_server_byname(self):
        if (self._servername is None) or (self._client is None):
            return False
        servers = self._client.servers
        for server in servers:
            if self._servername == server.name:
                self.set_server(server)
                return True
        return False
    def set_server(self, server):
        if server is None:
            raise DCError("!init はDMじゃなくてテキストチャットに送って")
        self._server = server
        self._servername = server.name
    def set_channel_byname(self):
        if (self._channelname is None) or (self._server is None):
            return False
        channels = self._server.channels
        for channel in channels:
            if self._channelname == channel.name:
                self.set_channel(channel)
                return True
        return False
    def set_channel(self, channel):
        self._channel = channel
        self._channelname = channel.name
    def get_server(self):
        if self._server is None:
            raise DCError("サーバー未設定だよ(!initして)")
        else:
            return self._server
    def get_servername(self):
        return self._servername
    def get_channel(self):
        if self._channel is None:
            raise DCError("チャンネル未設定だよ(!initして)")
        else:
            return self._channel

# global変数
config = DCConfig()
