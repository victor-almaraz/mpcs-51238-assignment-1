import os, subprocess, time, signal, sys
CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
HERE = os.path.dirname(os.path.abspath(__file__))
PROF = HERE + '/chrome-prof'
def shot(url, png, w, h, budget=4000, scale=1):
    if os.path.exists(png): os.remove(png)
    p = subprocess.Popen([CH, '--headless=new', '--user-data-dir=' + PROF, '--no-first-run', '--disable-gpu', '--hide-scrollbars',
                          '--force-device-scale-factor=%s' % scale, '--allow-file-access-from-files', '--force-prefers-reduced-motion',
                          '--virtual-time-budget=%d' % budget, '--window-size=%d,%d' % (w, h), '--screenshot=' + png, url],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    t0 = time.time(); last = -1
    while time.time() - t0 < 60:
        time.sleep(0.4)
        if os.path.exists(png):
            s = os.path.getsize(png)
            if s == last and s > 0: break
            last = s
    try: os.killpg(p.pid, signal.SIGKILL)
    except Exception: pass
    subprocess.run(['pkill', '-9', '-f', 'user-data-dir=' + PROF])
if __name__ == '__main__':
    shot(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
