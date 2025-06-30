
import json
from collections import defaultdict
from pprint import PrettyPrinter

j = json.load(open('fn_nand.json'))
m = j['modules']['add1']
cells = m['cells']
ports = m['ports']

net_port = {}
for pname,pinfo in ports.items():
    for idx,net in enumerate(pinfo['bits']):
        net_port[net] = (pinfo['direction'], f"{pname}[{idx}]")

net_drv = {}
net_loads = defaultdict(list)
for cname,c in cells.items():
    for net in c['connections'].get('Y',[])+c['connections'].get('Q',[]):
        net_drv[net] = cname
    for pin in ['A','B','I']:
        for net in c['connections'].get(pin,[]):
            net_loads[net].append(cname)

for net,(dir,name) in net_port.items():
    if dir=='input':
        net_drv[net] = None

depth = {}
def get_depth(c):
    if c in depth: return depth[c]
    ins = []
    for pin in ['A','B','I']:
        for net in cells[c]['connections'].get(pin,[]):
            drv = net_drv.get(net)
            ins.append(get_depth(drv) if drv else 0)
    depth[c] = 1 + max(ins or [0])
    return depth[c]

for c in cells:
    get_depth(c)

cols = defaultdict(list)
for c,d in depth.items():
    raw_id = int(c.rsplit('$',1)[-1])
    inp = []
    for pin in ['A','B','I']:
        for net in cells[c]['connections'].get(pin,[]):
            if net in net_port and net_port[net][0]=='input':
                inp.append(net_port[net][1])
            else:
                drv = net_drv.get(net)
                inp.append(int(drv.rsplit('$',1)[-1]) if drv else None)
    out = []
    for net in sum([cells[c]['connections'].get(pin,[]) for pin in ['Y','Q']], []):
        if net in net_port and net_port[net][0]=='output':
            out.append(net_port[net][1])
        else:
            for g in net_loads.get(net,[]):
                out.append(int(g.rsplit('$',1)[-1]))
    cols[d].append({'id': raw_id, 'inputs': inp, 'outputs': out})

pp = PrettyPrinter(indent=2)
for depth in sorted(cols):
    print(f"Depth {depth}:")
    pp.pprint(cols[depth])
