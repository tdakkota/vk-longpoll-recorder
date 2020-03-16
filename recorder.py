import json
import os
import sys

import fire
import requests


class VkException(Exception):
    pass


class LongPollException(VkException):
    pass


class LongPoll:
    def __init__(
            self,
            token: str,
            api_version: str = "5.103",
            version: int = 10,
            mode: int = 128,
            wait: int = 25,
            ts: int = 0
    ):
        self.token = token
        self.api_version = api_version
        self.version = version
        self.mode = mode
        self.wait = wait

        self._server = ""
        self._key = ""
        self._ts = ts

    def _get_server(self, endpoint_template: str = "https://api.vk.com/method/{0}"):
        r = requests.get(
            endpoint_template.format("messages.getLongPollServer"),
            params={"lp_version": self.version, "access_token": self.token, "v": self.api_version}
        ).json()

        if "error" in r:
            raise VkException(r["error"]["error_msg"])
        return r.get("response", {})

    def _update_server(self, update_ts: bool):
        response = self._get_server()
        if update_ts:
            self._ts = response["ts"]

        self._key = response["key"]
        self._server = response["server"]

    def _build_url(self) -> str:
        return f"https://{self._server}?act=a_check&key={self._key}&ts={self._ts}" \
               f"&wait={self.wait}&mode={self.mode}&version={self.version}"

    def _poll(self):
        response = requests.get(self._build_url()).json()

        code = response.get("failed", 0)
        if code == 0:
            self._ts = response["ts"]
        elif code == 1:
            self._ts = response["ts"]
            return None
        elif code == 2:
            self._update_server(False)
        elif code == 3:
            self._update_server(True)
        elif code == 4:
            raise LongPollException("not valid LongPoll version")
        else:
            raise LongPollException("invalid code %d" % code)

        return response

    def _loop(self):
        self._update_server(self._ts == 0)
        while True:
            response = self._poll()
            if response:
                yield response.get("updates", []), response["ts"]

    def run(self):
        for events, ts in self._loop():
            for event in events:
                yield event, ts


def main(
        token: str = "",
        output: str = "output.json",
        api_version: str = "5.103",
        version: int = 10,
        mode: int = 2 + 8 + 64,
        wait: int = 25,
        ts: int = 0
):
    if not token:
        token = os.environ.get("VK_TOKEN")
    if not token:
        print('Set token as environment variable VK_TOKEN or as `--token` parameter')
        sys.exit(1)

    lp = LongPoll(token, api_version, version, mode, wait, ts)

    if output:
        mode = "a" if os.path.exists(output) else "w"
        with open(output, mode=mode, encoding="utf-8") as f:
            for event, ts in lp.run():
                event = json.dumps(event, ensure_ascii=False)
                print(event, ts)
                f.write(f"{event}\n")
                f.flush()
    else:
        for event, ts in lp.run():
            print(event, ts)


if __name__ == "__main__":
    fire.Fire(main)
