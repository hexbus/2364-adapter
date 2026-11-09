"""Geometry shared by the fabrication audit and ZIP-based preview renderer."""
from pathlib import Path
from dataclasses import asdict
import hashlib
import json
import re
from gerbonara import GerberFile
from shapely.geometry import Point, LineString, box

ROOT = Path(__file__).resolve().parents[1]
NAME = '68764-to-28pin'
EDITION = '2364-adapter-rev-a-credit-20261109'
FAB = ROOT/'hardware/rev-a/fabrication'
ZIP = ROOT/'fabrication'/f'{EDITION}-gerbers.zip'
SUFFIXES = ['-F_Cu.gtl','-B_Cu.gbl','-F_Mask.gts','-B_Mask.gbs',
            '-F_Silkscreen.gto','-B_Silkscreen.gbo','-Edge_Cuts.gm1','.drl','-job.gbrjob']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def primitives(path):
    result = [p for o in GerberFile.open(path).objects for p in o.to_primitives()]
    for p in result:
        assert p.polarity_dark, 'Unsupported clear-polarity geometry'
        assert type(p).__name__ in ('Circle','Rectangle','Line'), type(p)
    return result

def geometry_hash(path):
    rows = []
    for p in primitives(path):
        values = {k:round(v,6) if isinstance(v,float) else v for k,v in asdict(p).items()}
        rows.append(json.dumps([type(p).__name__,values],sort_keys=True))
    return sha('\n'.join(sorted(rows)).encode())

def shape(p):
    kind = type(p).__name__
    if kind == 'Circle':
        return Point(p.x,p.y).buffer(p.r,quad_segs=64)
    if kind == 'Rectangle':
        assert p.rotation == 0
        return box(p.x-p.w/2,p.y-p.h/2,p.x+p.w/2,p.y+p.h/2)
    if kind == 'Line':
        return LineString([(p.x1,p.y1),(p.x2,p.y2)]).buffer(p.width/2,quad_segs=64)
    raise AssertionError(kind)

def drills(path):
    text=Path(path).read_text()
    assert 'METRIC' in text and 'T1C0.800' in text
    assert 'TA.AperFunction,Plated,PTH,ComponentDrill' in text
    assert re.findall(r'^T\d+C[\d.]+$',text,re.M)==['T1C0.800']
    hits=[(round(float(x),6),round(float(y),6)) for x,y in re.findall(r'^X(-?[\d.]+)Y(-?[\d.]+)$',text,re.M)]
    assert len(hits)==len(set(hits))==52
    expected={(round(x,6),round(-(y+n*2.54),6)) for x,y,count in
              [(50,50,14),(65.24,50,14),(53.81,52.54,12),(69.05,52.54,12)] for n in range(count)}
    assert set(hits)==expected, 'Drill coordinates differ from connector pads'
    return sorted(hits)
