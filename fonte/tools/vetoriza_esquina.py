import cv2, numpy as np, json, sys
from skimage.morphology import skeletonize
S='/tmp/claude-0/-home-claude/59fa13e3-e507-5bb5-b839-3d0d73adc740/scratchpad/'
im=cv2.imread('media/obras/esquinas/esquina-06.jpg', cv2.IMREAD_GRAYSCALE)
c=im[362:760, 267:670]
c=cv2.resize(c,(800,790),interpolation=cv2.INTER_CUBIC)
bw=(c<115)
bw[:8,:]=0; bw[-8:,:]=0; bw[:,:8]=0; bw[:,-8:]=0
sk=skeletonize(bw).astype(np.uint8)*255
L=cv2.HoughLinesP(sk,1,np.pi/1440,threshold=35,minLineLength=35,maxLineGap=20).reshape(-1,4).astype(float)
segs=[]
for x1,y1,x2,y2 in L:
    th=np.arctan2(y2-y1,x2-x1)%np.pi
    segs.append([th,x1,y1,x2,y2])
segs=sorted(segs,key=lambda s:-np.hypot(s[3]-s[1],s[4]-s[2]))
def dist_line(p,a,d):
    v=np.array(p)-a; return abs(v[0]*d[1]-v[1]*d[0])
grupos=[]
for th,x1,y1,x2,y2 in segs:
    for g in grupos:
        dth=min(abs(th-g['th']),np.pi-abs(th-g['th']))
        if dth<np.radians(1.2) and dist_line((x1,y1),g["a"],g["d"])<3 and dist_line((x2,y2),g["a"],g["d"])<3:
            g['pts']+= [(x1,y1),(x2,y2)]; break
    else:
        d=np.array([np.cos(th),np.sin(th)])
        grupos.append(dict(th=th,a=np.array([x1,y1]),d=d,pts=[(x1,y1),(x2,y2)]))
out=[]
for g in grupos:
    P=np.array(g['pts']); 
    # refit
    c0=P.mean(0); u,s,vt=np.linalg.svd(P-c0); d=vt[0]
    t=(P-c0)@d; a=c0+d*t.min(); b=c0+d*t.max()
    Ln=np.hypot(*(b-a))
    if Ln<60: continue
    n=np.array([-d[1],d[0]]); ws=[]
    for f in np.linspace(0.1,0.9,15):
        p=a+(b-a)*f; w=0
        for k in range(-10,11):
            q=np.round(p+n*k).astype(int)
            if 0<=q[0]<800 and 0<=q[1]<790 and bw[q[1],q[0]]: w+=1
        ws.append(w)
    out.append(dict(a=a.round(1).tolist(),b=b.round(1).tolist(),w=float(np.median(ws)),L=float(Ln)))
print(len(out), sorted(round(o['w']) for o in out))
json.dump(out,open(S+'e06.json','w'))
vis=np.full((790,800,3),255,np.uint8)
for o in out:
    cv2.line(vis,tuple(map(int,o['a'])),tuple(map(int,o['b'])),(0,0,0),max(1,int(round(o['w']*0.75))))
cv2.imwrite(S+'e06_vet.png',np.hstack([cv2.cvtColor(bw.astype(np.uint8)*255,cv2.COLOR_GRAY2BGR),vis]))
# sobreposição: binário em cinza, vetores em vermelho fino
ov=cv2.cvtColor((255-bw.astype(np.uint8)*120),cv2.COLOR_GRAY2BGR)
for i,o in enumerate(out):
    cv2.line(ov,tuple(map(int,o['a'])),tuple(map(int,o['b'])),(0,0,230),2)
    m=((np.array(o['a'])+np.array(o['b']))/2).astype(int)
    cv2.putText(ov,str(i),tuple(m),cv2.FONT_HERSHEY_SIMPLEX,0.45,(200,0,0),1)
cv2.imwrite(S+'e06_ov.png',ov)
