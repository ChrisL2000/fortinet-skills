import importlib, sys, os
print('python', sys.version.split()[0])
for mod in ('chromadb', 'sentence_transformers', 'trafilatura', 'fitz', 'bs4', 'requests'):
    try:
        m = importlib.import_module(mod)
        print(mod, 'OK', getattr(m, '__version__', '?'))
    except Exception as e:
        print(mod, 'MISSING', str(e)[:100])
for p in ('/root/.cache/torch', '/root/.cache/huggingface', '/root/.cache/sentence_transformers', '/rag'):
    print(p, os.path.exists(p))
print('nproc', os.cpu_count())
try:
    with open('/proc/meminfo') as f:
        print([l.split()[1:3] for l in f if l.startswith('MemAvailable')])
except Exception as e:
    print('meminfo fail', e)
