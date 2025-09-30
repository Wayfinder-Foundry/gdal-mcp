from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import frontmatter
import typer

app = typer.Typer(add_completion=False)


def _emit(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _hash_text(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9-_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "item"


def _frontmatter(md: Dict[str, Any]) -> str:
    # Keep only expected keys to avoid leaking extra metadata
    data = {
        k: v
        for k, v in md.items()
        if v is not None and k in {"type", "id", "title", "tags", "links"}
    }
    import yaml  # pyyaml

    return "---\n" + yaml.safe_dump(data, sort_keys=False).strip() + "\n---\n\n"


@app.command()
def main(
    root: Path = typer.Option(Path("docs"), exists=True, file_okay=False),
    emit_dir: Path = typer.Option(Path("conport_export"), file_okay=False),
    only: Optional[str] = typer.Option(None, help="Comma list of types to include"),
    dry_run: bool = typer.Option(False, help="Do not write artifacts"),
    verbose: bool = typer.Option(False, help="Verbose output"),
) -> None:
    """Ingest markdown docs with frontmatter and emit ConPort-friendly artifacts.

    Types supported: product_context, decision, system_pattern, glossary, usage.
    """
    include_types = set(t.strip() for t in (only or "").split(",") if t.strip())
    artifacts: List[Dict[str, Any]] = []

    for p in root.rglob("*.md"):
        post = frontmatter.load(p)
        meta = post.metadata or {}
        typ = (meta.get("type") or "").strip()
        title = meta.get("title") or p.stem
        if include_types and typ not in include_types:
            continue
        item_id = meta.get("id") or meta.get("pattern") or title
        item: Dict[str, Any] = {
            "source_path": str(p),
            "type": typ,
            "title": title,
            "tags": meta.get("tags") or [],
            "links": meta.get("links") or [],
            "id": item_id,
            "hash": _hash_text(post.content),
            "content": post.content,
        }
        artifacts.append(item)

    if verbose:
        typer.echo(json.dumps({"count": len(artifacts)}, indent=2))

    if dry_run:
        return

    emit_dir.mkdir(parents=True, exist_ok=True)

    # Emit per-item Markdown with YAML frontmatter
    emitted = 0
    for it in artifacts:
        sub = it["type"] or "misc"
        fname = f"{_slug(it['id']) or _slug(it['title'])}.md"
        out_md = emit_dir / sub / fname
        fm = _frontmatter({
            "type": it["type"],
            "id": it["id"],
            "title": it["title"],
            "tags": it["tags"],
            "links": it["links"],
        })
        _emit(out_md, fm + it["content"].rstrip() + "\n")
        emitted += 1

    # Also write a JSONL index for quick diffs
    out_jsonl = emit_dir / "index.jsonl"
    with out_jsonl.open("w", encoding="utf-8") as f:
        for it in artifacts:
            f.write(json.dumps(it) + "\n")

    typer.echo(f"Emitted {emitted} markdown files and index to {emit_dir}")


if __name__ == "__main__":
    app()
