#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kakerlake_ultra_cleaner_v3.py
- Fix: LibCST nodes haben kein ".code" Attribut -> sichere helper code_for()
- Debug-Ausgaben stabil (kein AttributeError mehr)
- Ignoriert Patch-/Insert-Fragmente (*/patches/*, *.insert.py)
- Loggt PARSE_ERROR statt Abbruch
"""
from __future__ import annotations
import os, sys, csv, argparse
from typing import Any, Dict, List, Optional, Tuple, Set

def read_text(path:str)->str:
    return open(path, "r", encoding="utf-8", errors="ignore").read()

def write_text(path:str, text:str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(text)

def ensure_dir(p:str):
    os.makedirs(p, exist_ok=True); return p

def list_py(root:str)->List[str]:
    out=[]; 
    for r,_,f in os.walk(root):
        for fn in f:
            if not fn.endswith(".py"): 
                continue
            p=os.path.join(r,fn)
            # Skip Fragmente/Generator-Patches
            low=p.lower()
            if ("{}patches{}".format(os.sep, os.sep) in low) or low.endswith(".insert.py"):
                continue
            out.append(p)
    return out

# ---------- LibCST helpers ----------
def require_libcst():
    try:
        import libcst as cst
        import libcst.matchers as m
        return cst, m
    except Exception:
        print("Bitte installieren: pip install libcst", file=sys.stderr); raise

# Sicherer Serializer für Teilbäume
def code_for(node) -> str:
    cst, _ = require_libcst()
    try:
        mod = cst.Module([])
        return mod.code_for_node(node)
    except Exception:
        try:
            return str(node)
        except Exception:
            return ""

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

# ---------- Autopatch annual_savings ----------
RESULT_KEYS = {'annual_total_savings_euro','annual_financial_benefit_year1','annual_savings_consumption_eur','jahresersparnis_gesamt','total_annual_savings','annual_savings','annual_savings_total_euro'}
FEEDIN_NAMES = {'annual_feedin_revenue','feed_in_revenue','annual_feed_in_revenue','annual_revenue_feed_in_eur'}
CONSUMP_SAVINGS_NAMES = {'annual_electricity_savings','consumption_savings','annual_savings_consumption_eur'}
OLD_COST_NAMES = {'annual_old_cost','old_annual_cost','annual_cost_old'}
HP_COST_NAMES  = {'annual_hp_cost','hp_annual_cost','annual_cost_hp'}
WITHOUT_PV_NAMES={'electricity_costs_without_pv','cost_without_pv','annual_cost_without_pv'}
WITH_PV_NAMES={'electricity_costs_with_pv','cost_with_pv','annual_cost_with_pv'}
FEEDIN_EXTRA = {'annual_feed_in_revenue','annual_feedin_revenue','feed_in_revenue','annual_revenue_feed_in_eur'}

def autopatch_annual_savings(root:str, write:bool, out:str, no_backup:bool=False, debug:bool=False):
    cst, m = require_libcst(); ensure_dir(out); report=[]; changed_files=0

    def log(file, lineno, before, after, reason):
        report.append(dict(file=file, lineno=str(lineno), before=before, after=after, reason=reason))
        if debug:
            print(f"[{file}:{lineno}] {reason}")
            if before: print("  BEFORE:", before[:200].replace("\n"," "))
            if after:  print("  AFTER :", after[:200].replace("\n"," "))

    def process(path:str)->bool:
        # Skip non-root code? (already filtered)
        code = read_text(path)
        base = os.path.basename(path).lower()
        if base == "calculations.py":
            newc = insert_def_if_missing_calculations(code, "compute_annual_savings", COMPUTE_DEF_CODE)
            if newc != code and write:
                if not no_backup: write_text(path+".bak", code)
                write_text(path, newc)
                code = newc

        try:
            mod = cst.parse_module(code)
        except Exception as e:
            log(path, "?", "", "", f"PARSE_ERROR:{e}")
            return False

        class Tx(cst.CSTTransformer):
            def __init__(self): self.changed=False
            def leave_Module(self, orig, updated):
                if self.changed:
                    updated, imp = add_named_import(updated, "calculations", "compute_annual_savings")
                    if imp: log(path, 1, "(kein Import)", "from calculations import compute_annual_savings", "missing_import_added")
                return updated
            def leave_Assign(self, orig, updated):
                try:
                    tgt = orig.targets[0].target if len(orig.targets)==1 else None
                except Exception:
                    return updated
                if not m.matches(tgt, m.Name("annual_savings")):
                    return updated
                rhs = orig.value
                rhs_code = code_for(rhs)

                # 1) results_like.get('KEY', default)
                if m.matches(rhs, m.Call(func=m.Attribute(attr=m.Name("get")))):
                    call = rhs
                    if call.args and m.matches(call.args[0].value, m.SimpleString()):
                        key = call.args[0].value.value.strip('\'"')
                        if key in RESULT_KEYS:
                            default_expr = code_for(call.args[1].value) if len(call.args)>=2 else "0.0"
                            new_call = cst.parse_expression(f"compute_annual_savings(results={code_for(call.func.value)}, default={default_expr})")
                            self.changed=True; log(path, getattr(orig,'ln','?'), rhs_code, code_for(new_call), "results_get_to_compute")
                            return updated.with_changes(value=new_call)

                # 2) dict_like['KEY']
                if m.matches(rhs, m.Subscript(value=m.DoNotCare(), slice=m.SubscriptElement())):
                    sub = rhs
                    try:
                        if m.matches(sub.slice, m.Index(value=m.SimpleString())):
                            key = sub.slice.value.value.strip('\'"')
                            if key in RESULT_KEYS:
                                new_call = cst.parse_expression(f"compute_annual_savings(results={code_for(sub.value)}, default=0.0)")
                                self.changed=True; log(path, getattr(orig,'ln','?'), rhs_code, code_for(new_call), "dict_index_to_compute")
                                return updated.with_changes(value=new_call)
                    except Exception:
                        pass

                # 3) feed_in + consumption
                if m.matches(rhs, m.BinaryOperation(operator=m.Add())):
                    l=rhs.left; r=rhs.right
                    def name_in(node, names:Set[str]):
                        if m.matches(node, m.Name()): 
                            return node.value if node.value in names else None
                        if m.matches(node, m.Attribute()):
                            try: 
                                return node.attr.value if node.attr.value in names else None
                            except Exception: return None
                        return None
                    f1 = name_in(l, FEEDIN_NAMES) or name_in(r, FEEDIN_NAMES)
                    c1 = name_in(l, CONSUMP_SAVINGS_NAMES) or name_in(r, CONSUMP_SAVINGS_NAMES)
                    if f1 and c1:
                        feed = l if name_in(l, FEEDIN_NAMES) else r
                        cons = r if feed is l else l
                        new_call = cst.parse_expression(f"compute_annual_savings(annual_feedin_revenue={code_for(feed)}, annual_electricity_savings={code_for(cons)}, default=0.0)")
                        self.changed=True; log(path, getattr(orig,'ln','?'), rhs_code, code_for(new_call), "feedin_plus_consumption")
                        return updated.with_changes(value=new_call)

                # 4) old - hp
                if m.matches(rhs, m.BinaryOperation(operator=m.Subtract())):
                    l=rhs.left; r=rhs.right
                    def name_is(node, names:Set[str]):
                        if m.matches(node, m.Name()): return node.value in names
                        if m.matches(node, m.Attribute()):
                            try: return node.attr.value in names
                            except Exception: return False
                        return False
                    if name_is(l, OLD_COST_NAMES) and name_is(r, HP_COST_NAMES):
                        new_call = cst.parse_expression(f"compute_annual_savings(annual_old_cost={code_for(l)}, annual_hp_cost={code_for(r)}, default=0.0)")
                        self.changed=True; log(path, getattr(orig,'ln','?'), rhs_code, code_for(new_call), "old_minus_hp")
                        return updated.with_changes(value=new_call)

                # 5) (without - with) (+ feedin)
                def diff_names(node):
                    if not m.matches(node, m.BinaryOperation(operator=m.Subtract())): return None
                    l=node.left; r=node.right
                    def name_in2(n, names:Set[str]):
                        if m.matches(n, m.Name()): return n.value in names
                        if m.matches(n, m.Attribute()):
                            try: return n.attr.value in names
                            except Exception: return False
                        return False
                    return (l,r) if name_in2(l, WITHOUT_PV_NAMES) and name_in2(r, WITH_PV_NAMES) else None
                d = diff_names(rhs)
                if d:
                    new_call = cst.parse_expression(f"compute_annual_savings(electricity_costs_without_pv={code_for(d[0])}, electricity_costs_with_pv={code_for(d[1])}, default=0.0)")
                    self.changed=True; log(path, getattr(orig,'ln','?'), rhs_code, code_for(new_call), "without_with_difference")
                    return updated.with_changes(value=new_call)
                if m.matches(rhs, m.BinaryOperation(operator=m.Add())):
                    l=rhs.left; r=rhs.right
                    d=diff_names(l)
                    if d and any(k in code_for(r) for k in FEEDIN_EXTRA):
                        new_call = cst.parse_expression(f"compute_annual_savings(electricity_costs_without_pv={code_for(d[0])}, electricity_costs_with_pv={code_for(d[1])}, annual_feed_in_revenue={code_for(r)}, default=0.0)")
                        self.changed=True; log(path, getattr(orig,'ln','?'), rhs_code, code_for(new_call), "diff_plus_feedin")
                        return updated.with_changes(value=new_call)
                    d=diff_names(r)
                    if d and any(k in code_for(l) for k in FEEDIN_EXTRA):
                        new_call = cst.parse_expression(f"compute_annual_savings(electricity_costs_without_pv={code_for(d[0])}, electricity_costs_with_pv={code_for(d[1])}, annual_feed_in_revenue={code_for(l)}, default=0.0)")
                        self.changed=True; log(path, getattr(orig,'ln','?'), rhs_code, code_for(new_call), "feedin_plus_diff")
                        return updated.with_changes(value=new_call)
                return updated

        tx=Tx(); new_mod = mod.visit(tx)
        if tx.changed:
            if write:
                write_text(path+".bak", code) if not no_backup else None
                write_text(path, new_mod.code)
            return True
        return False

    for p in list_py(root):
        try:
            if process(p): changed_files += 1
        except Exception as e:
            log(p, "?", "", "", f"ERROR:{e}")

    rep=os.path.join(out,"autopatch_annual_savings_report.csv")
    with open(rep,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=["file","lineno","before","after","reason"]); w.writeheader(); [w.writerow(r) for r in report]
    return changed_files, rep

# ---------- Autopatch project_data ----------
def autopatch_project_data(root:str, write:bool, out:str, no_backup:bool=False, debug:bool=False):
    cst, m = require_libcst(); ensure_dir(out); report=[]; changed_files=0
    def log(file, lineno, before, after, reason):
        report.append(dict(file=file, lineno=str(lineno), before=before, after=after, reason=reason))
        if debug: print(f"[{file}:{lineno}] {reason}")
    def process(path:str)->bool:
        code = read_text(path); base = os.path.basename(path).lower()
        if base == "calculations.py":
            newc = insert_def_if_missing_calculations(code, "build_project_data", BUILD_PD_DEF_CODE)
            if newc != code and write:
                write_text(path+".bak", code) if not no_backup else None
                write_text(path, newc); code = newc
        try:
            mod = cst.parse_module(code)
        except Exception as e:
            log(path, "?", "", "", f"PARSE_ERROR:{e}")
            return False

        class Tx(cst.CSTTransformer):
            def __init__(self): self.changed=False
            def leave_Module(self, orig, updated):
                if self.changed:
                    updated, imp = add_named_import(updated, "calculations", "build_project_data")
                    if imp: log(path, 1, "(kein Import)", "from calculations import build_project_data", "missing_import_added")
                return updated
            def leave_SimpleStatementLine(self, orig, updated):
                if len(orig.body)==1 and m.matches(orig.body[0], m.Expr(value=m.Call(func=m.Attribute()))):
                    call=orig.body[0].value
                    if m.matches(call.func, m.Attribute(value=m.Name("project_data"), attr=m.Name("update"))):
                        arg_code = code_for(call.args[0].value) if call.args else "{}"
                        repl = cst.parse_statement(f"project_data = build_project_data(project_data, {arg_code})\n")
                        self.changed=True; log(path, getattr(orig,'ln','?'), code_for(call), repl.code.strip(), "project_data.update")
                        return repl
                return updated
            def leave_Assign(self, orig, updated):
                if len(orig.targets)!=1 or not m.matches(orig.targets[0].target, m.Name("project_data")): return updated
                rhs=orig.value
                if m.matches(rhs, m.Dict()):
                    new = cst.parse_expression(f"build_project_data({code_for(rhs)})"); self.changed=True
                    log(path, getattr(orig,'ln','?'), code_for(rhs), code_for(new), "dict_literal_to_builder")
                    return updated.with_changes(value=new)
                if m.matches(rhs, m.BinaryOperation(operator=m.BitOr())):
                    new = cst.parse_expression(f"build_project_data({code_for(rhs.left)}, {code_for(rhs.right)})"); self.changed=True
                    log(path, getattr(orig,'ln','?'), code_for(rhs), code_for(new), "dict_union_to_builder")
                    return updated.with_changes(value=new)
                if m.matches(rhs, m.Call()):
                    new = cst.parse_expression(f"build_project_data({code_for(rhs)})"); self.changed=True
                    log(path, getattr(orig,'ln','?'), code_for(rhs), code_for(new), "call_wrapped_to_builder")
                    return updated.with_changes(value=new)
                return updated
        tx=Tx(); new_mod = mod.visit(tx)
        if tx.changed:
            if write:
                write_text(path+".bak", code) if not no_backup else None
                write_text(path, new_mod.code)
            return True
        return False
    for p in list_py(root):
        try:
            if process(p): changed_files += 1
        except Exception as e:
            log(p, "?", "", "", f"ERROR:{e}")
    rep=os.path.join(out,"autopatch_project_data_report.csv")
    with open(rep,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=["file","lineno","before","after","reason"]); w.writeheader(); [w.writerow(r) for r in report]
    return changed_files, rep

# ---------- CLI ----------
def main():
    ap=argparse.ArgumentParser(description="Kakerlake Ultra Cleaner v3 (stabilisiert)")
    sub=ap.add_subparsers(dest="cmd", required=True)
    p=sub.add_parser("autopatch-annual-savings"); p.add_argument("root"); p.add_argument("--out", default="ultra_reports"); p.add_argument("--write", action="store_true"); p.add_argument("--no-backup", action="store_true"); p.add_argument("--debug", action="store_true")
    p=sub.add_parser("autopatch-project-data"); p.add_argument("root"); p.add_argument("--out", default="ultra_reports"); p.add_argument("--write", action="store_true"); p.add_argument("--no-backup", action="store_true"); p.add_argument("--debug", action="store_true")
    args=ap.parse_args(); ensure_dir(args.out)
    if args.cmd=="autopatch-annual-savings":
        ch,rep=autopatch_annual_savings(args.root, write=args.write, out=args.out, no_backup=args.no_backup, debug=args.debug)
        print(f"Autopatch annual_savings: {ch} Dateien geändert. Report: {rep}"); return
    if args.cmd=="autopatch-project-data":
        ch,rep=autopatch_project_data(args.root, write=args.write, out=args.out, no_backup=args.no_backup, debug=args.debug)
        print(f"Autopatch project_data: {ch} Dateien geändert. Report: {rep}"); return

if __name__ == "__main__":
    main()
