import os, re, subprocess, time
PKG = os.environ.get("PKG", "com.paradox.dscm")
APK_URL = os.environ["APK_URL"]
API = os.environ.get("API", "")
SESSION_MINUTES = 300
CHECK_EVERY = 10
def run(cmd):
    print("+", cmd, flush=True)
    return subprocess.run(cmd, shell=True)
def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
def write(name, text):
    with open(os.path.join("output", name), "a") as f:
        f.write(str(text) + "\n")
def shot(name):
    run("adb exec-out screencap -p > output/" + name)
def dump_ui(name):
    run("adb shell uiautomator dump /sdcard/dump.xml")
    run("adb pull /sdcard/dump.xml output/" + name)
    try:
        return open(os.path.join("output", name)).read()
    except Exception:
        return ""
def find_tap(xml, pattern):
    m = re.search(r'(?:content-desc|text)="[^"]*' + pattern + r'[^"]*"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    if not m:
        return None
    return ((int(m.group(1)) + int(m.group(3))) // 2, (int(m.group(2)) + int(m.group(4))) // 2)
def tap(x, y):
    run("adb shell input tap %d %d" % (x, y))
os.makedirs("output", exist_ok=True)
write("session-log.txt", "START fixed: 20 emulators, session_minutes=300 check_every=10 LABEL=%s API=%s" % (os.environ.get("LABEL",""), API))
run("curl -L '" + APK_URL + "' -o app.apk")
write("install.txt", sh("ls -l app.apk"))
write("install.txt", sh("adb install -r app.apk"))
run("adb shell monkey -p " + PKG + " -c android.intent.category.LAUNCHER 1")
time.sleep(30)
shot("02-app.png")
xml = dump_ui("dump_last.xml")
t = find_tap(xml, "Continue as guest")
if t:
    tap(*t); write("session-log.txt", "TAP Continue as guest %s" % (t,))
else:
    size = sh("adb shell wm size"); m = re.search(r"(\d+)x(\d+)", size)
    w, h = (int(m.group(1)), int(m.group(2))) if m else (1080, 2400)
    tap(w // 2, int(h * 0.71)); write("session-log.txt", "TAP Continue as guest fallback")
time.sleep(6); shot("03-after-guest.png")
player_name = "Tester" + (API if API else "1")
run('adb shell input text "%s"' % player_name)
time.sleep(2)
xml = dump_ui("dump_name.xml"); t = find_tap(xml, "Start playing")
if t:
    tap(*t); write("session-log.txt", "TAP Start playing %s" % (t,))
else:
    write("session-log.txt", "Start playing NOT FOUND")
time.sleep(8)
xml = dump_ui("dump_notif.xml"); t = find_tap(xml, "Decline")
if t:
    tap(*t); write("session-log.txt", "TAP Decline notifications %s" % (t,)); time.sleep(5)
else:
    write("session-log.txt", "Decline notifications NOT FOUND")
shot("04-lobby.png")
xml = dump_ui("dump_game.xml"); done=False
for name in ["Carrom", "Chess", "Ludo", "Dominoes", "Snakes"]:
    t = find_tap(xml, name)
    if t:
        tap(*t); write("session-log.txt", "GAME TAP %s %s" % (name, t)); done=True; break
if not done:
    write("session-log.txt", "GAME TAP none-found, swipe up"); run("adb shell input swipe 500 1500 500 700 300")
time.sleep(8); shot("05-game.png")
start=time.time(); end=start+SESSION_MINUTES*60; i=0
while time.time() < end:
    time.sleep(CHECK_EVERY*60); i+=1
    alive = bool(sh("adb shell pidof " + PKG).strip())
    if alive:
        write("session-log.txt", "check %d ALIVE elapsed_min=%d" % (i, int((time.time()-start)//60)))
    else:
        write("session-log.txt", "check %d DEAD elapsed_min=%d - relaunching" % (i, int((time.time()-start)//60)))
        run("adb shell monkey -p " + PKG + " -c android.intent.category.LAUNCHER 1"); time.sleep(15)
    shot("soak-%02d.png" % i)
write("session-log.txt", "SESSION DONE checks=%d" % i)
run("adb logcat -d > output/logcat.txt"); run("ls -la output")
print("SESSION20 LONG DONE")
