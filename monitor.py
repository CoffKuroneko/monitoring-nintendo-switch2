import subprocess
from datetime import datetime
import time
import re
import os

TARGETS = {
    "router": os.environ.get("ROUTER_IP"),
    "switch2": os.environ.get("SWITCH2_IP"),
    "google_dns": "8.8.8.8",
    "cloudflare_dns": "1.1.1.1",
}


LOG_FILE = "ping.log"
packet_lost = False

while True:
    for name, ip in TARGETS.items():
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
    
        #matchは文字列なので、floatに変換してping_timeに入れる
        if match:
            ping_time = float(match.group(1))


        #result.returncode 0 応答あり, 1 応答なし
        if result.returncode != 0:
            if not packet_lost:
                with open(LOG_FILE, "a") as f:
                    f.write(f"{now}\n")
                    f.write(f"{name}\n")
                    f.write("パケットロス検知\n")
                    f.write("\n")

            packet_lost = True

        elif ping_time > 100:
            with open(LOG_FILE, "a") as f:
                f.write(f"{now}\n")
                f.write(result.stdout)
                f.write("\n")
            
            packet_lost = False
        else:
            packet_lost = False
        

        time.sleep(1)