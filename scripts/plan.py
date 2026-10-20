import re,sys,json
# reads `mega-find / --type=f -l` output on stdin, prints JSON list of shards (paths only)
N=int(sys.argv[1]); shard=int(sys.argv[2])
skip=re.compile(r'(Partie 5 - |Partie 14 - |Partie 17 - |\.DS_Store)')
items=[]
for line in sys.stdin:
    m=re.match(r'^(.*\.mp4) \(([\d.]+) (KB|MB|GB)\)\s*$',line.strip())
    if not m or skip.search(m.group(1)): continue
    size=float(m.group(2))*{'KB':1e-3,'MB':1,'GB':1e3}[m.group(3)]
    items.append((size,m.group(1)))
items.sort(key=lambda x:(-x[0],x[1]))
bins=[[0,[]] for _ in range(N)]
for size,p in items:
    b=min(bins,key=lambda b:b[0]); b[0]+=size; b[1].append(p)
print("\n".join(bins[shard][1]))
