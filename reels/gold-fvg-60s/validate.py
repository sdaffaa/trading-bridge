import json, re, statistics as st, os
d = json.load(open('trade.json')); B = d['bars']; t = d['trade']; A = d['analysis']; err = []
times = [b[0] for b in B]; I = times.index
for i, (tm, o, h, l, c) in enumerate(B):
    if h < max(o, c) or l > min(o, c): err.append(f'OHLC bad {tm}')
    if i:
        a = int(B[i-1][0][:2])*60+int(B[i-1][0][3:]); b = int(tm[:2])*60+int(tm[3:])
        if (b - a) % 1440 != 15: err.append(f'gap {tm}')
long = t['side'] == 'long'; ei, ti = I(t['entryTime']), I(t['tpTime'])
e = B[ei]
if not (e[3] <= t['entry'] <= e[2]): err.append('entry not touchable')
for b in B[ei:ti+1]:
    if (long and b[3] <= t['stop']) or (not long and b[2] >= t['stop']): err.append(f'SL hit {b[0]}')
for b in B[ei+1:ti]:
    if (long and b[2] >= t['target']) or (not long and b[3] <= t['target']): err.append(f'TP hit early {b[0]}')
if not ((long and B[ti][2] >= t['target']) or (not long and B[ti][3] <= t['target'])): err.append('TP not reached')
# TP must not be touched inside the entry bar after the fill either (entry bar path)
c1, c3 = B[I(A['fvg']['c1'])], B[I(A['fvg']['c3'])]
if long and not c1[2] < c3[3]: err.append('bull FVG invalid')
if not long and not c1[3] > c3[2]: err.append('bear FVG invalid')
top, bot = A['fvg']['top'], A['fvg']['bottom']
if long and (abs(top - c3[3]) > 1e-6 or abs(bot - c1[2]) > 1e-6): err.append('FVG box != real gap')
if not long and (abs(top - c1[3]) > 1e-6 or abs(bot - c3[2]) > 1e-6): err.append('FVG box != real gap')
if not (bot <= t['entry'] <= top): err.append('entry outside FVG')
sw = B[I(A['sweep']['time'])]; lv = A['sweep']['level']; lb = B[I(A['sweep']['levelTime'])]
if long and not (sw[3] < lv and abs(lb[3] - lv) < 1e-6): err.append('sweep invalid')
if not long and not (sw[2] > lv and abs(lb[2] - lv) < 1e-6): err.append('sweep invalid')
if long and not t['stop'] < sw[3]: err.append('stop not beyond sweep')
if not long and not t['stop'] > sw[2]: err.append('stop not beyond sweep')
bo = B[I(A['bos']['time'])]; bl = A['bos']['level']; bb = B[I(A['bos']['levelTime'])]
if long and not (bo[4] > bl and abs(bb[2] - bl) < 1e-6): err.append('BOS invalid')
if not long and not (bo[4] < bl and abs(bb[3] - bl) < 1e-6): err.append('BOS invalid')
R = abs(t['target'] - t['entry']) / abs(t['entry'] - t['stop'])
if R < 3: err.append(f'RR {R:.2f} < 3')
print('bars', len(B), 'RR', round(R, 3), 'target', round(abs(t['target']-t['entry']), 2), 'stop', round(abs(t['entry']-t['stop']), 2))
# geometry from the render probe (output px)
if os.path.exists('probe.json'):
    P = json.load(open('probe.json')); bad = []
    for p in P:
        if p['n'] < 4: continue
        L = p['lens']; med = st.median(L); short = sum(1 for x in L if x < 30) / len(L)
        if p['bodyPx'] < 45 or med < 60 or short > 0.25: bad.append((p['f'], round(p['bodyPx'], 1), round(med, 1), round(short, 2)))
    print('geometry frames checked', len(P), 'violations', len(bad), bad[:10])
    if bad: err.append('candle geometry')
# palette: every hex in the page must be in the identity table
pal = set('FCF9F3 F5EEE5 E4DED8 DDDCD9 CFD6D7 BFC0BC A7A6A2 908F88 777771 A9D0D1 5EA8A9 3F8182 2B6567 1D4D4F 133538 6FD3D2 33B7B7 189EA0 177F82 DFC4A9 D3AE89 BF9367 855E38 164245 11282A 0C1414 323128'.split())
hexes = set(h.upper() for h in re.findall(r'#([0-9A-Fa-f]{6})\b', open('chart.html').read()))
pal.add('000000')  # TradingView markup colour on light pages (tv-chart-replica, Fahad 7 Oct)
if hexes - pal: err.append(f'off-palette {hexes - pal}')
print('ERRORS' if err else 'ALL CHECKS PASS', err)
