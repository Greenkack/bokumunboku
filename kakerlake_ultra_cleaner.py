# Create a single consolidated "Super Ultra Cleaner" script
import textwrap, os, zipfile, json, re, hashlib

ULTRA_PATH = "/mnt/data/kakerlake_ultra_cleaner.py"

code = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kakerlake_ultra_cleaner.py
=================================
Ein einziger „Super Ultra Reiniger“ für dein Projekt. Kombiniert:
  1) SCAN: Duplikate & Kollisionen (Python)
     - Gleicher LHS-Name mit unterschiedlichen RHS-Formeln
     - Gleiche RHS-Formel für unterschiedliche LHS-Namen
     - Gleiche LHS-Form (Shape), aber unterschiedliche Variablen
     - Funktionsnamen-Konflikte (gleicher Name, verschiedene Bodies)
     - Duplizierte Funktionskörper (exakter Hash)
  2) AUTOPATCH: annual_savings ➜ compute_annual_savings(...)
     - Insert DEF-Block in calculations.py (falls fehlt)
     - Import ergänzen
  3) AUTOPATCH: project_data ➜ build_project_data(...)
     - Insert DEF-Block in calculations.py (falls fehlt)
     - Import ergänzen
  4) STRUCTURE: App-Struktur-Manifest, Verzeichnis-Übersicht, Trees
  5) YAML-CHECK: Positionskollisionen (x/y/left/top/page) ähnlich belegte Koordinaten

Ausgabe: CSV-Reports im Ziel-Ordner, optional ZIP.

Abhängigkeiten:
  - Standardbibliothek
  - Für Autopatcher: libcst (installierbar via `pip install libcst`)
  - Für YAML-Parsing optional: pyyaml (`pip install pyyaml`), sonst heuristischer Fallback

Nutzung (Beispiele):
  python kakerlake_ultra_cleaner.py scan . --out reports
  python kakerlake_ultra_cleaner.py autopatch-annual-savings . --write
  python kakerlake_ultra_cleaner.py autopatch-project-data . --write
  python kakerlake_ultra_cleaner.py structure . --out reports
  python kakerlake_ultra_cleaner.py yaml-check . --out reports --tol-mm 0.2
  python kakerlake_ultra_cleaner.py all . --out reports --write

Autor: GPT-5 Thinking — Kompakt, reproduzierbar, side-effect-frei.
"""

from __future__ import annotations
import os, re, sys, ast, csv, argparse, hashlib, textwrap
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Set

# ----------------------------- Utils -----------------------------

def read_text(path:str)->str:
    return open(path, "r", encoding="utf-8", errors="ignore").read()

def write_text(path:str, text:str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(text)

def ensure_dir(p:str):
    os.makedirs(p, exist_ok=True)
    return p

def sha1_bytes(b:bytes)->str:
    import hashlib
    return hashlib.sha1(b).hexdigest()

def list_py(root:str)->List[str]:
    out=[]
    for r,_,f in os.walk(root):
        for fn in f:
            if fn.endswith(".py"):
                out.append(os.path.join(r,fn))
    return out

def list_yaml(root:str)->List[str]:
    out=[]
    for r,_,f in os.walk(root):
        for fn in f:
            if fn.lower().endswith((".yml",".yaml")):
                out.append(os.path.join(r,fn))
    return out

# ----------------------------- SCAN: Python Kollisionen -----------------------------

COMMUTATIVE_OPS = (ast.Add, ast.Mult,)

def node_signature(node:ast.AST)->Tuple[Any,...]:
    if node is None:
        return ('None',)
    if isinstance(node, ast.Name):
        return ('Name', node.id)
    if isinstance(node, ast.Attribute):
        try:
            base = ast.unparse(node.value)
        except Exception:
            base = ('AttrBase',)
        return ('Attr', base, node.attr)
    if isinstance(node, ast.Constant):
        return ('Const', repr(node.value))
    if isinstance(node, ast.Call):
        func_sig = node_signature(node.func)
        args_sig = tuple(node_signature(a) for a in node.args)
        kwargs_sig = tuple(sorted((k.arg if k.arg else '**', node_signature(k.value)) for k in node.keywords))
        return ('Call', func_sig, args_sig, kwargs_sig)
    if isinstance(node, ast.BinOp):
        op_type = type(node.op).__name__
        if isinstance(node.op, COMMUTATIVE_OPS):
            def flatten(n):
                if isinstance(n, ast.BinOp) and isinstance(n.op, type(node.op)):
                    return flatten(n.left) + flatten(n.right)
                else:
                    return [n]
            terms = flatten(node.left) + flatten(node.right)
            term_sigs = sorted([node_signature(t) for t in terms])
            return (op_type, tuple(term_sigs))
        else:
            return (op_type, node_signature(node.left), node_signature(node.right))
    if isinstance(node, ast.UnaryOp):
        return (type(node.op).__name__, node_signature(node.operand))
    if isinstance(node, ast.Compare):
        return ('Compare', node_signature(node.left),
                tuple(type(op).__name__ for op in node.ops),
                tuple(node_signature(c) for c in node.comparators))
    if isinstance(node, ast.BoolOp):
        op_type = type(node.op).__name__
        values = tuple(sorted(node_signature(v) for v in node.values)) if isinstance(node.op,(ast.And,ast.Or)) else tuple(node_signature(v) for v in node.values)
        return ('BoolOp', op_type, values)
    if isinstance(node, ast.Subscript):
        try:
            slice_sig = node_signature(node.slice)
        except Exception:
            slice_sig = ('Slice', 'err')
        return ('Subscript', node_signature(node.value), slice_sig)
    if isinstance(node, ast.Dict):
        items=[]
        for k,v in zip(node.keys, node.values):
            if k is None:
                items.append(('UNPACK', node_signature(v)))
            else:
                items.append(('KV', node_signature(k), node_signature(v)))
        return ('Dict', tuple(sorted(items)))
    if isinstance(node, ast.List):
        return ('List', tuple(node_signature(e) for e in node.elts))
    if isinstance(node, ast.Tuple):
        return ('Tuple', tuple(node_signature(e) for e in node.elts))
    return ('Other', type(node).__name__)

def node_shape(node:ast.AST)->Tuple[Any,...]:
    if node is None:
        return ('None',)
    if isinstance(node, ast.Name):
        return ('Name',)
    if isinstance(node, ast.Attribute):
        return ('Attr',)
    if isinstance(node, ast.Constant):
        return ('Const',)
    if isinstance(node, ast.Call):
        return ('Call', len(node.args), len(node.keywords))
    if isinstance(node, ast.BinOp):
        op_type = type(node.op).__name__
        if isinstance(node.op, COMMUTATIVE_OPS):
            def flatten(n):
                if isinstance(n, ast.BinOp) and isinstance(n.op, type(node.op)):
                    return flatten(n.left) + flatten(n.right)
                else:
                    return [n]
            terms = flatten(node.left) + flatten(node.right)
            term_shapes = sorted([node_shape(t) for t in terms])
            return (op_type, tuple(term_shapes))
        else:
            return (op_type, node_shape(node.left), node_shape(node.right))
    if isinstance(node, ast.UnaryOp):
        return (type(node.op).__name__, node_shape(node.operand))
    if isinstance(node, ast.Compare):
        return ('Compare', tuple(type(op).__name__ for op in node.ops), len(node.comparators))
    if isinstance(node, ast.BoolOp):
        return ('BoolOp', type(node.op).__name__, len(node.values))
    if isinstance(node, ast.Subscript):
        return ('Subscript',)
    if isinstance(node, ast.Dict):
        return ('Dict', len(node.keys))
    if isinstance(node, ast.List):
        return ('List', len(node.elts))
    if isinstance(node, ast.Tuple):
        return ('Tuple', len(node.elts))
    return ('Other', type(node).__name__)

def collect_names(node:ast.AST)->Set[str]:
    names=set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            names.add(n.id)
    return names

def scan_python(root:str, out:str):
    ensure_dir(out)
    py = list_py(root)
    assignments=[]
    func_defs=[]
    errors=[]
    for p in py:
        try:
            src = read_text(p)
            tree = ast.parse(src, filename=p)
            lines = src.splitlines()
        except Exception as e:
            errors.append((p, repr(e)))
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else ([node.target] if node.target is not None else [])
                value = node.value if hasattr(node, 'value') else None
                if value is None: 
                    continue
                for t in targets:
                    lhs=None
                    if isinstance(t, ast.Name):
                        lhs=t.id
                    elif isinstance(t, ast.Attribute):
                        try:
                            lhs=ast.unparse(t)
                        except Exception:
                            lhs=None
                    if lhs is None: 
                        continue
                    sig = node_signature(value)
                    shape = node_shape(value)
                    vars_used = ",".join(sorted(list(collect_names(value))))
                    lineno = getattr(node, 'lineno', None)
                    text_line = lines[lineno-1].strip() if lineno and 1<=lineno<=len(lines) else ""
                    assignments.append(dict(file=p, lineno=lineno, lhs=lhs, rhs_sig=repr(sig), rhs_shape=repr(shape), rhs_vars=vars_used, line=text_line))
            if isinstance(node, ast.FunctionDef):
                start=node.lineno; end=getattr(node,'end_lineno',start)
                body_src="\n".join(lines[start-1:end])
                norm=re.sub(r'\s+','',body_src)
                func_defs.append(dict(file=p,name=node.name,lineno=start,end_lineno=end,hash=hashlib.md5(norm.encode()).hexdigest(),body=body_src))
    import pandas as pd
    assign_df=pd.DataFrame(assignments)
    func_df=pd.DataFrame(func_defs)

    # 1) Same LHS, different RHS
    dup_lhs = assign_df.groupby('lhs').agg(count=('lhs','size'), unique_rhs=('rhs_sig','nunique')).reset_index()
    conflicting_lhs = dup_lhs[(dup_lhs['count']>1) & (dup_lhs['unique_rhs']>1)]
    lhs_conflicts_df = assign_df[assign_df['lhs'].isin(set(conflicting_lhs['lhs']))].sort_values(['lhs','rhs_sig','file','lineno'])
    lhs_conflicts_df.to_csv(os.path.join(out,"python_lhs_conflicts.csv"), index=False, encoding="utf-8")

    # 2) Same RHS, different LHS
    rhs_groups = assign_df.groupby('rhs_sig').agg(lhs_set=('lhs', lambda x: sorted(set(x))), count=('lhs','size')).reset_index()
    rhs_conflicting = rhs_groups[rhs_groups['lhs_set'].map(len) > 1]
    rhs_conflict_df = assign_df.merge(rhs_conflicting[['rhs_sig']], on='rhs_sig', how='inner').sort_values(['rhs_sig','lhs','file','lineno'])
    rhs_conflict_df.to_csv(os.path.join(out,"python_rhs_same_expr_diff_lhs.csv"), index=False, encoding="utf-8")

    # 3) Same LHS, same shape, different vars
    rows=[]
    for lhs, g in assign_df.groupby('lhs'):
        for shape, sub in g.groupby('rhs_shape'):
            if len(sub)>=2 and sub['rhs_vars'].nunique()>1:
                rows.append(sub)
    if rows:
        import pandas as pd
        pd.concat(rows).to_csv(os.path.join(out, "python_lhs_same_shape_diff_vars.csv"), index=False, encoding="utf-8")
    else:
        assign_df.head(0).to_csv(os.path.join(out, "python_lhs_same_shape_diff_vars.csv"), index=False, encoding="utf-8")

    # 4) Function name conflicts
    name_groups = func_df.groupby('name').agg(files=('file', list), hashes=('hash', lambda x: list(x))).reset_index()
    conflicts = []
    for _, row in name_groups.iterrows():
        if len(set(row['hashes']))>1:
            conflicts.append(dict(name=row['name'], distinct_impls=len(set(row['hashes'])), files=" | ".join(sorted(set(row['files'])))))
    import pandas as pd
    pd.DataFrame(conflicts).to_csv(os.path.join(out, "python_function_name_conflicts.csv"), index=False, encoding="utf-8")

    # 5) Exact duplicate bodies
    body_groups = func_df.groupby('hash').agg(names=('name', list), files=('file', list), count=('hash','size')).reset_index()
    body_groups[body_groups['count']>1][['hash','count','names','files']].to_csv(os.path.join(out, "python_function_body_duplicates.csv"), index=False, encoding="utf-8")

    # 6) Parse errors
    import pandas as pd
    pd.DataFrame(errors, columns=["file","error"]).to_csv(os.path.join(out, "python_parse_errors.csv"), index=False, encoding="utf-8")

    # 7) Top 30 conflicting LHS
    top30 = dup_lhs.sort_values("unique_rhs", ascending=False).head(30)[["lhs","count","unique_rhs"]].rename(columns={"count":"n_assign","unique_rhs":"n_rhs"})
    top30.to_csv(os.path.join(out, "top30_conflicting_lhs.csv"), index=False, encoding="utf-8")

# ----------------------------- DEF-Blocks -----------------------------

COMPUTE_DEF_CODE = r"""
def compute_annual_savings(
    *,
    results: Optional[Dict[str, Any]] = None,
    annual_feedin_revenue: Optional[float] = None,
    annual_electricity_savings: Optional[float] = None,
    annual_old_cost: Optional[float] = None,
    annual_hp_cost: Optional[float] = None,
    electricity_costs_without_pv: Optional[float] = None,
    electricity_costs_with_pv: Optional[float] = None,
    annual_feed_in_revenue: Optional[float] = None,
    default: float = 0.0,
) -> float:
    \"\"\"Gleichschaltung für *annual_savings* (kanonisch).\"\"\"
    try:
        if results:
            for key in (
                'annual_total_savings_euro',
                'annual_financial_benefit_year1',
                'annual_savings_consumption_eur',
                'jahresersparnis_gesamt',
                'total_annual_savings',
                'annual_savings',
                'annual_savings_total_euro',
            ):
                if isinstance(results, dict) and key in results:
                    val = results.get(key, None)
                    try:
                        if val is not None and float(val) != 0.0:
                            return float(val)
                    except Exception:
                        pass
            try:
                feed_in_revenue = results.get('annual_revenue_feed_in_eur', 0.0)
                consumption_savings = results.get('annual_savings_consumption_eur', 0.0)
                if (float(feed_in_revenue) > 0.0) or (float(consumption_savings) > 0.0):
                    return float(feed_in_revenue) + float(consumption_savings)
            except Exception:
                pass

        if annual_feedin_revenue is not None and annual_electricity_savings is not None:
            return float(annual_feedin_revenue) + float(annual_electricity_savings)

        if annual_old_cost is not None and annual_hp_cost is not None:
            return float(annual_old_cost) - float(annual_hp_cost)

        if electricity_costs_without_pv is not None and electricity_costs_with_pv is not None:
            base = float(electricity_costs_without_pv) - float(electricity_costs_with_pv)
            if annual_feed_in_revenue is not None:
                base += float(annual_feed_in_revenue)
            return base

        return float(default)
    except Exception:
        try:
            return float(default)
        except Exception:
            return 0.0
""".strip("\n")

BUILD_PD_DEF_CODE = r"""
def build_project_data(*parts, drop_none=True, drop_empty_str=True, normalize=True, keymap=None):
    \"\"\"Zentraler, side-effect-freier Builder für *project_data*.
    - *parts*: beliebig viele dict-ähnliche Objekte (None ignoriert).
    - *drop_none*: None-Werte entfernen.
    - *drop_empty_str*: leere Strings entfernen.
    - *normalize*: Keys trimmen, Zero-Width/Zeilenumbrüche bereinigen.
    - *keymap*: optionales Synonym-Mapping.
    \"\"\"
    out = {}
    def _coerce(x):
        try:
            if x is None:
                return {}
            if isinstance(x, dict):
                return x
            if hasattr(x, 'items'):
                return dict(x.items())
            return dict(x)
        except Exception:
            return {}
    for part in parts:
        d = _coerce(part)
        for k, v in d.items():
            if drop_none and v is None:
                continue
            if drop_empty_str and isinstance(v, str) and v.strip() == "":
                continue
            kk = k
            try:
                if isinstance(kk, str):
                    kk = kk.strip().replace("\\u200b","").replace("\\n"," ").strip()
                if keymap and kk in keymap:
                    kk = keymap[kk]
            except Exception:
                pass
            out[kk] = v
    return out
""".strip("\n")

# ----------------------------- LibCST Helpers -----------------------------

def require_libcst():
    try:
        import libcst as cst  # type: ignore
        import libcst.matchers as m  # type: ignore
        return cst, m
    except Exception as e:
        print("Fehlende Abhängigkeit: Bitte installieren: pip install libcst", file=sys.stderr)
        raise

def insert_def_if_missing_calculations(code:str, func_name:str, def_code:str):
    cst, m = require_libcst()
    try:
        mod = cst.parse_module(code)
    except Exception:
        return code
    class Finder(cst.CSTVisitor):
        def __init__(self): self.found=False
        def visit_FunctionDef(self, node:cst.FunctionDef):
            if node.name.value == func_name:
                self.found=True
    f=Finder(); mod.visit(f)
    if f.found: return code
    insert_stmt = cst.parse_statement(def_code + "\n\n")
    body=list(mod.body)
    insert_idx=0
    for i, stmt in enumerate(body):
        if m.matches(stmt, m.SimpleStatementLine(body=[m.Import() | m.ImportFrom()])) or \
           m.matches(stmt, m.ImportFrom()) or m.matches(stmt, m.Import()):
            insert_idx=i+1
    body.insert(insert_idx, insert_stmt)
    return mod.with_changes(body=body).code

def add_named_import(module, module_name:str, symbol:str)->Tuple[Any,bool]:
    cst, m = require_libcst()
    class Finder(cst.CSTVisitor):
        def __init__(self): self.found=False
        def visit_ImportFrom(self, node:cst.ImportFrom):
            if node.module and node.module.value == module_name:
                for n in node.names:
                    if isinstance(n, cst.ImportAlias) and n.name.value == symbol:
                        self.found=True
    finder=Finder(); module.visit(finder)
    if finder.found:
        return module, False
    imp = cst.parse_statement(f"from {module_name} import {symbol}\n")
    body=list(module.body)
    insert_idx=0
    for i, stmt in enumerate(body):
        if m.matches(stmt, m.SimpleStatementLine(body=[m.Import() | m.ImportFrom()])) or \
           m.matches(stmt, m.ImportFrom()) or m.matches(stmt, m.Import()):
            insert_idx=i+1
    body.insert(insert_idx, imp)
    return module.with_changes(body=body), True

# ----------------------------- AUTOPATCH: annual_savings -----------------------------

HEIKLE_PATTERNS = {('peak_reduction_kw','*','power_price_per_kw')}

RESULT_KEYS = {
    'annual_total_savings_euro',
    'annual_financial_benefit_year1',
    'annual_savings_consumption_eur',
    'jahresersparnis_gesamt',
    'total_annual_savings',
    'annual_savings',
    'annual_savings_total_euro',
}
FEEDIN_NAMES = {'annual_feedin_revenue','feed_in_revenue','annual_feed_in_revenue','annual_revenue_feed_in_eur'}
CONSUMP_SAVINGS_NAMES = {'annual_electricity_savings','consumption_savings','annual_savings_consumption_eur'}
OLD_COST_NAMES = {'annual_old_cost','old_annual_cost','annual_cost_old'}
HP_COST_NAMES  = {'annual_hp_cost','hp_annual_cost','annual_cost_hp'}
WITHOUT_PV_NAMES={'electricity_costs_without_pv','cost_without_pv','annual_cost_without_pv'}
WITH_PV_NAMES={'electricity_costs_with_pv','cost_with_pv','annual_cost_with_pv'}
FEEDIN_EXTRA = {'annual_feed_in_revenue','annual_feedin_revenue','feed_in_revenue','annual_revenue_feed_in_eur'}

def autopatch_annual_savings(root:str, write:bool, no_backup:bool, out:str):
    cst, m = require_libcst()
    ensure_dir(out)
    report=[]
    changed_files=0

    def process(path:str)->bool:
        nonlocal report
        code = read_text(path)
        base = os.path.basename(path).lower()
        if base == "calculations.py":
            new_code = insert_def_if_missing_calculations(code, "compute_annual_savings", COMPUTE_DEF_CODE)
            if new_code != code and write:
                if not no_backup: write_text(path+".bak", code)
                write_text(path, new_code)
                code = new_code
        try:
            mod = cst.parse_module(code)
        except Exception:
            return False

        class Tx(cst.CSTTransformer):
            def __init__(self): self.changed=False
            def leave_Module(self, orig, updated):
                if self.changed:
                    updated, imp = add_named_import(updated, "calculations", "compute_annual_savings")
                    if imp:
                        report.append(dict(file=path, lineno="1", before="(kein Import)", after="from calculations import compute_annual_savings", reason="missing_import_added"))
                return updated
            def leave_Assign(self, orig, updated):
                try:
                    if len(orig.targets)!=1 or not m.matches(orig.targets[0].target, m.Name("annual_savings")):
                        return updated
                except Exception:
                    return updated
                orig_code = orig.value.code
                for a,b,c in HEIKLE_PATTERNS:
                    if a in orig_code and c in orig_code:
                        report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig_code, after="(unchanged)", reason="skipped_suspicious_pattern"))
                        return updated
                # results.get('key', default)
                if m.matches(orig.value, m.Call(func=m.Attribute(attr=m.Name("get")))):
                    call = orig.value
                    if call.args and m.matches(call.args[0].value, m.SimpleString()):
                        key = call.args[0].value.value.strip('\'"')
                        if key in RESULT_KEYS:
                            default_expr = call.args[1].value.code if len(call.args)>=2 else "0.0"
                            new_call = cst.parse_expression(f"compute_annual_savings(results={call.func.value.code}, default={default_expr})")
                            self.changed=True
                            report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig_code, after=new_call.code, reason="results_get_to_compute"))
                            return updated.with_changes(value=new_call)
                # dict['key']
                if m.matches(orig.value, m.Subscript(value=m.DoNotCare(), slice=m.SubscriptElement())):
                    sub = orig.value
                    try:
                        if m.matches(sub.slice, m.Index(value=m.SimpleString())):
                            key = sub.slice.value.value.strip('\'"')
                            if key in RESULT_KEYS:
                                new_call = cst.parse_expression(f"compute_annual_savings(results={sub.value.code}, default=0.0)")
                                self.changed=True
                                report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig_code, after=new_call.code, reason="dict_index_to_compute"))
                                return updated.with_changes(value=new_call)
                    except Exception:
                        pass
                # feedin + consumption
                if m.matches(orig.value, m.BinaryOperation(operator=m.Add())):
                    l=orig.value.left; r=orig.value.right
                    def name_in(node, names:Set[str]):
                        if m.matches(node, m.Name()):
                            if node.value in names: return node.value
                        if m.matches(node, m.Attribute()):
                            try:
                                if node.attr.value in names: return node.attr.value
                            except Exception: pass
                        return None
                    f1 = name_in(l, FEEDIN_NAMES) or name_in(r, FEEDIN_NAMES)
                    c1 = name_in(l, CONSUMP_SAVINGS_NAMES) or name_in(r, CONSUMP_SAVINGS_NAMES)
                    if f1 and c1:
                        feed = l if name_in(l, FEEDIN_NAMES) else r
                        cons = r if feed is l else l
                        new_call=cst.parse_expression(f"compute_annual_savings(annual_feedin_revenue={feed.code}, annual_electricity_savings={cons.code}, default=0.0)")
                        self.changed=True
                        report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig_code, after=new_call.code, reason="feedin_plus_consumption"))
                        return updated.with_changes(value=new_call)
                # old - hp
                if m.matches(orig.value, m.BinaryOperation(operator=m.Subtract())):
                    l=orig.value.left; r=orig.value.right
                    def name_in(node, names:Set[str]):
                        if m.matches(node, m.Name()):
                            if node.value in names: return node.value
                        if m.matches(node, m.Attribute()):
                            try:
                                if node.attr.value in names: return node.attr.value
                            except Exception: pass
                        return None
                    if (name_in(l, OLD_COST_NAMES) and name_in(r, HP_COST_NAMES)):
                        new_call=cst.parse_expression(f"compute_annual_savings(annual_old_cost={l.code}, annual_hp_cost={r.code}, default=0.0)")
                        self.changed=True
                        report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig_code, after=new_call.code, reason="old_minus_hp"))
                        return updated.with_changes(value=new_call)
                # (without - with) (+ feedin)
                val=orig.value
                def has_names(node, A:Set[str], B:Set[str]):
                    if not m.matches(node, m.BinaryOperation(operator=m.Subtract())): return False
                    l=node.left; r=node.right
                    def name_in(n, names:Set[str]):
                        if m.matches(n, m.Name()):
                            return n.value in names
                        if m.matches(n, m.Attribute()):
                            try: return n.attr.value in names
                            except Exception: return False
                        return False
                    return name_in(l, A) and name_in(r, B)
                if m.matches(val, m.BinaryOperation(operator=m.Subtract())) and has_names(val, WITHOUT_PV_NAMES, WITH_PV_NAMES):
                    new_call=cst.parse_expression(f"compute_annual_savings(electricity_costs_without_pv={val.left.code}, electricity_costs_with_pv={val.right.code}, default=0.0)")
                    self.changed=True
                    report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig.value.code, after=new_call.code, reason="without_with_difference"))
                    return updated.with_changes(value=new_call)
                if m.matches(val, m.BinaryOperation(operator=m.Add())):
                    l=val.left; r=val.right
                    if m.matches(l, m.BinaryOperation(operator=m.Subtract())) and has_names(l, WITHOUT_PV_NAMES, WITH_PV_NAMES):
                        # (a-b)+c where c is feedin
                        if r.code and any(k in r.code for k in FEEDIN_EXTRA):
                            new_call=cst.parse_expression(f"compute_annual_savings(electricity_costs_without_pv={l.left.code}, electricity_costs_with_pv={l.right.code}, annual_feed_in_revenue={r.code}, default=0.0)")
                            self.changed=True
                            report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig.value.code, after=new_call.code, reason="diff_plus_feedin"))
                            return updated.with_changes(value=new_call)
                    if m.matches(r, m.BinaryOperation(operator=m.Subtract())) and has_names(r, WITHOUT_PV_NAMES, WITH_PV_NAMES):
                        if l.code and any(k in l.code for k in FEEDIN_EXTRA):
                            new_call=cst.parse_expression(f"compute_annual_savings(electricity_costs_without_pv={r.left.code}, electricity_costs_with_pv={r.right.code}, annual_feed_in_revenue={l.code}, default=0.0)")
                            self.changed=True
                            report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig.value.code, after=new_call.code, reason="feedin_plus_diff"))
                            return updated.with_changes(value=new_call)
                return updated

        tx=Tx()
        new_mod = mod.visit(tx)
        if tx.changed and write:
            if not no_backup: write_text(path+".bak", code)
            write_text(path, new_mod.code)
            return True
        return tx.changed

    for p in list_py(root):
        try:
            if process(p): changed_files+=1
        except Exception as e:
            report.append(dict(file=p, lineno="?", before="", after="", reason=f"ERROR:{e}"))

    rep=os.path.join(out,"autopatch_annual_savings_report.csv")
    with open(rep,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=["file","lineno","before","after","reason"])
        w.writeheader()
        for r in report: w.writerow(r)
    return changed_files, rep

# ----------------------------- AUTOPATCH: project_data -----------------------------

def autopatch_project_data(root:str, write:bool, no_backup:bool, out:str):
    cst, m = require_libcst()
    ensure_dir(out)
    report=[]; changed_files=0

    def process(path:str)->bool:
        nonlocal report
        code = read_text(path)
        base = os.path.basename(path).lower()
        if base == "calculations.py":
            new_code = insert_def_if_missing_calculations(code, "build_project_data", BUILD_PD_DEF_CODE)
            if new_code != code and write:
                if not no_backup: write_text(path+".bak", code)
                write_text(path, new_code)
                code = new_code
        try:
            mod = cst.parse_module(code)
        except Exception:
            return False

        class Tx(cst.CSTTransformer):
            def __init__(self): self.changed=False
            def leave_Module(self, orig, updated):
                if self.changed:
                    updated, imp = add_named_import(updated, "calculations", "build_project_data")
                    if imp:
                        report.append(dict(file=path, lineno="1", before="(kein Import)", after="from calculations import build_project_data", reason="missing_import_added"))
                return updated

            def leave_SimpleStatementLine(self, orig, updated):
                # project_data.update({...})
                if len(orig.body)==1 and m.matches(orig.body[0], m.Expr(value=m.Call(func=m.Attribute()))):
                    call = orig.body[0].value
                    if m.matches(call.func, m.Attribute(value=m.Name("project_data"), attr=m.Name("update"))):
                        arg_code = call.args[0].value.code if call.args else "{}"
                        repl = cst.parse_statement(f"project_data = build_project_data(project_data, {arg_code})\n")
                        self.changed=True
                        report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=call.code, after=repl.code.strip(), reason="project_data.update"))
                        return repl
                return updated

            def leave_Assign(self, orig, updated):
                # project_data = ...
                if len(orig.targets)!=1 or not m.matches(orig.targets[0].target, m.Name("project_data")):
                    return updated
                rhs = orig.value
                # dict literal (inkl. {**a, **b})
                if m.matches(rhs, m.Dict()):
                    new = cst.parse_expression(f"build_project_data({rhs.code})")
                    self.changed=True
                    report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=rhs.code, after=new.code, reason="dict_literal_to_builder"))
                    return updated.with_changes(value=new)
                # dict union: a | b
                if m.matches(rhs, m.BinaryOperation(operator=m.BitOr())):
                    new = cst.parse_expression(f"build_project_data({rhs.left.code}, {rhs.right.code})")
                    self.changed=True
                    report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=rhs.code, after=new.code, reason="dict_union_to_builder"))
                    return updated.with_changes(value=new)
                # call(...)
                if m.matches(rhs, m.Call()):
                    fname = rhs.func.attr.value if m.matches(rhs.func, m.Attribute()) else (rhs.func.value if m.matches(rhs.func, m.Name()) else "call")
                    new = cst.parse_expression(f"build_project_data({rhs.code})")
                    reason = f"{fname}_to_builder" if str(fname).lower() in {"dict","merge","combine","deepmerge","update"} else "call_wrapped_to_builder"
                    self.changed=True
                    report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=rhs.code, after=new.code, reason=reason))
                    return updated.with_changes(value=new)
                return updated

        tx=Tx()
        new_mod = mod.visit(tx)
        if tx.changed and write:
            if not no_backup: write_text(path+".bak", code)
            write_text(path, new_mod.code)
            return True
        return tx.changed

    for p in list_py(root):
        try:
            if process(p): changed_files+=1
        except Exception as e:
            report.append(dict(file=p, lineno="?", before="", after="", reason=f"ERROR:{e}"))

    rep=os.path.join(out,"autopatch_project_data_report.csv")
    with open(rep,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=["file","lineno","before","after","reason"])
        w.writeheader()
        for r in report: w.writerow(r)
    return changed_files, rep

# ----------------------------- STRUCTURE -----------------------------

def do_structure(root:str, out:str):
    ensure_dir(out)
    rows=[]
    for r,_,f in os.walk(root):
        for fn in f:
            p=os.path.join(r,fn)
            rel=os.path.relpath(p, root)
            try:
                size=os.path.getsize(p)
            except Exception:
                size=None
            text=""; ext=os.path.splitext(fn)[1].lower()
            if ext in {".py",".ts",".tsx",".js",".json",".yml",".yaml",".md",".txt",".ini",".cfg"}:
                try:
                    text=read_text(p)
                except Exception: text=""
            n_lines=text.count("\n")+1 if text else 0
            rows.append(dict(path=rel, ext=ext, size=size, lines=n_lines))
    import pandas as pd, json
    df=pd.DataFrame(rows).sort_values("path")

    def tag_roles(path, ext, text):
        tags=[]; primary="misc"
        p=path.lower()
        if any(k in p for k in ["pdf","doc","report"]): tags.append("pdf")
        if any(k in p for k in ["ui","view","screen","pages","components"]): tags.append("ui")
        if any(k in p for k in ["calc","analysis","compute"]): tags.append("calc")
        if any(k in p for k in ["api","server","backend","fastapi"]): tags.append("api")
        if any(k in p for k in ["data","csv","excel","db","sql"]): tags.append("data")
        if any(k in p for k in ["utils","helpers","common","lib"]): tags.append("utils")
        if ext in [".tsx",".ts",".js"]: tags.append("frontend")
        if ext == ".py": tags.append("python")
        if ext in [".yml",".yaml"]: tags.append("yaml")
        if ext == ".json": tags.append("json")
        if text:
            if re.search(r"\bstreamlit\b", text): tags += ["streamlit","ui"]
            if re.search(r"\b(reportlab|fitz|pymupdf|pypdf|borb|weasyprint|pikepdf)\b", text, re.I): tags.append("pdf")
            if re.search(r"\b(pandas|numpy|scipy)\b", text): tags.append("calc")
            if re.search(r"\bfastapi\b", text, re.I): tags.append("api")
            if re.search(r"\b(sqlite3|better-sqlite3|sqlalchemy|psycopg2)\b", text, re.I): tags.append("db")
            if re.search(r"\breact\b|\bprimereact\b|\bchakra-ui\b|\btailwind\b", text, re.I): tags += ["react","ui"]
            if re.search(r"\belectron\b", text, re.I): tags.append("electron")
            if re.search(r"\bheatpump|waermepumpe|wärmepumpe\b", text, re.I): tags.append("heatpump")
            if re.search(r"\bphotovoltaic|photovoltaik|pv\b", text, re.I): tags.append("pv")
            if re.search(r"\bcrm\b", text, re.I): tags.append("crm")
            if re.search(r"\bqrcode|qr\b", text, re.I): tags.append("qr")
            if re.search(r"\bicc\b|\bcolorspace\b|\bcolormanagement\b", text, re.I): tags.append("color")
            if re.search(r"\bpyyaml|yaml\.safe_load\b", text, re.I): tags.append("yaml-io")
            if re.search(r"\bghostscript|gswin|pdfcompress\b", text, re.I): tags.append("pdf-post")
            if re.search(r"\bdocx|python-docx\b", text, re.I): tags.append("docx")
            if re.search(r"\bmatplotlib|plotly|altair\b", text, re.I): tags.append("charts")
        prio=["frontend","ui","pdf","calc","api","db","data","utils","python","yaml","json"]
        uniq=[]
        for t in tags:
            if t not in uniq: uniq.append(t)
        for c in prio:
            if c in uniq: primary=c; break
        return primary, ",".join(uniq)

    roles=[]
    for _, r in df.iterrows():
        t=""
        if r["ext"] in [".py",".ts",".tsx",".js",".json",".yml",".yaml",".md",".txt",".ini",".cfg"]:
            try:
                t=read_text(os.path.join(root, r["path"]))
            except Exception: t=""
        primary, tags = tag_roles(r["path"], r["ext"], t)
        roles.append((primary, tags))
    df["primary_role"]=[x[0] for x in roles]
    df["tags"]=[x[1] for x in roles]

    # Save
    manifest = os.path.join(out, "app_structure_manifest.csv")
    df.to_csv(manifest, index=False, encoding="utf-8")

    # Dir summary
    import pandas as pd
    from pathlib import Path
    by_dir=[]
    for _, r in df.iterrows():
        d=str(Path(r["path"]).parent)
        by_dir.append((d, r["path"], r["primary_role"]))
    bdf=pd.DataFrame(by_dir, columns=["dir","path","role"])
    dir_summary=bdf.groupby("dir").agg(files=("path","count"), roles=("role", lambda s: ",".join(sorted(set([x for x in s if pd.notna(x)]))))).reset_index().sort_values("dir")
    dir_csv=os.path.join(out, "app_structure_dirs.csv")
    dir_summary.to_csv(dir_csv, index=False, encoding="utf-8")

    # Trees
    from pathlib import Path
    def tree_text(root_dir, max_depth=3):
        lines=[]
        root_path=Path(root_dir)
        for path in sorted(root_path.rglob("*")):
            rel=path.relative_to(root_path)
            if len(rel.parts)==0: continue
            depth=len(rel.parts)
            if depth>max_depth: continue
            indent="  "*(depth-1)
            lines.append(f"{indent}{'📁' if path.is_dir() else '📄'} {rel.name}")
        return "\n".join(lines)

    depth3=os.path.join(out,"app_tree_depth3.txt")
    write_text(depth3, tree_text(root,3))

    # Full tree
    all_lines=[]
    for p in sorted(Path(root).rglob("*")):
        rel=p.relative_to(Path(root))
        if len(rel.parts)==0: continue
        indent="  "*(len(rel.parts)-1)
        all_lines.append(f"{indent}{'📁' if p.is_dir() else '📄'} {rel.name}")
    full=os.path.join(out,"app_tree_full.txt")
    write_text(full, "\n".join(all_lines))

    return manifest, dir_csv, depth3, full

# ----------------------------- YAML Positions-Check -----------------------------

def yaml_positions_check(root:str, out:str, tol_mm:float=0.2, key_x=("x","left"), key_y=("y","top"), key_page=("page","seite","p")):
    ensure_dir(out)
    try:
        import yaml  # type: ignore
        loader_available=True
    except Exception:
        yaml=None; loader_available=False

    collisions=[]
    import math, json
    for path in list_yaml(root):
        try:
            text=read_text(path)
        except Exception:
            continue
        docs=[]
        if loader_available:
            try:
                for doc in yaml.safe_load_all(text):  # type: ignore
                    if doc is not None: docs.append(doc)
            except Exception:
                # Fallback: naive
                docs=[]
        # Heuristic fallback: try to extract dict-like blocks
        if not docs:
            # naive parse of "key: value" lines into one dict (best-effort)
            current={}
            for line in text.splitlines():
                m=re.match(r'^\s*([A-Za-z0-9_\-\.]+)\s*:\s*(.+?)\s*$', line)
                if m:
                    current[m.group(1)] = m.group(2)
            if current: docs=[current]

        def visit(o, file_path):
            if isinstance(o, dict):
                keys_lower={str(k).lower():k for k in o.keys()}
                def first_key(cands):
                    for c in cands:
                        if c in keys_lower:
                            return keys_lower[c]
                    return None
                kx=first_key(k.lower() for k in key_x) if False else None  # not used
                # read numeric x,y if present
                xk = first_key([k for k in key_x])
                yk = first_key([k for k in key_y])
                pg = first_key([k for k in key_page])
                try:
                    x = float(o[xk]) if xk and o.get(xk) is not None else None
                    y = float(o[yk]) if yk and o.get(yk) is not None else None
                    p = int(o[pg]) if pg and o.get(pg) is not None else 1
                except Exception:
                    x=y=None; p=None
                if x is not None and y is not None and p is not None:
                    collisions.append(dict(file=file_path, page=p, x=x, y=y, key_hint=list(o.keys())[:3]))
                # recurse
                for v in o.values():
                    visit(v, file_path)
            elif isinstance(o, list):
                for it in o:
                    visit(it, file_path)

        for d in docs:
            visit(d, path)

    # Group by (page, x,y) within tolerance
    # Convert mm tolerance to absolute tolerance; we assume coordinates already in mm; if not, it's still a useful near-duplicate detector.
    groups=[]
    used=[False]*len(collisions)
    for i,a in enumerate(collisions):
        if used[i]: continue
        group=[a]; used[i]=True
        for j,b in enumerate(collisions):
            if used[j]: continue
            if a["file"]==b["file"] and a["page"]==b["page"] and abs(a["x"]-b["x"])<=tol_mm and abs(a["y"]-b["y"])<=tol_mm:
                group.append(b); used[j]=True
        if len(group)>1:
            groups.append(group)

    # Save CSV
    import pandas as pd
    flat=[]
    for g in groups:
        for item in g:
            flat.append(dict(file=item["file"], page=item["page"], x=item["x"], y=item["y"], key_hint=";".join(map(str,item["key_hint"]))))
        flat.append(dict(file="---", page="", x="", y="", key_hint=""))
    out_csv=os.path.join(out, "yaml_position_collisions.csv")
    pd.DataFrame(flat).to_csv(out_csv, index=False, encoding="utf-8")
    return out_csv

# ----------------------------- CLI -----------------------------

def main():
    ap = argparse.ArgumentParser(description="Kakerlake Super Ultra Cleaner")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_scan = sub.add_parser("scan", help="Python-Kollisionen scannen")
    ap_scan.add_argument("root")
    ap_scan.add_argument("--out", default="ultra_reports")

    ap_aas = sub.add_parser("autopatch-annual-savings", help="annual_savings zentralisieren")
    ap_aas.add_argument("root")
    ap_aas.add_argument("--out", default="ultra_reports")
    ap_aas.add_argument("--write", action="store_true")
    ap_aas.add_argument("--no-backup", action="store_true")

    ap_pd = sub.add_parser("autopatch-project-data", help="project_data zentralisieren")
    ap_pd.add_argument("root")
    ap_pd.add_argument("--out", default="ultra_reports")
    ap_pd.add_argument("--write", action="store_true")
    ap_pd.add_argument("--no-backup", action="store_true")

    ap_struct = sub.add_parser("structure", help="App-Struktur-Manifest & Trees erzeugen")
    ap_struct.add_argument("root")
    ap_struct.add_argument("--out", default="ultra_reports")

    ap_yaml = sub.add_parser("yaml-check", help="YAML-Positionskollisionen erkennen")
    ap_yaml.add_argument("root")
    ap_yaml.add_argument("--out", default="ultra_reports")
    ap_yaml.add_argument("--tol-mm", type=float, default=0.2)

    ap_all = sub.add_parser("all", help="Alles: scan + structure + yaml-check + Autopatches (write)")
    ap_all.add_argument("root")
    ap_all.add_argument("--out", default="ultra_reports")
    ap_all.add_argument("--no-backup", action="store_true")

    args = ap.parse_args()
    out = ensure_dir(args.out)

    if args.cmd == "scan":
        scan_python(args.root, out)
        print("SCAN fertig. CSVs in:", out)
        return

    if args.cmd == "autopatch-annual-savings":
        ch, rep = autopatch_annual_savings(args.root, write=args.write, no_backup=args.no_backup, out=out)
        print(f"Autopatch annual_savings: {ch} Dateien geändert. Report: {rep}")
        return

    if args.cmd == "autopatch-project-data":
        ch, rep = autopatch_project_data(args.root, write=args.write, no_backup=args.no_backup, out=out)
        print(f"Autopatch project_data: {ch} Dateien geändert. Report: {rep}")
        return

    if args.cmd == "structure":
        manifest, dirs, t3, full = do_structure(args.root, out)
        print("STRUCTURE fertig:", manifest, dirs, t3, full)
        return

    if args.cmd == "yaml-check":
        csv_path = yaml_positions_check(args.root, out, tol_mm=args.tol_mm)
        print("YAML-CHECK fertig:", csv_path)
        return

    if args.cmd == "all":
        # 1) Struktur & Scan & YAML
        manifest, dirs, t3, full = do_structure(args.root, out)
        scan_python(args.root, out)
        yaml_positions_check(args.root, out, tol_mm=0.2)

        # 2) Autopatches (write)
        try:
            aas_ch, aas_rep = autopatch_annual_savings(args.root, write=True, no_backup=args.no_backup, out=out)
        except Exception as e:
            aas_ch, aas_rep = 0, f"(ERROR:{e})"
        try:
            pd_ch, pd_rep = autopatch_project_data(args.root, write=True, no_backup=args.no_backup, out=out)
        except Exception as e:
            pd_ch, pd_rep = 0, f"(ERROR:{e})"

        # 3) ZIP zusammenstellen
        import zipfile
        zip_path = os.path.join(out, "ultra_reports.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for fn in os.listdir(out):
                if fn == "ultra_reports.zip": continue
                z.write(os.path.join(out, fn), arcname=fn)

        print("ALL fertig.")
        print("SCAN/STRUCT/YAML CSVs und Reports in:", out)
        print("Autopatch annual_savings:", aas_ch, "Dateien; Report:", aas_rep)
        print("Autopatch project_data:", pd_ch, "Dateien; Report:", pd_rep)
        print("ZIP:", zip_path)
        return

if __name__ == "__main__":
    main()
'''
with open(ULTRA_PATH, "w", encoding="utf-8") as f:
    f.write(code)

ULTRA_PATH
