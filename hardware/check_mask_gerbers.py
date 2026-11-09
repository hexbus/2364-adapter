"""Verify actual Gerber mask apertures against the adapter's solderable pads."""
from pathlib import Path
import json
import re
import sys

NAME = '68764-to-28pin'

def verify(folder):
    folder = Path(folder)
    through = {(round(x, 6), round(y + n * 2.54, 6)): ('R' if n == 0 and x in (50, 53.81) else 'C', 1.6, 1.6)
               for x, y, count in [(50, 50, 14), (65.24, 50, 14), (53.81, 52.54, 12), (69.05, 52.54, 12)]
               for n in range(count)}
    smd = {(56.35, 50): ('R', 1., 1.5), (57.65, 50): ('R', 1., 1.5),
           (60.05, 50): ('R', 1.1, 1.5), (61.95, 50): ('R', 1.1, 1.5)}
    result = {}
    for suffix, expected in [('-F_Mask.gts', through | smd), ('-B_Mask.gbs', through)]:
        source = (folder / (NAME + suffix)).read_text()
        assert '%FSLAX46Y46*%' in source and '%MOMM*%' in source
        apertures, actual, active = {}, {}, None
        for line in source.splitlines():
            m = re.fullmatch(r'%ADD(\d+)([CR]),([\d.]+)(?:X([\d.]+))?\*%', line)
            if m:
                number, shape, width, height = m.groups()
                apertures[int(number)] = (shape, float(width), float(height or width))
            m = re.fullmatch(r'D(\d+)\*', line)
            if m:
                active = int(m[1])
            m = re.fullmatch(r'X(-?\d+)Y(-?\d+)D03\*', line)
            if m:
                xy = (round(int(m[1]) / 1e6, 6), round(-int(m[2]) / 1e6, 6))
                assert xy not in actual, ('duplicate opening', suffix, xy)
                actual[xy] = apertures[active]
        assert actual == expected, (suffix, 'missing', sorted(expected.keys() - actual.keys()),
                                    'unexpected', sorted(actual.keys() - expected.keys()),
                                    'wrong dimensions', [p for p in actual.keys() & expected.keys() if actual[p] != expected[p]])
        result[suffix] = len(actual)
    return {'result': 'PASS', 'through_hole_openings_each_side': 52,
            'top_smd_openings': 4, 'mask_flashes': result}

if __name__ == '__main__':
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / 'rev-a/fabrication'
    report = verify(folder)
    (folder.parent / 'mask-gerber-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
