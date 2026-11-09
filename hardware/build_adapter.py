"""Generate compact 68764 socket -> AT28C64B / 27C64 read-only adapter.
Run using KiCad 10 Python. Route DSN externally, then run with 'import'.
Pin maps transcribed from Motorola MCM68764 and Microchip DS20006432B.
"""
from pathlib import Path
import json, uuid, sys
import pcbnew as k

HERE=Path(__file__).resolve().parent
OUT=HERE/'rev-a'; OUT.mkdir(exist_ok=True)
LIB=OUT/'Adapter.pretty'; LIB.mkdir(exist_ok=True)
NAME='68764-to-28pin'
plugin=k.PCB_IO_KICAD_SEXPR()
def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL,'cc40/68764-adapter/a/'+s))
def pt(x,y): return k.VECTOR2I(k.FromMM(x),k.FromMM(y))
HOST=dict(enumerate(['A7','A6','A5','A4','A3','A2','A1','A0','D0','D1','D2','GND','D3','D4','D5','D6','D7','A11','A10','SELECT_N','A12','A9','A8','VCC'],1))
ROM=dict(enumerate(['PIN1','A12','A7','A6','A5','A4','A3','A2','A1','A0','D0','D1','D2','GND','D3','D4','D5','D6','D7','SELECT_N','A10','SELECT_N','A11','A9','A8',None,'VCC','VCC'],1))
PARTS=[dict(ref='J1',value='68764 HOST PLUG - BOTTOM',count=24,nets=HOST,x=53.81,y=52.54,sx=60.96,sy=83.82,bottom=True,fp='DIP24_Male_15.24mm'),
 dict(ref='U1',value='AT28C64B / 27C64 SOCKET',count=28,nets=ROM,x=50,y=50,sx=157.48,sy=83.82,bottom=False,fp='DIP28_SocketStrips_15.24mm'),
 dict(ref='C1',value='100nF',count=2,nets={1:'VCC',2:'GND'},x=61,y=50,sx=60.96,sy=149.86,bottom=False,fp='C_0805'),
 dict(ref='JP1',value='CLOSE FOR 2764 VPP',count=2,nets={1:'VCC',2:'PIN1'},x=57,y=50,sx=157.48,sy=149.86,bottom=False,fp='SolderJumper_Open')]

def shape(owner,a,b,layer,width=.15):
 s=k.PCB_SHAPE(owner) if isinstance(owner,k.FOOTPRINT) else k.PCB_SHAPE()
 s.SetShape(k.SHAPE_T_SEGMENT);s.SetStart(pt(*a));s.SetEnd(pt(*b));s.SetLayer(layer);s.SetWidth(k.FromMM(width));owner.Add(s)
def rect(owner,x0,y0,x1,y1,layer,w=.15):
 for a,b in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]:shape(owner,a,b,layer,w)
def text(b,s,x,y,bottom=False,size=.8):
 size=max(.8,size)
 t=k.PCB_TEXT(b);t.SetText(s);t.SetPosition(pt(x,y));t.SetTextSize(pt(size,size));t.SetTextThickness(k.FromMM(.12));t.SetLayer(k.B_SilkS if bottom else k.F_SilkS);t.SetMirrored(bottom);b.Add(t)

def footprint(p):
 f=k.FOOTPRINT(None); f.SetFPIDAsString('Adapter:'+p['fp']); f.SetReference('REF**');f.SetValue(p['value'])
 f.Value().SetVisible(False);f.Reference().SetVisible(False)
 count=p['count']; dip=count>2
 f.SetAttributes(k.FP_THROUGH_HOLE if dip else k.FP_SMD)
 for i in range(1,count+1):
  pad=k.PAD(f);pad.SetNumber(str(i))
  if dip:
   x=0 if i<=count//2 else 15.24;y=(i-1 if i<=count//2 else count-i)*2.54
   if p['bottom']: y=-y
   pad.SetAttribute(k.PAD_ATTRIB_PTH);pad.SetShape(k.PAD_SHAPE_RECT if i==1 else k.PAD_SHAPE_CIRCLE);pad.SetSize(pt(1.6,1.6));pad.SetDrillSize(pt(.8,.8));ls=k.PAD.PTHMask()
  else:
   x=(-.95 if i==1 else .95) if p['ref']=='C1' else (-.65 if i==1 else .65);y=0
   pad.SetAttribute(k.PAD_ATTRIB_SMD);pad.SetShape(k.PAD_SHAPE_RECT);pad.SetSize(pt(1.1,1.5) if p['ref']=='C1' else pt(1,1.5));ls=k.LSET();ls.AddLayer(k.F_Cu);ls.AddLayer(k.F_Mask)
   if p['ref']=='C1':ls.AddLayer(k.F_Paste)
  pad.SetLayerSet(ls);pad.SetPosition(pt(x,y));f.Add(pad)
 if dip:
  h=(count//2-1)*2.54
  lo,hi=(-h-1.5,1.5) if p['bottom'] else (-1.5,h+1.5)
  for x in [0,15.24]:
   rect(f,x-1.5,lo,x+1.5,hi,k.F_CrtYd,.05)
   rect(f,x-1.25,lo+.25,x+1.25,hi-.25,k.F_Fab,.1)
  # A notch identifies the end but does not cross the opposite-side pads.
  ny=3 if not p['bottom'] else 0
  for a,b in [((5.8,ny-.8),(6.7,ny-.8)),((6.7,ny-.8),(6.7,ny+.2)),((6.7,ny+.2),(8.5,ny+.2)),((8.5,ny+.2),(8.5,ny-.8)),((8.5,ny-.8),(9.4,ny-.8))]:
   if p['bottom']:a=(a[0],-a[1]);b=(b[0],-b[1])
   shape(f,a,b,k.F_SilkS)
 else:
  rect(f,-1.8,-1,1.8,1,k.F_CrtYd,.05)
 plugin.FootprintSave(str(LIB),f)
 # Verify the serialized footprint, not just the in-memory layer assignment.
 saved=plugin.FootprintLoad(str(LIB),p['fp'])
 for pad in saved.Pads():
  assert pad.GetLayerSet().Contains(k.F_Mask), (p['ref'],pad.GetNumber(),'F.Mask missing')
  if dip: assert pad.GetLayerSet().Contains(k.B_Mask), (p['ref'],pad.GetNumber(),'B.Mask missing')

def schematic():
 root=uid('sheet');syms=[];chunks=[]
 for count in [24,28]:
  half=count//2; h=(half+1)*1.27; pins=[]
  for i in range(1,count+1):
   left=i<=half;row=i-1 if left else count-i;y=(half-1)*1.27-row*2.54
   pins.append(f'(pin passive line (at {(-20.32 if left else 20.32)} {y} {(0 if left else 180)}) (length 5.08) (name "P{i}" (effects (font (size 1 1)))) (number "{i}" (effects (font (size 1 1)))))')
  syms.append(f'(symbol "Adapter:DIP{count}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" "J" (at 0 {h+4} 0) (effects (font (size 1.27 1.27)))) (property "Value" "DIP{count}" (at 0 {h+1.5} 0) (effects (font (size 1.27 1.27)))) (symbol "DIP{count}_0_1" (rectangle (start -15.24 {h}) (end 15.24 {-h}) (stroke (width .254) (type default)) (fill (type background)))) (symbol "DIP{count}_1_1" {"".join(pins)}))')
 for sym,graphic,length in [('Cap','(polyline (pts (xy -1.27 -2.54)(xy -1.27 2.54)) (stroke (width .254)(type default))(fill (type none))) (polyline (pts (xy 1.27 -2.54)(xy 1.27 2.54)) (stroke (width .254)(type default))(fill (type none)))',19.05),('Link','(circle (center -2.54 0)(radius .762)(stroke (width .254)(type default))(fill (type none))) (circle (center 2.54 0)(radius .762)(stroke (width .254)(type default))(fill (type none)))',17.78)]:
  pins=''.join(f'(pin passive line (at {x} 0 {angle})(length {length})(name "~" (effects(font(size 1 1))))(number "{i}" (effects(font(size 1 1)))))' for i,x,angle in [(1,-20.32,0),(2,20.32,180)])
  syms.append(f'(symbol "Adapter:{sym}" (pin_names(offset 0))(in_bom yes)(on_board yes)(property "Reference" "X" (at 0 6 0)(effects(font(size 1.27 1.27))))(property "Value" "{sym}" (at 0 4 0)(effects(font(size 1.27 1.27))))(symbol "{sym}_0_1" {graphic})(symbol "{sym}_1_1" {pins}))')
 for p in PARTS:
  ref=p['ref'];count=p['count'];half=count//2;x,y=p['sx'],p['sy']
  props=''.join(f'(property "{key}" {json.dumps(value)} (at {x} {yy} 0) (effects (font (size 1.27 1.27)){hide}))' for key,value,yy,hide in [('Reference',ref,y-(half+1)*1.27-7,''),('Value',p['value'],y-(half+1)*1.27-4,''),('Footprint','Adapter:'+p['fp'],y,' (hide yes)')])
  pins=''.join(f'(pin "{i}" (uuid "{uid(ref+str(i))}"))' for i in range(1,count+1))
  sym='Cap' if ref=='C1' else 'Link' if ref=='JP1' else f'DIP{count}'
  chunks.append(f'(symbol (lib_id "Adapter:{sym}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid(ref)}") {props} {pins} (instances (project "{NAME}" (path "/{root}" (reference "{ref}") (unit 1)))))')
  for i in range(1,count+1):
   left=i<=half;px=x+(-20.32 if left else 20.32);py=y-((half-1)*1.27-(i-1 if left else count-i)*2.54)
   if not p['nets'].get(i):chunks.append(f'(no_connect (at {px} {py}) (uuid "{uid(ref+str(i)+"nc")}"))');continue
   lx=px+(-5.08 if left else 5.08)
   chunks.append(f'(wire (pts (xy {px} {py}) (xy {lx} {py})) (stroke (width 0) (type default)) (uuid "{uid(ref+str(i)+"w")}"))')
   chunks.append(f'(label "{p["nets"][i]}" (at {lx} {py} {(0 if left else 180)}) (effects (font (size 1 1)) (justify left bottom)) (uuid "{uid(ref+str(i)+"l")}"))')
 notes=['READ-ONLY ADAPTER. Program U1 separately in a programmer. Never program through J1.', 'JP1 OPEN: AT28C64B (pin 1 NC). JP1 CLOSED: 2764/27C64 (pin 1 VPP at +5V).', 'U1 pins 20 and 22 follow J1 pin 20. U1 pin 27 tied HIGH. U1 pin 26 NC.', 'U1: two 1x14 turned-pin socket strips above. J1: two 1x12 round-pin strips below.', 'Pins shown from top. J1 bottom footprint is intentionally flipped; pin 1 remains at notch end.']
 for i,n in enumerate(notes):chunks.append(f'(text {json.dumps(n)} (at 22.86 {175.26+i*3.81} 0) (effects (font (size 1.05 1.05)) (justify left)) (uuid "{uid("note"+str(i))}"))')
 (OUT/(NAME+'.kicad_sch')).write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{root}") (paper "A4") (title_block (title "68764 to 28-pin ROM adapter") (rev "A") (comment 1 "5V read-only; physical prototype not yet tested")) (lib_symbols {"".join(syms)}) {"".join(chunks)})\n')
 (OUT/'Adapter.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor") '+''.join(syms).replace('"Adapter:','"')+')\n')
 (OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Adapter")(type "KiCad")(uri "${KIPRJMOD}/Adapter.kicad_sym")(options "")(descr "Adapter symbols")))')
 return root

def build():
 for p in PARTS:footprint(p)
 (OUT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Adapter")(type "KiCad")(uri "${KIPRJMOD}/Adapter.pretty")(options "")(descr "Adapter footprints")))')
 root=schematic();b=k.BOARD();b.SetFileName(str(OUT/(NAME+'.kicad_pcb')))
 ds=b.GetDesignSettings();ds.m_MinClearance=k.FromMM(.2);ds.m_CopperEdgeClearance=k.FromMM(.3);ds.m_TrackMinWidth=k.FromMM(.25)
 nc=ds.m_NetSettings.GetDefaultNetclass();nc.SetClearance(k.FromMM(.2));nc.SetTrackWidth(k.FromMM(.25));nc.SetViaDiameter(k.FromMM(.6));nc.SetViaDrill(k.FromMM(.3))
 nets={}
 for n in sorted({n for p in PARTS for n in p['nets'].values() if n}):
  net=k.NETINFO_ITEM(b,'/'+n);b.Add(net);nets[n]=net
 for p in PARTS:
  f=plugin.FootprintLoad(str(LIB),p['fp']);f.SetFPIDAsString('Adapter:'+p['fp']);f.SetReference(p['ref']);f.SetValue(p['value']);f.SetPosition(pt(p['x'],p['y']));b.Add(f)
  if p['bottom']:f.Flip(pt(p['x'],p['y']),True)
  path=k.KIID_PATH();path.push_back(k.KIID(root));path.push_back(k.KIID(uid(p['ref'])));f.SetPath(path)
  for pad in f.Pads():
   n=p['nets'].get(int(pad.GetNumber()))
   if n:pad.SetNet(nets[n])
   else:
    ncnet=k.NETINFO_ITEM(b,f'unconnected-({p["ref"]}-P{pad.GetNumber()}-Pad{pad.GetNumber()})');b.Add(ncnet);pad.SetNet(ncnet)
 rect(b,48,48,71,85,k.Edge_Cuts,.05)
 text(b,'68764\nTO 28PIN',59.5,59,size=.85)
 text(b,'READ ONLY',59.5,62,size=.85)
 text(b,'REV A',59.5,76,size=.8)
 text(b,'U1 NOTCH',59.5,55,size=.8)
 text(b,'JP1',57,48.6,size=.65);text(b,'C1',61,48.6,size=.65)
 text(b,'CLOSE:2764',59.5,64,size=.75)
 text(b,'OPEN:28C64B',59.5,66,size=.75)
 text(b,'1',51.7,50,size=.7);text(b,'1',52.1,52.54,True,size=.7)
 text(b,'hexbus.com\n(c) 2026',59.5,72,True,.8)
 text(b,'J1 TO HOST',59.5,60,True,.85);text(b,'68764 / 2364',59.5,62,True,.8)
 tb=b.GetTitleBlock();tb.SetTitle('68764 to 28-pin read-only adapter');tb.SetRevision('A');tb.SetComment(0,'23 x 37 mm; physical fit and function untested');b.SetTitleBlock(tb)
 (OUT/(NAME+'.kicad_pro')).write_text(json.dumps({'meta':{'filename':NAME+'.kicad_pro','version':1},'net_settings':{'classes':[{'name':'Default','clearance':.2,'track_width':.25,'via_diameter':.6,'via_drill':.3}],'version':4}},indent=2))
 k.SaveBoard(str(OUT/(NAME+'.kicad_pcb')),b);k.ExportSpecctraDSN(b,str(OUT/(NAME+'.dsn')))
 print('Generated',OUT)

if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='import':
  p=OUT/(NAME+'.kicad_pcb');b=k.LoadBoard(str(p));assert k.ImportSpecctraSES(b,str(OUT/(NAME+'.ses')))
  # Router may neck down SMD escapes; keep our specified 0.25 mm minimum.
  for t in b.GetTracks():
   if not isinstance(t,k.PCB_VIA) and t.GetWidth()<k.FromMM(.25):t.SetWidth(k.FromMM(.25))
  k.SaveBoard(str(p),b)
 else:build()
