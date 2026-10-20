import sys,os,subprocess,hashlib
from faster_whisper import WhisperModel
model=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=os.cpu_count())
paths=[l.rstrip("\n") for l in open(sys.argv[1]) if l.strip()]
os.makedirs("out",exist_ok=True)
for i,p in enumerate(paths):
    h=hashlib.sha1(p.encode()).hexdigest()[:12]
    subprocess.run(["mega-get",p,"in.mp4"],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i","in.mp4","-vn","-ac","1","-ar","16000","in.wav"],check=True)
    os.remove("in.mp4")
    segs,_=model.transcribe("in.wav",language="fr",beam_size=1,vad_filter=True)
    with open(f"out/{h}.txt","w") as f:
        f.write(p+"\n\n")
        for s in segs: f.write(f"[{int(s.start//60):02d}:{int(s.start%60):02d}] {s.text.strip()}\n")
    os.remove("in.wav")
    print(f"done {i+1}/{len(paths)}",flush=True)
