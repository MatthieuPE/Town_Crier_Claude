"""Command line of the run tools: ``python3 tc.py <command> ...``.

Commands, in pipeline order: resolve, load (or import, as a fallback),
sheet, judge, finalize, paper, cut, verify, news, note, assemble, check.
Theme tools: validate-theme, theme-test. ``status`` shows the progress of a
run folder.
"""

import argparse
import datetime as dt
import json
import sys
import urllib.error
from pathlib import Path

from . import (assemble, candidates, checks, config as config_mod, data, files, fulltext, prefilter,
               selection as selection_mod, sheets, themes as themes_mod)

EXIT_ERRORS = 2
EXIT_NO_DATA = 3


def _print(*lines):
    """Print lines to stdout."""
    print("\n".join(str(x) for x in lines))


def _resolved(run_dir):
    """Resolved configuration of a run folder."""
    path = Path(run_dir) / "config.resolved.yaml"
    if not path.exists():
        raise SystemExit(f"error: {path} not found; run `tc.py resolve` first")
    return files.read_yaml(path)


def _subsection(resolved, sid):
    """One resolved subsection."""
    for sub in config_mod.iter_subsections(resolved):
        if sub["id"] == sid:
            return sub
    raise SystemExit(f"error: no subsection {sid}")


def _records(run_dir):
    """Candidate records of a run, by paper id."""
    return {r["paper_id"]: r for r in files.read_jsonl(Path(run_dir) / "candidates.jsonl")}


def add_note(run_dir, text):
    """Append a note shown at the top of the digest (no duplicates)."""
    path = Path(run_dir) / "notes.json"
    notes = files.read_json(path, [])
    if text not in [n["text"] for n in notes]:
        notes.append({"text": text})
        files.write_json(path, notes)


def cmd_resolve(args):
    """Merge, resolve and check the configuration; create the run folder."""
    cfg = config_mod.load(args.config)
    if args.data_dir:
        cfg.setdefault("data", {})["local_dir"] = str(Path(args.data_dir).resolve())
    local = themes_mod.load_local(config_mod.SKILLS_DIR)
    remote, data_warning = {}, None
    try:
        source = data.DataSource(repository=(cfg.get("data") or {}).get("repository"),
                                 branch=(cfg.get("data") or {}).get("branch", "data"),
                                 local_dir=(cfg.get("data") or {}).get("local_dir"))
        remote = source.index().get("themes") or {}
    except (FileNotFoundError, ValueError, urllib.error.URLError, OSError) as exc:
        data_warning = f"data index not readable ({exc}); using installed themes only"
    all_themes = themes_mod.merge(local, remote)
    run_date = dt.date.fromisoformat(args.run_date) if args.run_date else dt.date.today()
    try:
        resolved = config_mod.resolve(cfg, all_themes, run_date, anchor=args.anchor)
    except ValueError as exc:
        _print(f"ERROR {exc}")
        return EXIT_ERRORS
    errors, warnings = config_mod.validate(cfg, resolved, all_themes)
    if data_warning:
        warnings.append(data_warning)
    p = resolved["period"]
    _print(f"period: {p['start']} -> {p['end']} ({p['n_days']} days, {p['anchor']})")
    for sub in config_mod.iter_subsections(resolved):
        _print(f"  {sub['id']} {sub['title']} | theme {sub['theme']} | category {sub['category']} | "
               f"{sub['n_papers']} paper(s) | extract: {sub['skills']['extract']} | "
               f"summarize: {sub['skills']['summarize']}")
    _print(*(f"WARNING {w}" for w in warnings))
    if errors:
        _print(*(f"ERROR {e}" for e in errors))
        return EXIT_ERRORS
    if args.dry_run:
        _print("configuration OK (dry run, no run folder created)")
        return 0
    run_dir = Path(args.out) / f"{p['start']}_{p['end']}"
    run_dir.mkdir(parents=True, exist_ok=True)
    files.write_yaml(run_dir / "config.resolved.yaml", resolved)
    if not (run_dir / "notes.json").exists():
        files.write_json(run_dir / "notes.json", [])
    _print(f"run folder: {run_dir.resolve()}")
    return 0


def cmd_load(args):
    """Read the period's papers and build the stage-1 pools."""
    run_dir = Path(args.run)
    resolved = _resolved(run_dir)
    source = data.from_config(resolved, run_dir=run_dir, local_dir=args.data_dir)
    try:
        index = source.index()
    except (FileNotFoundError, urllib.error.URLError, OSError) as exc:
        _print(f"ERROR data not available: {exc}",
               "Fallback: see the fetch-papers skill (alphaXiv search, counts unknown).")
        return EXIT_NO_DATA
    days = candidates.period_days(resolved)
    records, notes = candidates.collect(source, index, candidates.needed_databases(resolved), days)
    notes += candidates.coverage_notes(index, resolved, days[0])
    pools, cands = candidates.build_pools(resolved, records)
    files.write_jsonl(run_dir / "candidates.jsonl", cands.values())
    files.write_json(run_dir / "pools.json", pools)
    for note in notes:
        add_note(run_dir, note)
    limit = int((resolved.get("selection") or {}).get("title_screen_above", 120))
    _print(f"{len(records)} papers in the period; {len(cands)} candidates")
    for sub in config_mod.iter_subsections(resolved):
        n = len(pools[sub["id"]])
        mode = "titles first" if n > limit else "abstracts"
        _print(f"  {sub['id']} {sub['title']}: {n} candidates -> review {mode}")
    _print(*(f"NOTE {n}" for n in notes))
    return 0


IMPORT_REQUIRED = ("paper_id", "title", "url", "found_for")


def cmd_import(args):
    """Add papers found by search (fallback); their subsections get unknown counts."""
    run_dir = Path(args.run)
    resolved = _resolved(run_dir)
    subs = [s["id"] for s in config_mod.iter_subsections(resolved)]
    rows = files.read_jsonl(args.file)
    errors = []
    for i, row in enumerate(rows, 1):
        missing = [k for k in IMPORT_REQUIRED if not row.get(k)]
        if missing:
            errors.append(f"line {i}: missing {', '.join(missing)}")
        elif not str(row["url"]).startswith(("http://", "https://")):
            errors.append(f"line {i}: url must start with http(s)://")
        elif set(row["found_for"]) - set(subs):
            errors.append(f"line {i}: unknown subsection(s) {sorted(set(row['found_for']) - set(subs))}")
    if errors:
        _print(*(f"ERROR {e}" for e in errors))
        return EXIT_ERRORS
    cands = _records(run_dir)
    pools = files.read_json(run_dir / "pools.json", {}) or {}
    for sid in subs:
        pools.setdefault(sid, [])
    touched = set()
    for row in rows:
        rec = cands.get(row["paper_id"]) or {
            "source": row.get("source", "search"), "abstract": "", "authors": [], "categories": [],
            "html_url": None, "doi": None, "comment": None, "journal_ref": None, "version": 1,
            "first_seen": row.get("published") or resolved["period"]["end"], "found_for": []}
        rec.update({k: v for k, v in row.items() if k != "found_for"})
        rec["found_for"] = sorted(set(rec.get("found_for") or []) | set(row["found_for"]))
        cands[row["paper_id"]] = rec
        for sid in row["found_for"]:
            if row["paper_id"] not in pools[sid]:
                pools[sid].append(row["paper_id"])
            touched.add(sid)
    files.write_jsonl(run_dir / "candidates.jsonl", cands.values())
    files.write_json(run_dir / "pools.json", pools)
    fallback = files.read_json(run_dir / "fallback.json", {})
    fallback.update({sid: args.reason for sid in touched})
    files.write_json(run_dir / "fallback.json", fallback)
    add_note(run_dir, f"Subsection(s) {', '.join(sorted(touched))}: papers found by search ({args.reason}); "
                      "counts are unknown and lists may be incomplete.")
    _print(f"imported {len(rows)} paper(s) into {', '.join(sorted(touched))}")
    return 0


def cmd_sheet(args):
    """Print the review sheet of a subsection."""
    run_dir = Path(args.run)
    sub = _subsection(_resolved(run_dir), args.sub)
    pool = files.read_json(run_dir / "pools.json", {}).get(args.sub, [])
    if args.ids:
        wanted = set(args.ids.split(","))
        pool = [p for p in pool if p in wanted]
    recs = _records(run_dir)
    _print(sheets.render(sub, [recs[p] for p in pool], titles_only=args.titles))
    return 0


def cmd_judge(args):
    """Parse and check a subsection's judgments; save them."""
    run_dir = Path(args.run)
    sub = _subsection(_resolved(run_dir), args.sub)
    pool = files.read_json(run_dir / "pools.json", {}).get(args.sub, [])
    try:
        judgments = selection_mod.parse(Path(args.file).read_text(encoding="utf-8"))
    except ValueError as exc:
        _print(f"ERROR {exc}")
        return EXIT_ERRORS
    errors = selection_mod.validate(judgments, pool, sub["category"])
    if errors:
        _print(*(f"ERROR {e}" for e in errors))
        return EXIT_ERRORS
    files.write_json(run_dir / "judgments" / f"{args.sub}.json", [j.__dict__ for j in judgments])
    on = sum(j.on_theme for j in judgments)
    _print(f"{args.sub}: {len(judgments)} judged, {on} on theme")
    return 0


def cmd_finalize(args):
    """Choose summaries and lists; count papers per subsection."""
    run_dir = Path(args.run)
    resolved = _resolved(run_dir)
    pools = files.read_json(run_dir / "pools.json", {})
    judged, missing = {}, []
    for sub in config_mod.iter_subsections(resolved):
        raw = files.read_json(run_dir / "judgments" / f"{sub['id']}.json")
        if raw is None and pools.get(sub["id"]):
            missing.append(sub["id"])
        judged[sub["id"]] = [selection_mod.Judgment(**j) for j in raw or []]
    if missing:
        _print(f"ERROR no judgments yet for subsection(s) {', '.join(missing)}")
        return EXIT_ERRORS
    fallback = files.read_json(run_dir / "fallback.json", {})
    sel = selection_mod.finalize(resolved, pools, judged, _records(run_dir), uncounted=fallback)
    files.write_json(run_dir / "selection.json", sel)
    for sub in config_mod.iter_subsections(resolved):
        s = sel["subsections"][sub["id"]]
        _print(f"{sub['id']} {sub['title']} (category {sub['category']}): count {s['count']}, "
               f"{len(s['summaries'])} summary(ies), {len(s['list'])} listed")
        for j in s["summaries"]:
            full = sub["category"] == 1 and sub["full_text"]["source"] == "alphaxiv"
            _print(f"  - {j['paper_id']} [{'full text' if full else 'abstract'}] "
                   f"{sel['papers'][j['paper_id']]['title']}")
    return 0


def cmd_paper(args):
    """Print one candidate record."""
    rec = _records(args.run).get(args.id)
    if not rec:
        _print(f"ERROR {args.id} is not a candidate of this run")
        return EXIT_ERRORS
    _print(json.dumps(rec, ensure_ascii=False, indent=1))
    return 0


def cmd_cut(args):
    """Keep the configured sections of a saved full text."""
    run_dir = Path(args.run)
    resolved = _resolved(run_dir)
    sel = files.read_json(run_dir / "selection.json", {})
    sections = args.sections.split(",") if args.sections else None
    for sub in config_mod.iter_subsections(resolved):
        picked = [j["paper_id"] for j in sel.get("subsections", {}).get(sub["id"], {}).get("summaries", [])]
        if args.paper in picked and sub["category"] == 1 and not sections:
            sections = sub["full_text"]["sections"]
    sections = sections or ["abstract", "methods", "results", "conclusions"]
    rec = _records(run_dir).get(args.paper, {})
    dst = run_dir / "fulltext" / f"{files.safe_name(args.paper)}.txt"
    stats = fulltext.cut_file(args.input, dst, sections, abstract=rec.get("abstract"))
    _print(f"written {dst} (~{stats['approx_tokens_out']} tokens, from {stats['chars_in']} characters)",
           f"sections kept: {', '.join(stats['kept'])}; missing: {', '.join(stats['missing']) or 'none'}")
    if stats["truncated"]:
        _print("WARNING output truncated to the size cap")
    return 0


def cmd_verify(args):
    """Record the source quote of a number flagged by the check."""
    path = Path(args.run) / "verified.json"
    verified = files.read_json(path, {})
    verified.setdefault(args.paper, []).append({"number": args.number, "quote": args.quote})
    files.write_json(path, verified)
    _print(f"recorded quote for {args.number} in {args.paper}")
    return 0


def cmd_news(args):
    """Record the news article found for a category-3 paper."""
    if not args.url.startswith(("http://", "https://")):
        _print("ERROR url must start with http(s)://")
        return EXIT_ERRORS
    path = Path(args.run) / "news.json"
    news = files.read_json(path, {})
    news[args.paper] = {"url": args.url, "outlet": args.outlet}
    files.write_json(path, news)
    _print(f"news link recorded for {args.paper}")
    return 0


def cmd_note(args):
    """Add a note to the top of the digest."""
    add_note(args.run, args.text)
    _print("note added")
    return 0


def cmd_assemble(args):
    """Build the digest file."""
    _print(f"digest: {assemble.write(args.run).resolve()}")
    return 0


def cmd_check(args):
    """Run accuracy and format checks."""
    report = checks.run(args.run)
    _print(*(f"ERROR {e}" for e in report["errors"]), *(f"WARNING {w}" for w in report["warnings"]))
    _print(f"{len(report['errors'])} error(s), {len(report['warnings'])} warning(s)")
    return 1 if report["errors"] else 0


def cmd_validate_theme(args):
    """Check a theme definition file."""
    path = Path(args.theme)
    theme = files.read_yaml(path)
    folder = path.parent.name
    expected = folder.removeprefix("theme-") if folder.startswith("theme-") else None
    errors = themes_mod.validate(theme, expected)
    _print(*([f"ERROR {e}" for e in errors] or ["theme OK"]))
    return EXIT_ERRORS if errors else 0


def cmd_theme_test(args):
    """Count the papers a theme's stage-1 filter keeps over the last days."""
    theme = files.read_yaml(args.theme)
    errors = themes_mod.validate(theme)
    if errors:
        _print(*(f"ERROR {e}" for e in errors))
        return EXIT_ERRORS
    source = data.DataSource(repository=args.repository, branch=args.branch, local_dir=args.data_dir)
    try:
        index = source.index()
    except (FileNotFoundError, urllib.error.URLError, OSError) as exc:
        _print(f"ERROR data not available: {exc}")
        return EXIT_NO_DATA
    end = dt.date.fromisoformat(index.get("last_run_day") or dt.date.today().isoformat())
    days = [end - dt.timedelta(days=i) for i in range(args.days)][::-1]
    scopes = themes_mod.scopes(theme)
    records, _ = candidates.collect(source, index, sorted(scopes), days)
    filt = prefilter.ThemeFilter.from_theme(theme)
    kept = sorted((r for r in records.values() if filt.passes(r)),
                  key=lambda r: r.get("first_seen", ""), reverse=True)
    in_scope = sum(filt.in_scope(r) for r in records.values())
    _print(f"last {args.days} days ({days[0]} -> {days[-1]}): {in_scope} papers in scope, "
           f"{len(kept)} pass the keywords")
    for rec in kept[:args.samples]:
        _print(f"  - {rec['paper_id']} | {rec['title']}")
    for db, scope_list in scopes.items():
        coverage = ((index.get("databases") or {}).get(db) or {}).get("coverage") or {}
        missing = [s for s in scope_list if s not in coverage]
        if missing:
            _print(f"NOTE {db} {', '.join(missing)} not fetched yet: available after the next daily fetch")
    return 0


def cmd_status(args):
    """Show which steps of a run are done."""
    run_dir = Path(args.run)
    resolved = _resolved(run_dir)
    sel = files.read_json(run_dir / "selection.json")
    _print(f"period {resolved['period']['start']} -> {resolved['period']['end']}",
           f"candidates: {'yes' if (run_dir / 'candidates.jsonl').exists() else 'no'}",
           f"selection: {'yes' if sel else 'no'}")
    for sub in config_mod.iter_subsections(resolved):
        judged = (run_dir / "judgments" / f"{sub['id']}.json").exists()
        summary = (run_dir / "summaries" / f"{sub['id']}.md").exists()
        _print(f"  {sub['id']}: judged {'yes' if judged else 'no'}, summaries {'yes' if summary else 'no'}")
    _print(f"digest: {'yes' if assemble.output_path(run_dir, resolved).exists() else 'no'}")
    return 0


def build_parser():
    """Argument parser with one sub-command per step."""
    parser = argparse.ArgumentParser(prog="tc.py", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("resolve", help="check the configuration and create the run folder")
    p.add_argument("--config", help="user configuration: file or URL")
    p.add_argument("--run-date", help="YYYY-MM-DD (default: today)")
    p.add_argument("--anchor", choices=["rolling", "calendar"], help="override period.anchor")
    p.add_argument("--out", default="town-crier-runs", help="parent of run folders")
    p.add_argument("--data-dir", help="local data folder instead of GitHub")
    p.add_argument("--dry-run", action="store_true", help="check only")
    p.set_defaults(func=cmd_resolve)

    p = sub.add_parser("load", help="read the period's papers; build stage-1 pools")
    p.add_argument("--run", required=True)
    p.add_argument("--data-dir")
    p.set_defaults(func=cmd_load)

    p = sub.add_parser("import", help="add papers found by search (fallback)")
    p.add_argument("--run", required=True)
    p.add_argument("--file", required=True,
                   help="JSON lines: paper_id, title, url, found_for [, abstract, authors, published, journal]")
    p.add_argument("--reason", required=True, help="why search was needed, shown in the notes")
    p.set_defaults(func=cmd_import)

    p = sub.add_parser("sheet", help="print a subsection's review sheet")
    p.add_argument("--run", required=True)
    p.add_argument("--sub", required=True)
    p.add_argument("--titles", action="store_true", help="titles only")
    p.add_argument("--ids", help="comma-separated paper ids")
    p.set_defaults(func=cmd_sheet)

    p = sub.add_parser("judge", help="save a subsection's judgments")
    p.add_argument("--run", required=True)
    p.add_argument("--sub", required=True)
    p.add_argument("--file", required=True, help="judgment lines: id | y/n | score | kind | field | reason")
    p.set_defaults(func=cmd_judge)

    p = sub.add_parser("finalize", help="choose summaries and lists, count papers")
    p.add_argument("--run", required=True)
    p.set_defaults(func=cmd_finalize)

    p = sub.add_parser("paper", help="print one candidate record")
    p.add_argument("--run", required=True)
    p.add_argument("--id", required=True)
    p.set_defaults(func=cmd_paper)

    p = sub.add_parser("cut", help="keep the configured sections of a saved full text")
    p.add_argument("--run", required=True)
    p.add_argument("--paper", required=True)
    p.add_argument("--input", required=True, help="saved alphaXiv result or text file")
    p.add_argument("--sections", help="comma-separated, overrides the configuration")
    p.set_defaults(func=cmd_cut)

    p = sub.add_parser("verify", help="record where a flagged number appears in the paper")
    p.add_argument("--run", required=True)
    p.add_argument("--paper", required=True)
    p.add_argument("--number", required=True)
    p.add_argument("--quote", required=True, help="exact text of the paper holding the number")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("news", help="record the news article of a category-3 paper")
    p.add_argument("--run", required=True)
    p.add_argument("--paper", required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--outlet", required=True)
    p.set_defaults(func=cmd_news)

    p = sub.add_parser("note", help="add a note to the top of the digest")
    p.add_argument("--run", required=True)
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_note)

    p = sub.add_parser("assemble", help="build the digest file")
    p.add_argument("--run", required=True)
    p.set_defaults(func=cmd_assemble)

    p = sub.add_parser("check", help="accuracy and format checks")
    p.add_argument("--run", required=True)
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("validate-theme", help="check a theme.yaml")
    p.add_argument("--theme", required=True)
    p.set_defaults(func=cmd_validate_theme)

    p = sub.add_parser("theme-test", help="try a theme's filter on the last days of data")
    p.add_argument("--theme", required=True, help="theme.yaml path")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--samples", type=int, default=5)
    p.add_argument("--repository", default="MatthieuPE/Town_Crier_Claude")
    p.add_argument("--branch", default="data")
    p.add_argument("--data-dir")
    p.set_defaults(func=cmd_theme_test)

    p = sub.add_parser("status", help="progress of a run folder")
    p.add_argument("--run", required=True)
    p.set_defaults(func=cmd_status)
    return parser


def main(argv=None):
    """Run one command; returns the exit code."""
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
