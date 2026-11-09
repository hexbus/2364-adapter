"""Independent datasheet-to-CAD audit; does not import generator mappings."""
from pathlib import Path
import csv, json, hashlib
import pcbnew as k
HERE=Path(__file__).resolve().parent
OUT=HERE/'rev-a'; NAME='68764-to-28pin'
# Independently transcribed host-pin -> replacement-pin correspondence.
# Motorola MCM68764 p1, Microchip DS20006432B p5, ST M27C64A pinout.
EXPECTED={1:[3],2:[4],3:[5],4:[6],5:[7],6:[8],7:[9],8:[10],9:[11],10:[12],11:[13],12:[14],13:[15],14:[16],15:[17],16:[18],17:[19],18:[23],19:[21],20:[20,22],21:[2],22:[24],23:[25],24:[27,28]}
SIGNALS=['A7','A6','A5','A4','A3','A2','A1','A0','D0','D1','D2','GND','D3','D4','D5','D6','D7','A11','A10','/SELECT','A12','A9','A8','+5V']
b=k.LoadBoard(str(OUT/(NAME+'.kicad_pcb')))
fs={f.GetReference():f for f in b.GetFootprints()}
ps={r:{int(p.GetNumber()):p for p in f.Pads()} for r,f in fs.items()}
assert set(fs)=={'J1','U1','C1','JP1'}
def net(r,i):return ps[r][i].GetNetCode()
for j,us in EXPECTED.items():
 actual=sorted(i for i,p in ps['U1'].items() if p.GetNetCode()==net('J1',j))
 assert actual==us,(j,actual,us)
assert net('JP1',1)==net('J1',24)==net('C1',1)
assert net('JP1',2)==net('U1',1)!=net('J1',24)
assert net('C1',2)==net('J1',12)
assert not any(t.GetNetCode()==net('U1',26) for t in b.GetTracks())
# Critical bottom-side numbering, spacing and solder-tail clearance.
for ref,count in [('J1',24),('U1',28)]:
 assert fs[ref].GetLayer()==(k.B_Cu if ref=='J1' else k.F_Cu)
 origin=ps[ref][1].GetPosition()
 for i,p in ps[ref].items():
  expected_x=0 if i<=count//2 else 15.24
  expected_y=(i-1 if i<=count//2 else count-i)*2.54
  assert abs(k.ToMM(p.GetPosition().x-origin.x)-expected_x)<.00001
  assert abs(k.ToMM(p.GetPosition().y-origin.y)-expected_y)<.00001
  assert abs(k.ToMM(p.GetDrillSize().x)-.8)<.00001
  assert p.GetLayerSet().Contains(k.F_Mask), (ref,i,'F.Mask missing')
  assert p.GetLayerSet().Contains(k.B_Mask), (ref,i,'B.Mask missing')
edges=[d for d in b.GetDrawings() if d.GetLayer()==k.Edge_Cuts]
xs=[k.ToMM(p.x) for e in edges for p in [e.GetStart(),e.GetEnd()]]
ys=[k.ToMM(p.y) for e in edges for p in [e.GetStart(),e.GetEnd()]]
assert len(edges)==4 and (max(xs)-min(xs),max(ys)-min(ys))==(23,37)
for t in b.GetTracks():
 if not isinstance(t,k.PCB_VIA):assert k.ToMM(t.GetWidth())>=.25
drc=json.loads((OUT/'drc.json').read_text())
assert all(not drc.get(key) for key in ['violations','unconnected_items','schematic_parity'])
erc=json.loads((OUT/'erc.json').read_text())
assert all(not s.get('violations') for s in erc['sheets'])
# Verify address/data permutation and select behavior exhaustively, independently
# of signal labels: all 8192 addresses, 256 data values, and both select levels.
host_addr=[8,7,6,5,4,3,2,1,23,22,19,18,21]
rom_addr=[10,9,8,7,6,5,4,3,25,24,21,23,2]
for a in range(8192):
 values={net('J1',p):(a>>bit)&1 for bit,p in enumerate(host_addr)}
 assert sum(values[net('U1',p)]<<bit for bit,p in enumerate(rom_addr))==a
for data in range(256):
 values={net('U1',p):(data>>bit)&1 for bit,p in enumerate([11,12,13,15,16,17,18,19])}
 assert sum(values[net('J1',p)]<<bit for bit,p in enumerate([9,10,11,13,14,15,16,17]))==data
for select in [0,1]:
 values={net('J1',20):select,net('J1',24):1}
 assert (not values[net('U1',20)] and not values[net('U1',22)])==(select==0)
 assert values[net('U1',27)]==1
with (HERE/'pin-map.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Host_68764_pin','Signal','Replacement_28pin_pins'])
 for j,us in EXPECTED.items():w.writerow([j,SIGNALS[j-1],';'.join(map(str,us))])
report={'result':'PASS','scope':'Datasheet-to-CAD and connectivity checks; not a physical test',
 'dimensions_mm':[23,37],'layers':2,'host_pitch_mm':2.54,'host_row_spacing_mm':15.24,
 'socket_to_rom_pins':EXPECTED,'address_vectors':8192,'data_vectors':256,'select_vectors':2,
 'through_hole_pads_with_both_mask_layers':52,
 'drc_violations':0,'erc_violations':0,'unconnected_items':0,'schematic_parity_issues':0,
 'jp1':'Open for AT28C64B; solder closed for 2764/27C64. U1 pin1 otherwise isolated.',
 'sha256':{ext:hashlib.sha256((OUT/(NAME+ext)).read_bytes()).hexdigest() for ext in ['.kicad_pcb','.kicad_sch','.kicad_pro']}}
(OUT/'independent-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
