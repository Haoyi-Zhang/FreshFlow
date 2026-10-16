"""Check fresh, self-contained generation of the three consumed vector figures."""
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='freshness-figures-') as tmp:
        out = Path(tmp)
        subprocess.run([sys.executable, '-B', str(HERE/'draw_schematics.py'),
                        '--output', str(out)], check=True, timeout=60)
        for name in ('data-gate', 'row-cover', 'residual'):
            actual = (out/(name+'.pdf')).read_bytes()
            if not actual.startswith(b'%PDF-') or actual != (HERE/(name+'.pdf')).read_bytes():
                raise RuntimeError('Missing, stale or nondeterministic figure: '+name)
    print('All three vector figures regenerate exactly and pass label bounds checks.')
