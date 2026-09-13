import subprocess
from datetime import datetime
import time
import re
import os

SWITCH2_FAIL_THRESHOLD = 3
PING_DELAY_THRESHOLD = 1

TARGETS = {
    "router": os.environ.get("ROUTER_IP"),
    "switch2": os.environ.get("SWITCH2_IP"),
    "google_dns": "8.8.8.8",
    "cloudflare_dns": "1.1.1.1",
}

packet_lost = {name: False for name in TARGETS}

LOG_FILE = "ping.log"
switch2_online = True
switch2_fail_count = 0

while True:
    for name, ip in TARGETS.items():

        # Switch2がofflineなら、Switch2以外は監視しない
        if not switch2_online and name != "switch2":
            continue

        result = subprocess.run(
            ["ping", "-c", "1", ip],
            capture_output=True, #コマンドの出力をPython側で受け取るための指定
            text=True #受け取った出力を文字列（str）として扱う指定
        )
        print(name, ip, result.returncode)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #正規表現
        #\d → 数字
        #. → 小数点も許可
        #+ → 1文字以上続く
        match = re.search(r"time=([\d.]+)", result.stdout)

        ping_time = None

        #matchは文字列なので、floatに変換してping_timeに入れる
        if match:
            ping_time = float(match.group(1))


        if name == "switch2":
            if result.returncode != 0:
                if switch2_fail_count < SWITCH2_FAIL_THRESHOLD:
                    switch2_fail_count += 1
                elif switch2_fail_count >= SWITCH2_FAIL_THRESHOLD:
                    switch2_online = False

            elif result.returncode == 0:
                switch2_fail_count = 0
                switch2_online = True
            

        #result.returncode 0 応答あり, 1 応答なし
        if switch2_online:
            if result.returncode != 0:
                if not packet_lost[name]:
                    with open(LOG_FILE, "a") as f:
                        f.write(f"{now}\n")
                        f.write(f"{name}:packet loss\n")
                        f.write("パケットロス検知\n")
                        f.write("\n")

                packet_lost[name] = True

            elif ping_time is not None and ping_time > PING_DELAY_THRESHOLD:
                with open(LOG_FILE, "a") as f:
                    f.write(f"{now}\n")
                    f.write(result.stdout)
                    f.write("\n")
                
                packet_lost[name] = False
            else:
                packet_lost[name] = False
            
        time.sleep(1)