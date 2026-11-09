"""Check the exact ZIP, exported geometry and original missing-mask regression."""
import json
import sys
import tempfile
import zipfile
from pathlib import Path
from shapely.ops import unary_union
from shapely.geometry import box
from fab_geometry import ROOT, NAME, FAB, ZIP, SUFFIXES, sha, primitives, geometry_hash, shape, drills

sys.path.insert(0,str(ROOT/'hardware'))
from check_mask_gerbers import verify

def main():
    baseline=json.loads((ROOT/'tests/fixtures/corrected-baseline.json').read_text())
    result={'result':'PASS','scope':'CAD/export/package checks; not hardware qualification',
            'zip':ZIP.name,'zip_sha256':sha(ZIP.read_bytes()),'baseline_unchanged':{},'layers':{}}
    expected={NAME+s for s in SUFFIXES}|{'LICENSE','NOTICE','SHA256SUMS.txt'}
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(ZIP) as z:
        assert len(z.namelist())==len(expected) and set(z.namelist())==expected
        assert z.testzip() is None
        manifest={}
        for line in z.read('SHA256SUMS.txt').decode().splitlines():
            digest,name=line.split('  ',1)
            assert name not in manifest and name in expected-{'SHA256SUMS.txt'}
            assert sha(z.read(name))==digest,name
            manifest[name]=digest
        assert set(manifest)==expected-{'SHA256SUMS.txt'}
        # Strictly known basenames only: no archive traversal paths.
        for n in expected:
            data=z.read(n)
            (Path(tmp)/n).write_bytes(data)
            if n.startswith(NAME):assert data==(FAB/n).read_bytes(),n
            elif n in ('LICENSE','NOTICE'):assert data==(ROOT/n).read_bytes(),n
        folder=Path(tmp)
        result['mask']=verify(folder)
        result['plated_component_holes']=len(drills(folder/(NAME+'.drl')))
        assert drills(folder/(NAME+'.drl'))==baseline['drill_positions_mm'] or [list(p) for p in drills(folder/(NAME+'.drl'))]==baseline['drill_positions_mm']
        for suffix,h in baseline['geometry_sha256'].items():
            assert geometry_hash(folder/(NAME+suffix))==h,('unintended geometry change',suffix)
            result['baseline_unchanged'][suffix]=True
        outline=primitives(folder/(NAME+'-Edge_Cuts.gm1'))
        assert len(outline)==4 and all(type(p).__name__=='Line' for p in outline)
        endpoints={tuple(round(v,6) for v in xy) for p in outline for xy in [(p.x1,p.y1),(p.x2,p.y2)]}
        assert endpoints=={(48.,-48.),(71.,-48.),(71.,-85.),(48.,-85.)}
        result['outline_mm']=[23,37]
        boundary=box(48,-85,71,-48)
        for side,cs,ms,ss in [('top','-F_Cu.gtl','-F_Mask.gts','-F_Silkscreen.gto'),('bottom','-B_Cu.gbl','-B_Mask.gbs','-B_Silkscreen.gbo')]:
            cu=primitives(folder/(NAME+cs)); mask=primitives(folder/(NAME+ms)); silk=primitives(folder/(NAME+ss))
            copper=unary_union([shape(p) for p in cu])
            openings=unary_union([shape(p) for p in mask])
            legend=unary_union([shape(p) for p in silk])
            assert openings.difference(copper.buffer(.000002)).area<.00001,'Mask not backed by copper'
            assert boundary.covers(copper) and boundary.covers(openings) and boundary.covers(legend)
            clearance=legend.distance(openings)
            assert clearance>=.1-.000002,('silkscreen clearance',side,clearance)
            result['layers'][side]={'copper_primitives':len(cu),'mask_openings':len(mask),'silkscreen_primitives':len(silk),'minimum_silk_to_mask_mm':round(clearance,6)}
    try:
        verify(ROOT/'tests/fixtures/missing-mask')
    except AssertionError:
        result['missing_mask_regression']='PASS: original defective mask exports rejected'
    else:
        raise AssertionError('Regression: defective mask layers accepted')
    result['paste']='Not delivered: bare-board package only'
    result['physical_tests']='Pending: continuity, fit, soldering, timing and host operation'
    (ROOT/'reports/fabrication-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
