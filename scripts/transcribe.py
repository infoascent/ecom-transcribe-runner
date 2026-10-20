import sys,os,subprocess,hashlib,time
from faster_whisper import WhisperModel
model=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=os.cpu_count())
paths=[l.rstrip("\n") for l in open(sys.argv[1]) if l.strip()]
os.makedirs("out",exist_ok=True)
ok=fail=0
q=dict(stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for p in paths:
    h=hashlib.sha1(p.encode()).hexdigest()[:12]
    rel=p.split("/",2)[2] if p.count("/")>=2 else p.lstrip("/")
    got=False
    for attempt in range(6):
        if os.path.exists("in.mp4"): os.remove("in.mp4")
        subprocess.run(["mega-get",rel,"in.mp4"],**q)
        if os.path.exists("in.mp4") and os.path.getsize("in.mp4")>0: got=True; break
        time.sleep(60*(attempt+1))
    if not got:
        fail+=1; open(f"out/{h}.FAILED","w").write(p); print(f"progress ok={ok} fail={fail}",flush=True); continue
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i","in.mp4","-vn","-ac","1","-ar","16000","in.wav"],**q)
    os.remove("in.mp4")
    segs,_=model.transcribe("in.wav",language="fr",beam_size=1,vad_filter=True)
    with open(f"out/{h}.txt","w") as f:
        f.write(p+"\n\n")
        for s in segs: f.write(f"[{int(s.start//60):02d}:{int(s.start%60):02d}] {s.text.strip()}\n")
    os.remove("in.wav"); ok+=1
    print(f"progress ok={ok} fail={fail}",flush=True)
