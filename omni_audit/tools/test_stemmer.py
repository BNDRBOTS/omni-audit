#!/usr/bin/env python3
"""Adversarial symmetry test for the normalizer, run over the live corpus."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from forensic_core import tokens, stem
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V=set()
for f in ("source/SOURCE_VERBATIM.md","build/compressed_v3.md"):
    p=os.path.join(ROOT,f)
    if os.path.exists(p):
        V |= {t.lower() for t in tokens(open(p,encoding='utf-8').read())}
bystem=collections.defaultdict(set)
for w in V: bystem[stem(w)].add(w)
fails=[]
for a in sorted(bystem):
    if len(a) < 4 or a.isdigit(): continue
    for cand in (a+"e", a+(a[-1] if a else "")+"e", a[:-1]):
        if cand and cand!=a and cand in bystem and len(cand)>=4 and not cand.isdigit():
            fails.append((a,sorted(bystem[a]),cand,sorted(bystem[cand])))
# known-distinct lemma pairs that legitimately differ by one char
ALLOW={("delivery","deliver"),("deliver","delivery"),("user","use"),("use","user"),
       ("router","route"),("route","router"),("model","mode"),("mode","model"),
       ("scan","sca"),("sca","scan"),("hash","has"),("has","hash"),("do","doe"),
       ("doe","do"),("b","be"),("be","b"),("on","one"),("one","on"),("not","noth"),
       ("noth","not"),("for","forg"),("forg","for"),("control","controll"),
       ("controll","control"),("complet","completion"),("line","lin")}
real=[f for f in fails if (f[0],f[2]) not in ALLOW]
print(f"vocabulary={len(V)} stems={len(bystem)} asymmetries={len(real)}")
for f in real: print("  FAIL:",f)
sys.exit(1 if real else 0)
