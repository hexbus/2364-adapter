"""Package checked exports with the designer's license and exact hashes."""
import json
import sys
import zipfile
from fab_geometry import ROOT, NAME, FAB, ZIP, SUFFIXES, sha

sys.path.insert(0,str(ROOT/'hardware'))
from check_mask_gerbers import verify

def main():
    rev=ROOT/'hardware/rev-a'
    audit=json.loads((rev/'independent-audit.json').read_text())
    assert audit['result']=='PASS'
    for ext,digest in audit['sha256'].items():
        assert sha((rev/(NAME+ext)).read_bytes())==digest, 'CAD changed after audit'
    verify(FAB)
    files={NAME+s:(FAB/(NAME+s)).read_bytes() for s in SUFFIXES}
    files.update({n:(ROOT/n).read_bytes() for n in ['LICENSE','NOTICE']})
    files['SHA256SUMS.txt']=''.join(f'{sha(data)}  {n}\n' for n,data in sorted(files.items())).encode()
    ZIP.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED) as z:
        for n,data in sorted(files.items()):
            info=zipfile.ZipInfo(n,(2026,11,9,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,data)
    with zipfile.ZipFile(ZIP) as z:
        assert z.testzip() is None
        assert set(z.namelist())==set(files)
        for n,data in files.items():assert z.read(n)==data,n
    report={'file':ZIP.relative_to(ROOT).as_posix(),'sha256':sha(ZIP.read_bytes()),
            'bytes':ZIP.stat().st_size,'entries':len(files),
            'contents_sha256':{n:sha(b) for n,b in sorted(files.items())}}
    (ROOT/'reports/package-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Packaged and checked:',ZIP.name)

if __name__=='__main__':main()
