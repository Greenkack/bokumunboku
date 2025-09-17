#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kakerlake_ultra_cleaner.py
=================================
Ein einziger „Super Ultra Reiniger“ für dein Projekt. Kombiniert:
  1) SCAN: Duplikate & Kollisionen (Python)
  2) AUTOPATCH: annual_savings ➜ compute_annual_savings(...)
  3) AUTOPATCH: project_data ➜ build_project_data(...)
  4) STRUCTURE: App-Struktur-Manifest, Verzeichnis-Übersicht, Trees
  5) YAML-CHECK: Positionskollisionen
"""
from __future__ import annotations
import os, re, sys, ast, csv, argparse, hashlib, textwrap
from typing import Any, Dict, List, Optional, Tuple, Set

# ---------- Utils ----------
def read_text(path:str)->str:
    return open(path, "r", encoding="utf-8", errors="ignore").read()

def write_text(path:str, text:str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(text)

def ensure_dir(p:str):
    os.makedirs(p, exist_ok=True); return p

def list_py(root:str)->List[str]:
    out=[]; 
    for r,_,f in os.walk(root):
        for fn in f:
            if fn.endswith(".py"): out.append(os.path.join(r,fn))
    return out

def list_yaml(root:str)->List[str]:
    out=[]; 
    for r,_,f in os.walk(root):
        for fn in f:
            if fn.lower().endswith((".yml",".yaml")): out.append(os.path.join(r,fn))
    return out

# ---------- Scan ----------
COMMUTATIVE_OPS=(ast.Add, ast.Mult,)
def node_signature(node:ast.AST):
    if node is None: return ('None',)
    if isinstance(node, ast.Name): return ('Name', node.id)
    if isinstance(node, ast.Attribute):
        try: base=ast.unparse(node.value)
        except Exception: base=('AttrBase',)
        return ('Attr', base, node.attr)
    if isinstance(node, ast.Constant): return ('Const', repr(node.value))
    if isinstance(node, ast.Call):
        return ('Call', node_signature(node.func),
                tuple(node_signature(a) for a in node.args),
                tuple(sorted((k.arg if k.arg else '**', node_signature(k.value)) for k in node.keywords)))
    if isinstance(node, ast.BinOp):
        op_type=type(node.op).__name__
        if isinstance(node.op, COMMUTATIVE_OPS):
            def flatten(n):
                if isinstance(n, ast.BinOp) and isinstance(n.op, type(node.op)): return flatten(n.left)+flatten(n.right)
                return [n]
            terms = flatten(node.left)+flatten(node.right)
            return (op_type, tuple(sorted([node_signature(t) for t in terms])))
        return (op_type, node_signature(node.left), node_signature(node.right))
    if isinstance(node, ast.UnaryOp): return (type(node.op).__name__, node_signature(node.operand))
    if isinstance(node, ast.Compare):
        return ('Compare', node_signature(node.left),
                tuple(type(op).__name__ for op in node.ops),
                tuple(node_signature(c) for c in node.comparators))
    if isinstance(node, ast.BoolOp):
        vals = tuple(sorted(node_signature(v) for v in node.values)) if isinstance(node.op,(ast.And,ast.Or)) else tuple(node_signature(v) for v in node.values)
        return ('BoolOp', type(node.op).__name__, vals)
    if isinstance(node, ast.Subscript):
        try: s=node_signature(node.slice)
        except Exception: s=('Slice','err')
        return ('Subscript', node_signature(node.value), s)
    if isinstance(node, ast.Dict):
        items=[]; 
        for k,v in zip(node.keys, node.values):
            items.append(('UNPACK', node_signature(v)) if k is None else ('KV', node_signature(k), node_signature(v)))
        return ('Dict', tuple(sorted(items)))
    if isinstance(node, ast.List): return ('List', tuple(node_signature(e) for e in node.elts))
    if isinstance(node, ast.Tuple): return ('Tuple', tuple(node_signature(e) for e in node.elts))
    return ('Other', type(node).__name__)

def node_shape(node:ast.AST):
    if node is None: return ('None',)
    if isinstance(node, ast.Name): return ('Name',)
    if isinstance(node, ast.Attribute): return ('Attr',)
    if isinstance(node, ast.Constant): return ('Const',)
    if isinstance(node, ast.Call): return ('Call', len(node.args), len(node.keywords))
    if isinstance(node, ast.BinOp):
        op_type=type(node.op).__name__
        if isinstance(node.op, COMMUTATIVE_OPS):
            def flatten(n):
                if isinstance(n, ast.BinOp) and isinstance(n.op, type(node.op)): return flatten(n.left)+flatten(n.right)
                return [n]
            terms = flatten(node.left)+flatten(node.right)
            return (op_type, tuple(sorted([node_shape(t) for t in terms])))
        return (op_type, node_shape(node.left), node_shape(node.right))
    if isinstance(node, ast.UnaryOp): return (type(node.op).__name__, node_shape(node.operand))
    if isinstance(node, ast.Compare): return ('Compare', tuple(type(op).__name__ for op in node.ops), len(node.comparators))
    if isinstance(node, ast.BoolOp): return ('BoolOp', type(node.op).__name__, len(node.values))
    if isinstance(node, ast.Subscript): return ('Subscript',)
    if isinstance(node, ast.Dict): return ('Dict', len(node.keys))
    if isinstance(node, ast.List): return ('List', len(node.elts))
    if isinstance(node, ast.Tuple): return ('Tuple', len(node.elts))
    return ('Other', type(node).__name__)

def collect_names(node:ast.AST)->Set[str]:
    names=set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name): names.add(n.id)
    return names

def scan_python(root:str, out:str):
    import pandas as pd
    ensure_dir(out)
    py = list_py(root)
    assignments=[]; func_defs=[]; errors=[]
    for p in py:
        try:
            src=read_text(p); tree=ast.parse(src, filename=p); lines=src.splitlines()
        except Exception as e:
            errors.append((p, repr(e))); continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else ([node.target] if node.target is not None else [])
                value = node.value if hasattr(node,'value') else None
                if value is None: continue
                for t in targets:
                    lhs=None
                    if isinstance(t, ast.Name): lhs=t.id
                    elif isinstance(t, ast.Attribute):
                        try: lhs=ast.unparse(t)
                        except Exception: lhs=None
                    if lhs is None: continue
                    sig=node_signature(value); shape=node_shape(value)
                    vars_used=",".join(sorted(list(collect_names(value))))
                    lineno=getattr(node,'lineno',None)
                    text_line=lines[lineno-1].strip() if lineno and 1<=lineno<=len(lines) else ""
                    assignments.append(dict(file=p, lineno=lineno, lhs=lhs, rhs_sig=repr(sig), rhs_shape=repr(shape), rhs_vars=vars_used, line=text_line))
            if isinstance(node, ast.FunctionDef):
                start=node.lineno; end=getattr(node,'end_lineno',start); body_src="\n".join(lines[start-1:end])
                norm=re.sub(r'\s+','',body_src)
                func_defs.append(dict(file=p,name=node.name,lineno=start,end_lineno=end,hash=hashlib.md5(norm.encode()).hexdigest(),body=body_src))
    assign_df=pd.DataFrame(assignments); func_df=pd.DataFrame(func_defs)

    dup_lhs=assign_df.groupby('lhs').agg(count=('lhs','size'), unique_rhs=('rhs_sig','nunique')).reset_index()
    conflicting=dup_lhs[(dup_lhs['count']>1) & (dup_lhs['unique_rhs']>1)]
    lhs_df=assign_df[assign_df['lhs'].isin(set(conflicting['lhs']))].sort_values(['lhs','rhs_sig','file','lineno'])
    lhs_df.to_csv(os.path.join(out,"python_lhs_conflicts.csv"), index=False, encoding="utf-8")

    rhs_groups=assign_df.groupby('rhs_sig').agg(lhs_set=('lhs', lambda x: sorted(set(x))), count=('lhs','size')).reset_index()
    rhs_conf=rhs_groups[rhs_groups['lhs_set'].map(len)>1]
    rhs_df=assign_df.merge(rhs_conf[['rhs_sig']], on='rhs_sig', how='inner').sort_values(['rhs_sig','lhs','file','lineno'])
    rhs_df.to_csv(os.path.join(out,"python_rhs_same_expr_diff_lhs.csv"), index=False, encoding="utf-8")

    rows=[]
    for lhs, g in assign_df.groupby('lhs'):
        for shape, sub in g.groupby('rhs_shape'):
            if len(sub)>=2 and sub['rhs_vars'].nunique()>1:
                rows.append(sub)
    if rows:
        pd.concat(rows).to_csv(os.path.join(out, "python_lhs_same_shape_diff_vars.csv"), index=False, encoding="utf-8")
    else:
        assign_df.head(0).to_csv(os.path.join(out, "python_lhs_same_shape_diff_vars.csv"), index=False, encoding="utf-8")

    name_groups=func_df.groupby('name').agg(files=('file', list), hashes=('hash', lambda x:list(x))).reset_index()
    conflicts=[]
    for _, row in name_groups.iterrows():
        if len(set(row['hashes']))>1:
            conflicts.append(dict(name=row['name'], distinct_impls=len(set(row['hashes'])), files=" | ".join(sorted(set(row['files'])))))
    pd.DataFrame(conflicts).to_csv(os.path.join(out, "python_function_name_conflicts.csv"), index=False, encoding="utf-8")

    body_groups=func_df.groupby('hash').agg(names=('name', list), files=('file', list), count=('hash','size')).reset_index()
    body_groups[body_groups['count']>1][['hash','count','names','files']].to_csv(os.path.join(out, "python_function_body_duplicates.csv"), index=False, encoding="utf-8")

    pd.DataFrame(errors, columns=["file","error"]).to_csv(os.path.join(out, "python_parse_errors.csv"), index=False, encoding="utf-8")

    top30=dup_lhs.sort_values("unique_rhs", ascending=False).head(30)[["lhs","count","unique_rhs"]].rename(columns={"count":"n_assign","unique_rhs":"n_rhs"})
    top30.to_csv(os.path.join(out, "top30_conflicting_lhs.csv"), index=False, encoding="utf-8")

# ---------- DEF-Blocks ----------
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
    out = {}
    def _coerce(x):
        try:
            if x is None: return {}
            if isinstance(x, dict): return x
            if hasattr(x, 'items'): return dict(x.items())
            return dict(x)
        except Exception:
            return {}
    for part in parts:
        d = _coerce(part)
        for k, v in d.items():
            if drop_none and v is None: continue
            if drop_empty_str and isinstance(v, str) and v.strip()== "": continue
            kk = k
            try:
                if isinstance(kk, str):
                    kk = kk.strip().replace("\\u200b","").replace("\\n"," ").strip()
                if keymap and kk in keymap: kk = keymap[kk]
            except Exception: pass
            out[kk] = v
    return out
""".strip("\n")

def require_libcst():
    try:
        import libcst as cst
        import libcst.matchers as m
        return cst, m
    except Exception:
        print("Bitte installieren: pip install libcst", file=sys.stderr); raise

def insert_def_if_missing_calculations(code:str, func_name:str, def_code:str):
    cst, m = require_libcst()
    try: mod = cst.parse_module(code)
    except Exception: return code
    class Finder(cst.CSTVisitor):
        def __init__(self): self.found=False
        def visit_FunctionDef(self, node:cst.FunctionDef):
            if node.name.value == func_name: self.found=True
    f=Finder(); mod.visit(f)
    if f.found: return code
    insert_stmt = cst.parse_statement(def_code + "\n\n")
    body=list(mod.body); insert_idx=0
    for i, stmt in enumerate(body):
        if m.matches(stmt, m.SimpleStatementLine(body=[m.Import() | m.ImportFrom()])) or m.matches(stmt, m.ImportFrom()) or m.matches(stmt, m.Import()):
            insert_idx=i+1
    body.insert(insert_idx, insert_stmt)
    return mod.with_changes(body=body).code

def add_named_import(module, module_name:str, symbol:str):
    cst, m = require_libcst()
    class Finder(cst.CSTVisitor):
        def __init__(self): self.found=False
        def visit_ImportFrom(self, node:cst.ImportFrom):
            if node.module and node.module.value == module_name:
                for n in node.names:
                    if isinstance(n, cst.ImportAlias) and n.name.value == symbol:
                        self.found=True
    finder=Finder(); module.visit(finder)
    if finder.found: return module, False
    imp=cst.parse_statement(f"from {module_name} import {symbol}\n")
    body=list(module.body); insert_idx=0
    for i, stmt in enumerate(body):
        if m.matches(stmt, m.SimpleStatementLine(body=[m.Import() | m.ImportFrom()])) or m.matches(stmt, m.ImportFrom()) or m.matches(stmt, m.Import()):
            insert_idx=i+1
    body.insert(insert_idx, imp)
    return module.with_changes(body=body), True

# ---------- Autopatch annual_savings ----------
HEIKLE_PATTERNS = {('peak_reduction_kw','*','power_price_per_kw')}
RESULT_KEYS = {'annual_total_savings_euro','annual_financial_benefit_year1','annual_savings_consumption_eur','jahresersparnis_gesamt','total_annual_savings','annual_savings','annual_savings_total_euro'}
FEEDIN_NAMES = {'annual_feedin_revenue','feed_in_revenue','annual_feed_in_revenue','annual_revenue_feed_in_eur'}
CONSUMP_SAVINGS_NAMES = {'annual_electricity_savings','consumption_savings','annual_savings_consumption_eur'}
OLD_COST_NAMES = {'annual_old_cost','old_annual_cost','annual_cost_old'}
HP_COST_NAMES  = {'annual_hp_cost','hp_annual_cost','annual_cost_hp'}
WITHOUT_PV_NAMES={'electricity_costs_without_pv','cost_without_pv','annual_cost_without_pv'}
WITH_PV_NAMES={'electricity_costs_with_pv','cost_with_pv','annual_cost_with_pv'}
FEEDIN_EXTRA = {'annual_feed_in_revenue','annual_feedin_revenue','feed_in_revenue','annual_revenue_feed_in_eur'}

def autopatch_annual_savings(root:str, write:bool, no_backup:bool, out:str):
    cst, m = require_libcst(); ensure_dir(out); report=[]; changed_files=0
    def process(path:str)->bool:
        nonlocal report
        code=read_text(path); base=os.path.basename(path).lower()
        if base=="calculations.py":
            new=insert_def_if_missing_calculations(code, "compute_annual_savings", COMPUTE_DEF_CODE)
            if new!=code and write:
                if not no_backup: write_text(path+".bak", code)
                write_text(path, new); code=new
        try: mod=cst.parse_module(code)
        except Exception: return False
        class Tx(cst.CSTTransformer):
            def __init__(self): self.changed=False
            def leave_Module(self, orig, updated):
                if self.changed:
                    updated, imp = add_named_import(updated, "calculations", "compute_annual_savings")
                    if imp: report.append(dict(file=path, lineno="1", before="(kein Import)", after="from calculations import compute_annual_savings", reason="missing_import_added"))
                return updated
            def leave_Assign(self, orig, updated):
                try:
                    if len(orig.targets)!=1 or not m.matches(orig.targets[0].target, m.Name("annual_savings")): return updated
                except Exception: return updated
                orig_code=orig.value.code
                for a,_,c in HEIKLE_PATTERNS:
                    if a in orig_code and c in orig_code:
                        report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig_code, after="(unchanged)", reason="skipped_suspicious_pattern"))
                        return updated
                # results.get('key', default)
                if m.matches(orig.value, m.Call(func=m.Attribute(attr=m.Name("get")))):
                    call=orig.value
                    if call.args and m.matches(call.args[0].value, m.SimpleString()):
                        key=call.args[0].value.value.strip('\'"')
                        if key in RESULT_KEYS:
                            default_expr = call.args[1].value.code if len(call.args)>=2 else "0.0"
                            new_call=cst.parse_expression(f"compute_annual_savings(results={call.func.value.code}, default={default_expr})")
                            self.changed=True; report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig_code, after=new_call.code, reason="results_get_to_compute"))
                            return updated.with_changes(value=new_call)
                # dict['key']
                if m.matches(orig.value, m.Subscript(value=m.DoNotCare(), slice=m.SubscriptElement())):
                    sub=orig.value
                    try:
                        if m.matches(sub.slice, m.Index(value=m.SimpleString())):
                            key=sub.slice.value.value.strip('\'"')
                            if key in RESULT_KEYS:
                                new_call=cst.parse_expression(f"compute_annual_savings(results={sub.value.code}, default=0.0)")
                                self.changed=True; report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig_code, after=new_call.code, reason="dict_index_to_compute"))
                                return updated.with_changes(value=new_call)
                    except Exception: pass
                # feedin + consumption
                if m.matches(orig.value, m.BinaryOperation(operator=m.Add())):
                    l=orig.value.left; r=orig.value.right
                    def name_in(node, names:Set[str]):
                        if m.matches(node, m.Name()): 
                            return node.value if node.value in names else None
                        if m.matches(node, m.Attribute()):
                            try: return node.attr.value if node.attr.value in names else None
                            except Exception: return None
                        return None
                    f1 = name_in(l, FEEDIN_NAMES) or name_in(r, FEEDIN_NAMES)
                    c1 = name_in(l, CONSUMP_SAVINGS_NAMES) or name_in(r, CONSUMP_SAVINGS_NAMES)
                    if f1 and c1:
                        feed = l if name_in(l, FEEDIN_NAMES) else r
                        cons = r if feed is l else l
                        new_call=cst.parse_expression(f"compute_annual_savings(annual_feedin_revenue={feed.code}, annual_electricity_savings={cons.code}, default=0.0)")
                        self.changed=True; report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig_code, after=new_call.code, reason="feedin_plus_consumption"))
                        return updated.with_changes(value=new_call)
                # old - hp
                if m.matches(orig.value, m.BinaryOperation(operator=m.Subtract())):
                    l=orig.value.left; r=orig.value.right
                    def name_in(node, names:Set[str]):
                        if m.matches(node, m.Name()): 
                            return node.value in names
                        if m.matches(node, m.Attribute()):
                            try: return node.attr.value in names
                            except Exception: return False
                        return False
                    if name_in(l, OLD_COST_NAMES) and name_in(r, HP_COST_NAMES):
                        new_call=cst.parse_expression(f"compute_annual_savings(annual_old_cost={l.code}, annual_hp_cost={r.code}, default=0.0)")
                        self.changed=True; report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig_code, after=new_call.code, reason="old_minus_hp"))
                        return updated.with_changes(value=new_call)
                # (without - with) (+ feedin)
                val=orig.value
                def has_names(node, A:Set[str], B:Set[str]):
                    if not m.matches(node, m.BinaryOperation(operator=m.Subtract())): return False
                    l=node.left; r=node.right
                    def name_in2(n, names:Set[str]):
                        if m.matches(n, m.Name()): return n.value in names
                        if m.matches(n, m.Attribute()):
                            try: return n.attr.value in names
                            except Exception: return False
                        return False
                    return name_in2(l, A) and name_in2(r, B)
                if m.matches(val, m.BinaryOperation(operator=m.Subtract())) and has_names(val, WITHOUT_PV_NAMES, WITH_PV_NAMES):
                    new_call=cst.parse_expression(f"compute_annual_savings(electricity_costs_without_pv={val.left.code}, electricity_costs_with_pv={val.right.code}, default=0.0)")
                    self.changed=True; report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig.value.code, after=new_call.code, reason="without_with_difference"))
                    return updated.with_changes(value=new_call)
                if m.matches(val, m.BinaryOperation(operator=m.Add())):
                    l=val.left; r=val.right
                    if m.matches(l, m.BinaryOperation(operator=m.Subtract())) and has_names(l, WITHOUT_PV_NAMES, WITH_PV_NAMES):
                        if r.code and any(k in r.code for k in FEEDIN_EXTRA):
                            new_call=cst.parse_expression(f"compute_annual_savings(electricity_costs_without_pv={l.left.code}, electricity_costs_with_pv={l.right.code}, annual_feed_in_revenue={r.code}, default=0.0)")
                            self.changed=True; report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig.value.code, after=new_call.code, reason="diff_plus_feedin"))
                            return updated.with_changes(value=new_call)
                    if m.matches(r, m.BinaryOperation(operator=m.Subtract())) and has_names(r, WITHOUT_PV_NAMES, WITH_PV_NAMES):
                        if l.code and any(k in l.code for k in FEEDIN_EXTRA):
                            new_call=cst.parse_expression(f"compute_annual_savings(electricity_costs_without_pv={r.left.code}, electricity_costs_with_pv={r.right.code}, annual_feed_in_revenue={l.code}, default=0.0)")
                            self.changed=True; report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=orig.value.code, after=new_call.code, reason="feedin_plus_diff"))
                            return updated.with_changes(value=new_call)
                return updated
        tx=Tx(); new_mod=mod.visit(tx)
        if tx.changed and write:
            if not no_backup: write_text(path+".bak", code)
            write_text(path, new_mod.code); return True
        return tx.changed
    for p in list_py(root):
        try:
            if process(p): changed_files+=1
        except Exception as e:
            report.append(dict(file=p, lineno="?", before="", after="", reason=f"ERROR:{e}"))
    rep=os.path.join(out,"autopatch_annual_savings_report.csv")
    with open(rep,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=["file","lineno","before","after","reason"]); w.writeheader(); [w.writerow(r) for r in report]
    return changed_files, rep

# ---------- Autopatch project_data ----------
def autopatch_project_data(root:str, write:bool, no_backup:bool, out:str):
    cst, m = require_libcst(); ensure_dir(out); report=[]; changed_files=0
    def process(path:str)->bool:
        nonlocal report
        code=read_text(path); base=os.path.basename(path).lower()
        if base=="calculations.py":
            new=insert_def_if_missing_calculations(code, "build_project_data", BUILD_PD_DEF_CODE)
            if new!=code and write:
                if not no_backup: write_text(path+".bak", code)
                write_text(path, new); code=new
        try: mod=cst.parse_module(code)
        except Exception: return False
        class Tx(cst.CSTTransformer):
            def __init__(self): self.changed=False
            def leave_Module(self, orig, updated):
                if self.changed:
                    updated, imp=add_named_import(updated, "calculations", "build_project_data")
                    if imp: report.append(dict(file=path, lineno="1", before="(kein Import)", after="from calculations import build_project_data", reason="missing_import_added"))
                return updated
            def leave_SimpleStatementLine(self, orig, updated):
                if len(orig.body)==1 and m.matches(orig.body[0], m.Expr(value=m.Call(func=m.Attribute()))):
                    call=orig.body[0].value
                    if m.matches(call.func, m.Attribute(value=m.Name("project_data"), attr=m.Name("update"))):
                        arg_code = call.args[0].value.code if call.args else "{}"
                        repl = cst.parse_statement(f"project_data = build_project_data(project_data, {arg_code})\n")
                        self.changed=True; report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=call.code, after=repl.code.strip(), reason="project_data.update"))
                        return repl
                return updated
            def leave_Assign(self, orig, updated):
                if len(orig.targets)!=1 or not m.matches(orig.targets[0].target, m.Name("project_data")): return updated
                rhs=orig.value
                if m.matches(rhs, m.Dict()):
                    new=cst.parse_expression(f"build_project_data({rhs.code})"); self.changed=True
                    report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=rhs.code, after=new.code, reason="dict_literal_to_builder"))
                    return updated.with_changes(value=new)
                if m.matches(rhs, m.BinaryOperation(operator=m.BitOr())):
                    new=cst.parse_expression(f"build_project_data({rhs.left.code}, {rhs.right.code})"); self.changed=True
                    report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=rhs.code, after=new.code, reason="dict_union_to_builder"))
                    return updated.with_changes(value=new)
                if m.matches(rhs, m.Call()):
                    fname = rhs.func.attr.value if m.matches(rhs.func, m.Attribute()) else (rhs.func.value if m.matches(rhs.func, m.Name()) else "call")
                    new=cst.parse_expression(f"build_project_data({rhs.code})"); self.changed=True
                    reason = f"{fname}_to_builder" if str(fname).lower() in {"dict","merge","combine","deepmerge","update"} else "call_wrapped_to_builder"
                    report.append(dict(file=path, lineno=str(getattr(orig,'ln','?')), before=rhs.code, after=new.code, reason=reason))
                    return updated.with_changes(value=new)
                return updated
        tx=Tx(); new_mod=mod.visit(tx)
        if tx.changed and write:
            if not no_backup: write_text(path+".bak", code)
            write_text(path, new_mod.code); return True
        return tx.changed
    for p in list_py(root):
        try:
            if process(p): changed_files+=1
        except Exception as e:
            report.append(dict(file=p, lineno="?", before="", after="", reason=f"ERROR:{e}"))
    rep=os.path.join(out,"autopatch_project_data_report.csv")
    with open(rep,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=["file","lineno","before","after","reason"]); w.writeheader(); [w.writerow(r) for r in report]
    return changed_files, rep

# ---------- Structure & YAML ----------
def do_structure(root:str, out:str):
    import pandas as pd
    ensure_dir(out); rows=[]
    for r,_,f in os.walk(root):
        for fn in f:
            p=os.path.join(r,fn); rel=os.path.relpath(p, root); ext=os.path.splitext(fn)[1].lower()
            size=os.path.getsize(p) if os.path.exists(p) else None
            text=read_text(p) if ext in {".py",".ts",".tsx",".js",".json",".yml",".yaml",".md",".txt",".ini",".cfg"} else ""
            lines=text.count("\n")+1 if text else 0
            rows.append(dict(path=rel, ext=ext, size=size, lines=lines))
    df=pd.DataFrame(rows).sort_values("path")
    df.to_csv(os.path.join(out,"app_structure_manifest.csv"), index=False, encoding="utf-8")
    # trees
    from pathlib import Path
    def tree_text(root_dir, max_depth=3):
        lines=[]; root_path=Path(root_dir)
        for path in sorted(root_path.rglob("*")):
            rel=path.relative_to(root_path); 
            if len(rel.parts)==0: continue
            depth=len(rel.parts); 
            if depth>max_depth: continue
            lines.append(f"{'  '*(depth-1)}{'📁' if path.is_dir() else '📄'} {rel.name}")
        return "\n".join(lines)
    write_text(os.path.join(out,"app_tree_depth3.txt"), tree_text(root,3))
    all_lines=[]
    for p in sorted(Path(root).rglob("*")):
        rel=p.relative_to(Path(root)); 
        if len(rel.parts)==0: continue
        all_lines.append(f"{'  '*(len(rel.parts)-1)}{'📁' if p.is_dir() else '📄'} {rel.name}")
    write_text(os.path.join(out,"app_tree_full.txt"), "\n".join(all_lines))
    return True

def yaml_positions_check(root:str, out:str, tol_mm:float=0.2):
    ensure_dir(out)
    try: import yaml; loader=True
    except Exception: yaml=None; loader=False
    collisions=[]
    for path in list_yaml(root):
        try: text=read_text(path)
        except Exception: continue
        docs=[]
        if loader:
            try:
                for doc in yaml.safe_load_all(text):
                    if doc is not None: docs.append(doc)
            except Exception: docs=[]
        if not docs: continue
        def visit(o, file_path):
            if isinstance(o, dict):
                low={str(k).lower():k for k in o.keys()}
                def fk(cands):
                    for c in cands:
                        if c in low: return low[c]
                    return None
                xk=fk(("x","left")); yk=fk(("y","top")); pg=fk(("page","seite","p"))
                try:
                    x=float(o[xk]) if xk and o.get(xk) is not None else None
                    y=float(o[yk]) if yk and o.get(yk) is not None else None
                    p=int(o[pg]) if pg and o.get(pg) is not None else None
                except Exception:
                    x=y=p=None
                if x is not None and y is not None and p is not None:
                    collisions.append((file_path,p,x,y))
                for v in o.values(): visit(v, file_path)
            elif isinstance(o, list):
                for it in o: visit(it, file_path)
        for d in docs: visit(d, path)
    # simple grouping by tolerance
    groups=[]
    used=[False]*len(collisions)
    for i,a in enumerate(collisions):
        if used[i]: continue
        group=[a]; used[i]=True
        for j,b in enumerate(collisions):
            if used[j]: continue
            if a[0]==b[0] and a[1]==b[1] and abs(a[2]-b[2])<=tol_mm and abs(a[3]-b[3])<=tol_mm:
                group.append(b); used[j]=True
        if len(group)>1: groups.append(group)
    # write CSV
    import pandas as pd
    rows=[]
    for g in groups:
        for (file,p,x,y) in g:
            rows.append(dict(file=file, page=p, x=x, y=y))
        rows.append(dict(file="---", page="", x="", y=""))
    out_csv=os.path.join(out, "yaml_position_collisions.csv")
    pd.DataFrame(rows).to_csv(out_csv, index=False, encoding="utf-8")
    return out_csv

# ---------- CLI ----------
def main():
    ap=argparse.ArgumentParser(description="Kakerlake Ultra Cleaner")
    sub=ap.add_subparsers(dest="cmd", required=True)
    p=sub.add_parser("scan"); p.add_argument("root"); p.add_argument("--out", default="ultra_reports")
    p=sub.add_parser("autopatch-annual-savings"); p.add_argument("root"); p.add_argument("--out", default="ultra_reports"); p.add_argument("--write", action="store_true"); p.add_argument("--no-backup", action="store_true")
    p=sub.add_parser("autopatch-project-data"); p.add_argument("root"); p.add_argument("--out", default="ultra_reports"); p.add_argument("--write", action="store_true"); p.add_argument("--no-backup", action="store_true")
    p=sub.add_parser("structure"); p.add_argument("root"); p.add_argument("--out", default="ultra_reports")
    p=sub.add_parser("yaml-check"); p.add_argument("root"); p.add_argument("--out", default="ultra_reports"); p.add_argument("--tol-mm", type=float, default=0.2)
    p=sub.add_parser("all"); p.add_argument("root"); p.add_argument("--out", default="ultra_reports"); p.add_argument("--no-backup", action="store_true")
    args=ap.parse_args(); out=ensure_dir(args.out)
    if args.cmd=="scan": scan_python(args.root, out); print("SCAN fertig:", out); return
    if args.cmd=="autopatch-annual-savings":
        ch,rep=autopatch_annual_savings(args.root, write=args.write, no_backup=args.no_backup, out=out)
        print(f"Autopatch annual_savings: {ch} Dateien geändert. Report: {rep}"); return
    if args.cmd=="autopatch-project-data":
        ch,rep=autopatch_project_data(args.root, write=args.write, no_backup=args.no_backup, out=out)
        print(f"Autopatch project_data: {ch} Dateien geändert. Report: {rep}"); return
    if args.cmd=="structure": do_structure(args.root, out); print("STRUCTURE fertig:", out); return
    if args.cmd=="yaml-check": print("YAML-CHECK:", yaml_positions_check(args.root, out, tol_mm=args.tol_mm)); return
    if args.cmd=="all":
        do_structure(args.root, out); scan_python(args.root, out); yaml_positions_check(args.root, out, tol_mm=0.2)
        try: a_ch,a_rep=autopatch_annual_savings(args.root, write=True, no_backup=args.no_backup, out=out)
        except Exception as e: a_ch,a_rep=0,f"(ERROR:{e})"
        try: p_ch,p_rep=autopatch_project_data(args.root, write=True, no_backup=args.no_backup, out=out)
        except Exception as e: p_ch,p_rep=0,f"(ERROR:{e})"
        # zip
        import zipfile; zip_path=os.path.join(out,"ultra_reports.zip")
        with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
            for fn in os.listdir(out):
                if fn=="ultra_reports.zip": continue
                z.write(os.path.join(out,fn), arcname=fn)
        print("ALL fertig. Reports:", out, "ZIP:", zip_path); return

if __name__ == "__main__":
    main()
