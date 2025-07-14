
import json
from collections import defaultdict
from pprint import PrettyPrinter

def analyze_netlist(json_path, module_name='fn', print_details=True):
    j = json.load(open(json_path))
    m = j['modules'][module_name]
    cells = m['cells']
    ports = m['ports']

    net_port = {}
    for pname, pinfo in ports.items():
        for idx, net in enumerate(pinfo['bits']):
            net_port[net] = (pinfo['direction'], f"{pname}[{idx}]")

    net_drv = {}
    net_loads = defaultdict(list)
    for cname, c in cells.items():
        for net in c['connections'].get('Y', []) + c['connections'].get('Q', []):
            net_drv[net] = cname
        for pin in ['A', 'B', 'I']:
            for net in c['connections'].get(pin, []):
                net_loads[net].append(cname)

    for net, (dir, name) in net_port.items():
        if dir == 'input':
            net_drv[net] = None

    depth = {}
    def get_depth(c):
        if c in depth:
            return depth[c]
        ins = []
        for pin in ['A', 'B', 'I']:
            for net in cells[c]['connections'].get(pin, []):
                drv = net_drv.get(net)
                ins.append(get_depth(drv) if drv else 0)
        depth[c] = 1 + max(ins or [0])
        return depth[c]

    for c in cells:
        get_depth(c)

    max_depth = max(depth.values()) if depth else 0
    cols = [[] for _ in range(max_depth + 1)]
    for c, d in depth.items():
        raw_id = int(c.rsplit('$', 1)[-1])
        gate_id = f"g{raw_id}"
        inp = []
        for pin in ['A', 'B', 'I']:
            for net in cells[c]['connections'].get(pin, []):
                if net in net_port and net_port[net][0] == 'input':
                    port_str = net_port[net][1]
                    port_num = ''.join(filter(str.isdigit, port_str))
                    inp.append(f"i{port_num}")
                else:
                    drv = net_drv.get(net)
                    if drv:
                        drv_id = int(drv.rsplit('$', 1)[-1])
                        inp.append(f"g{drv_id}")
                    else:
                        inp.append(None)
        out = []
        for net in sum([cells[c]['connections'].get(pin, []) for pin in ['Y', 'Q']], []):
            if net in net_port and net_port[net][0] == 'output':
                port_str = net_port[net][1]
                port_num = ''.join(filter(str.isdigit, port_str))
                out.append(f"o{port_num}")
            for g in net_loads.get(net, []):
                g_id = int(g.rsplit('$', 1)[-1])
                out.append(f"g{g_id}")
        cols[d].append({'id': gate_id, 'inputs': inp, 'outputs': out})

    input_nodes = []
    output_nodes = []
    input_to_gates = {}
    output_from_gates = {}
    for pname, pinfo in ports.items():
        if pinfo['direction'] == 'input':
            for idx, net in enumerate(pinfo['bits']):
                port_id = f"i{idx}"
                driven_gates = set()
                for g in net_loads.get(net, []):
                    g_id = int(g.rsplit('$', 1)[-1])
                    driven_gates.add(f"g{g_id}")
                input_to_gates[port_id] = sorted(driven_gates)
        elif pinfo['direction'] == 'output':
            for idx, net in enumerate(pinfo['bits']):
                port_id = f"o{idx}"
                driving_gates = set()
                drv = net_drv.get(net)
                if drv:
                    g_id = int(drv.rsplit('$', 1)[-1])
                    driving_gates.add(f"g{g_id}")
                output_from_gates[port_id] = sorted(driving_gates)
    for port_id, outs in input_to_gates.items():
        input_nodes.append({'id': port_id, 'inputs': [], 'outputs': outs})
    for port_id, ins in output_from_gates.items():
        output_nodes.append({'id': port_id, 'inputs': ins, 'outputs': []})
    gate_layers = [gates for gates in cols if gates]
    nonempty_cols = [input_nodes] + gate_layers + [output_nodes]

    if print_details:
        pp = PrettyPrinter(indent=2)
        for depth_level, gates in enumerate(nonempty_cols):
            print(f"Depth {depth_level}:")
            pp.pprint(gates)

    # Summary statistics
    max_inputs = 0
    max_outputs = 0
    for c in cells:
        num_inputs = sum(len(cells[c]['connections'].get(pin, [])) for pin in ['A', 'B', 'I'])
        max_inputs = max(max_inputs, num_inputs)
        num_outputs = sum(len(cells[c]['connections'].get(pin, [])) for pin in ['Y', 'Q'])
        max_outputs = max(max_outputs, num_outputs)
    circuit_inputs = 0
    circuit_outputs = 0
    for pname, pinfo in ports.items():
        if pinfo['direction'] == 'input':
            circuit_inputs += len(pinfo['bits'])
        elif pinfo['direction'] == 'output':
            circuit_outputs += len(pinfo['bits'])
    total_gates = len(cells)
    depth_counts = defaultdict(int)
    for d in depth.values():
        depth_counts[d] += 1
    summary = {
        'max_depth': max_depth,
        'max_inputs_per_gate': max_inputs,
        'max_outputs_per_gate': max_outputs,
        'total_circuit_inputs': circuit_inputs,
        'total_circuit_outputs': circuit_outputs,
        'total_gates': total_gates,
        'gates_by_depth': dict(depth_counts)
    }
    if print_details:
        print("\n" + "="*50)
        print("SUMMARY STATISTICS")
        print("="*50)
        for k, v in summary.items():
            print(f"{k}: {v}")
        print("Returned:")
        print(nonempty_cols)
    return nonempty_cols

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        json_path = '../synthesis/output/fn_nand.json'
        module_name = 'fn'
    elif len(sys.argv) < 2:
        print("Usage: python parse_gates.py [json_path] [module_name]")
        sys.exit(1)
    else:
        json_path = sys.argv[1]
        module_name = sys.argv[2] if len(sys.argv) > 2 else 'fn'
    analyze_netlist(json_path, module_name)
