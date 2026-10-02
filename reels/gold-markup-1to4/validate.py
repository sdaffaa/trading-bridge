import json
d=json.load(open('trade.json')); B=d['bars']; t=d['trade']; err=[]
for i,(tm,o,h,l,c) in enumerate(B):
    if h<max(o,c) or l>min(o,c): err.append(f'OHLC bad {tm}')
    if i:
        a=int(B[i-1][0][:2])*60+int(B[i-1][0][3:]); b=int(tm[:2])*60+int(tm[3:])
        if b-a!=15: err.append(f'gap {tm}')
times=[b[0] for b in B]; ei=times.index(t['entryTime']); ti=times.index(t['tpTime'])
e=B[ei]; assert e[3]<=t['entry']<=e[2], 'entry not touchable'
for b in B[ei:ti+1]:
    if b[3]<=t['stop']: err.append(f'SL hit {b[0]}')
for b in B[ei+1:ti]:
    if b[2]>=t['target']: err.append(f'TP hit early {b[0]}')
assert B[ti][2]>=t['target']
rr=(t['target']-t['entry'])/(t['entry']-t['stop'])
acc=d['analysis']['accumulation']; ai,aj=times.index(acc['from']),times.index(acc['to'])
print('bars',len(B),'RR',rr,'target%',round(100*(t['target']-t['entry'])/t['entry'],2),'stop%',round(100*(t['entry']-t['stop'])/t['entry'],2))
print('acc range real:',min(b[3] for b in B[ai:aj+1]),max(b[2] for b in B[ai:aj+1]))
print('ERRORS' if err else 'ALL CHECKS PASS', err)
