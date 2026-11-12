#!/usr/bin/env python3
"""Measure LLM-style prose patterns in a design doc.

Usage:
    scan.py <file> [--json] [--max-hits N] [--patterns <patterns.json>]

Reads a Markdown or plain-text file, ignores code, URLs and front matter, and
counts the patterns in patterns.json. Prints a report of densities per 1,000
words, a mechanical score from 0 to 10 for each measured axis, and the lines
where each pattern hit, so that a reviewer can quote them.

The scores are a starting point. The reviewer reads the doc and adjusts them,
as SKILL.md describes. Uses only the Python standard library.
"""

import argparse
import json
import math
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⭐⭕]")
ARROW = re.compile(r"[←-⇿⟰-⟿]|(?<![-=<])->(?!>)|=>")
EM_DASH = re.compile(r"—|(?<=\w) – (?=\w)|(?<=\w) -- (?=\w)")
BOLD = re.compile(r"\*\*[^*\n]+\*\*|__[^_\n]+__")
BOLD_LEAD = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(\*\*|__)[^*_\n]+(\*\*|__)")
URL = re.compile(r"https?://\S+")
MD_LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
# Template macros and shortcodes, such as MDN's {{domxref("Element")}}. A macro
# whose first argument is a string reads as that string; any other is dropped.
# Hugo shortcodes, such as {{< glossary_tooltip text="objects" term_id="object" >}}.
# A shortcode with a text attribute reads as that text; any other, including
# the open and close tags of {{< note >}}, is dropped.
SHORTCODE = re.compile(r"\{\{[<%]\s*/?\s*[\w-]+(.*?)[>%]\}\}")
SHORTCODE_TEXT = re.compile(r"\btext=\"([^\"]*)\"")
MACRO = re.compile(r"\{\{\s*[\w.-]+\s*(?:\(\s*(?:\"([^\"]*)\"|'([^']*)')?[^}]*\))?\s*\}\}")
HTML_COMMENT = re.compile(r"<!--.*?-->|\{\{<\s*comment\s*>\}\}.*?\{\{<\s*/comment\s*>\}\}", re.S)
WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[A-Z0-9\"'(\[])")
PROSE_COLON = re.compile(r"\w: [a-z]")
VAGUE_OPENER = re.compile(
    r"^(This|That|It|These)\s+(is|was|are|means|makes|allows|lets|ensures|keeps|gives|avoids|"
    r"matters|works|helps|has|does|can|will|would|also|should|may|might|removes|adds|needs|"
    r"requires|leaves)\b")
PASSIVE = re.compile(
    r"\b(is|are|was|were|be|been|being)\s+(\w+ly\s+)?(\w+ed|known|done|given|made|taken|sent|"
    r"written|built|seen|held|kept|set|run|read|shown|chosen|drawn|bound|found|left|put)\b", re.I)
# Clauses where "that" is optional, for that_omission_share. A complement
# clause after a verb such as "knows" or "ensures", with or without "that",
# and an object relative with "that" or "which". The object relative without
# it is the "reduced object relative" pattern in the syntax category, which
# RELATIVE_THAT mirrors, so that both sides count the same clauses.
REDUCED_RELATIVE = ("syntax", "reduced object relative")
_COMP_VERB = (r"\b(?:know|knew|knows|ensure|ensures|ensured|mean|means|meant|sure|assume|assumes|"
              r"assumed|believe|believes|think|thinks|guarantee|guarantees|show|shows|showed|says|"
              r"said|confirm|confirms|verify|verifies|note|notes|claim|claims|expect|expects|"
              r"requires|imply|implies|indicate|indicates)")
# The subject stops before a pronoun, "that", or a conjunction, so that it
# doesn't absorb a reduced relative ("the page it has loaded") or reach
# across "and" into a second verb phrase.
_CLAUSE_SUBJECT = (r"(?:the|a|an|this|each|every|it|we|they|you|he|she|no|all|its|our|their)"
                   r"(?:\s+(?!(?:and|or|but|it|we|they|you|he|she|that|which|who)\b)[a-z][\w-]*){0,3}?")
_AUX = (r"(?:is|are|was|were|has|have|had|will|would|can|could|must|should|may|might|does|did|"
        r"doesn['’]t|isn['’]t|won['’]t)\b")
COMPLEMENT_BARE = re.compile(rf"{_COMP_VERB}\s+{_CLAUSE_SUBJECT}\s+{_AUX}", re.I)
COMPLEMENT_THAT = re.compile(rf"{_COMP_VERB}\s+that\s+{_CLAUSE_SUBJECT}\s+{_AUX}", re.I)
RELATIVE_THAT = re.compile(
    r"\b(?:the|a|an|every|each|any)\s+(?!(?:time|times|moment|way|day|point|extent|place|case|"
    r"reason|same|following|first|last|only|one|past|end|future|meantime|interim|beginning|long|"
    r"short)\b)[a-z]{3,}\s+(?:that|which)\s+"
    r"(?:(?:the|this|our|your|its)\s+(?:[a-z]+\s+)?[a-z]+|we|you|they|it)\s+"
    r"(?:never\s+|already\s+|just\s+|still\s+)?(?:[a-z]+(?:ed|es|s)|wrote|built|chose|saw|knew|"
    r"made|took|gave|ran|left|kept|held|sent|got)\b(?!\s+(?:to|that)\b)", re.I)
CONTRACTION = re.compile(r"\b\w+(n['’]t|['’]re|['’]ll|['’]ve|['’]d)\b|\b(it|that|there|here|what|who|let)['’]s\b", re.I)
FIRST_PERSON = re.compile(r"\b(I|we|us|our|my)\b", re.I)
SECOND_PERSON = re.compile(r"\b(you|your|yours)\b", re.I)
ACRONYM = re.compile(r"\b([A-Z][A-Za-z0-9]*[A-Z][A-Z0-9]*)(s?)\b(?!-\d)")
# A hex number with a digit in it, such as the E001F in U+E001F.
HEX_NUMBER = re.compile(r"[0-9A-F]*[0-9][0-9A-F]*")

MD_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")
TXT_HEADING = re.compile(r"^(\d+(\.\d+)*\.?|Appendix [A-Z]\.?)\s+[A-Z].*$")
BULLET = re.compile(r"^\s*(?:[-*+•]|o|\d+[.)]|\([a-z0-9]+\))\s+\S")
TABLE = re.compile(r"^\s*\|")
RFC_PAGE = re.compile(r"(\[Page \d+\]\s*$|^RFC \d+\s.*\d{4}\s*$|^\f)")
TOC_LINE = re.compile(r"\.{4,}\s*\d+\s*$")
QUESTION_SECTION = re.compile(r"question|faq|unresolved|open issue", re.I)

AXES = ["vocabulary", "filler", "rhetoric", "tone", "typography",
        "structure", "precision"]


def load_patterns(path):
    data = json.loads(Path(path).read_text())
    compiled = {}
    for cat, entries in data["categories"].items():
        compiled[cat] = [
            (e["label"], re.compile(e["re"], 0 if e.get("case") else re.I | re.M), e["w"])
            for e in entries
        ]
    positive = {
        k: re.compile(v["re"], (0 if v.get("case") else re.I) | re.M)
        for k, v in data["positive"].items()
    }
    acronyms = data.get("acronyms", {})
    acronyms = set(acronyms.get("known", [])) | set(acronyms.get("ignore", []))
    return compiled, positive, data.get("scoring", {}), data.get("weights", {}), acronyms


def preprocess(text, is_txt):
    """Return a list of (line_number, kind, cleaned_text, section_heading)."""
    text = HTML_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    raw = text.splitlines()
    out = []
    in_fence = False
    fence = ""
    in_front = bool(raw) and raw[0].strip() == "---" and not is_txt
    section = ""
    for i, line in enumerate(raw, 1):
        if in_front:
            if i > 1 and line.strip() in ("---", "..."):
                in_front = False
            continue
        stripped = line.strip()
        m = re.match(r"^\s*(```+|~~~+)", line)
        if m:
            if not in_fence:
                in_fence, fence = True, m.group(1)[:3]
            elif stripped.startswith(fence):
                in_fence = False
            continue
        if in_fence or not stripped:
            out.append((i, "blank", "", section))
            continue
        if is_txt and (RFC_PAGE.search(line) or TOC_LINE.search(line)):
            continue
        clean = INLINE_CODE.sub("x", line)
        clean = SHORTCODE.sub(_shortcode_text, clean)
        clean = MACRO.sub(lambda m: m.group(1) or m.group(2) or "", clean)
        clean = MD_LINK.sub(r"\1", clean)
        clean = URL.sub("", clean)
        if not clean.strip():
            out.append((i, "blank", "", section))
            continue
        mh = MD_HEADING.match(clean)
        if mh:
            section = mh.group(1).strip()
            out.append((i, "heading", section, section))
        elif is_txt and TXT_HEADING.match(line) and len(stripped) < 80:
            section = stripped
            out.append((i, "heading", stripped, section))
        elif TABLE.match(clean):
            out.append((i, "table", clean, section))
        elif BULLET.match(clean):
            out.append((i, "bullet", clean, section))
        elif is_txt and _looks_like_art(line):
            out.append((i, "blank", "", section))
        elif (item := _open_bullet(out, line, is_txt)) is not None:
            # A continuation line belongs to the bullet above it, so that a
            # pattern can span the wrap and its words count as list words.
            ln, kind, txt, sec = out[item]
            out[item] = (ln, kind, txt + " " + clean.strip(), sec)
        else:
            out.append((i, "prose", clean, section))
    return out


def _shortcode_text(m):
    t = SHORTCODE_TEXT.search(m.group(1))
    return t.group(1) if t else ""


def _open_bullet(out, line, is_txt):
    """Return the index of the bullet that a line continues, or None.

    A line continues a bullet if it follows the bullet with no blank line in
    between, or, in Markdown, if it is indented under a bullet after a blank
    line, as in a loose list.
    """
    blank = False
    for idx in range(len(out) - 1, -1, -1):
        kind = out[idx][1]
        if kind == "blank":
            blank = True
            continue
        if kind != "bullet":
            return None
        if not blank or (not is_txt and line.startswith(("  ", "\t"))):
            return idx
        return None
    return None


def _looks_like_art(line):
    """Guess whether an RFC text line is ASCII art or a protocol listing."""
    s = line.strip()
    if not s:
        return False
    letters = sum(c.isalpha() for c in s)
    return letters / len(s) < 0.45 or s.startswith(("+-", "|", "struct", "}"))


def paragraphs(lines):
    """Group consecutive prose lines into paragraphs of (start_line, text, section)."""
    paras, cur, start, sec = [], [], None, ""
    for ln, kind, txt, section in lines:
        if kind == "prose":
            if not cur:
                start, sec = ln, section
            cur.append(txt.strip())
        else:
            if cur:
                paras.append((start, " ".join(cur), sec))
            cur = []
    if cur:
        paras.append((start, " ".join(cur), sec))
    return paras


def words(text):
    return WORD.findall(text)


def scan(path, patterns_path, max_hits):
    compiled, positive, scoring, weights, known_acronyms = load_patterns(patterns_path)
    text = Path(path).read_text(errors="replace")
    is_txt = Path(path).suffix.lower() not in (".md", ".markdown", ".mdx")
    lines = preprocess(text, is_txt)
    paras = paragraphs(lines)

    content = [(ln, kind, t, s) for ln, kind, t, s in lines
               if kind in ("prose", "bullet", "table")]
    prose_words = sum(len(words(p[1])) for p in paras)
    bullet_words = sum(len(words(t)) for _, k, t, _ in content if k == "bullet")
    table_words = sum(len(words(t)) for _, k, t, _ in content if k == "table")
    total_words = prose_words + bullet_words + table_words
    per_k = 1000.0 / max(total_words, 1)

    # Units searched for patterns: whole paragraphs, so that a pattern can span
    # a soft line break, plus individual bullet and table lines.
    units = [(ln, txt, sec) for ln, txt, sec in paras]
    units += [(ln, t, s) for ln, k, t, s in content if k in ("bullet", "table")]
    headings = [(ln, t) for ln, k, t, _ in lines if k == "heading"]

    hits = {cat: {} for cat in compiled}
    for cat, entries in compiled.items():
        if cat == "headings":
            for ln, t in headings:
                bare = re.sub(r"^[\d.\s]+", "", t).strip()
                for label, rx, w in entries:
                    if rx.search(bare):
                        hits[cat].setdefault(label, {"w": w, "lines": []})["lines"].append((ln, t))
            continue
        for ln, t, _ in units:
            for label, rx, w in entries:
                for m in rx.finditer(t):
                    hits[cat].setdefault(label, {"w": w, "lines": []})["lines"].append(
                        (ln, _excerpt(t, m.start(), m.end())))

    def weighted(cat):
        return sum(v["w"] * len(v["lines"]) for v in hits[cat].values())

    # Rhetorical questions: questions in prose outside question-themed sections.
    rq = []
    for ln, t, sec in paras:
        if QUESTION_SECTION.search(sec or ""):
            continue
        for s in SENTENCE_SPLIT.split(t):
            if s.rstrip().endswith("?"):
                rq.append((ln, s.strip()[:140]))

    body = "\n".join(t for _, _, t, _ in content)
    em_dashes = len(EM_DASH.findall(body))
    bold = len(BOLD.findall(body))
    emoji = len(EMOJI.findall(body)) + sum(len(EMOJI.findall(t)) for _, t in headings)
    arrows = sum(len(ARROW.findall(t)) for _, k, t, _ in content if k == "prose")

    bullets = [t for _, k, t, _ in content if k == "bullet"]
    bold_lead = sum(1 for t in bullets if BOLD_LEAD.match(t))

    sentences = []
    for _, t, _ in paras:
        sentences += [len(words(s)) for s in SENTENCE_SPLIT.split(t) if words(s)]
    para_sentences = [len([s for s in SENTENCE_SPLIT.split(t) if words(s)]) for _, t, _ in paras]
    sentence_texts = [s.strip() for _, t, _ in paras for s in SENTENCE_SPLIT.split(t) if words(s)]
    para_words = [len(words(t)) for _, t, _ in paras]
    unit_text = "\n".join(t for _, t, _ in units)
    undefined = _undefined_acronyms(units, unit_text, known_acronyms)

    # The share of optional-"that" clauses written without it. Unscored: human
    # writers drop it too, and the share is noisy when a doc has few clauses.
    that_kept = sum(len(COMPLEMENT_THAT.findall(t)) + len(RELATIVE_THAT.findall(t))
                    for _, t, _ in units)
    cat, label = REDUCED_RELATIVE
    that_dropped = (sum(len(COMPLEMENT_BARE.findall(t)) for _, t, _ in units)
                    + len(hits.get(cat, {}).get(label, {"lines": []})["lines"]))
    that_clauses = that_kept + that_dropped

    pos = {k: 0 for k in positive}
    for k, rx in positive.items():
        if k == "terminology_heading":
            pos[k] = sum(1 for _, t in headings if rx.search(t.strip()))
        else:
            pos[k] = sum(len(rx.findall(t)) for _, t, _ in units)

    m = {
        "words_total": total_words,
        "words_prose": prose_words,
        "words_bullet": bullet_words,
        "words_table": table_words,
        "bullet_word_share": round(bullet_words / max(total_words, 1), 3),
        "headings": len(headings),
        "headings_per_k": round(len(headings) * per_k, 2),
        "paragraphs": len(paras),
        "one_sentence_paragraph_share": round(
            sum(1 for n in para_sentences if n == 1) / max(len(para_sentences), 1), 3),
        "sentences": len(sentences),
        "sentence_words_mean": round(statistics.mean(sentences), 1) if sentences else 0,
        "sentence_words_stdev": round(statistics.pstdev(sentences), 1) if sentences else 0,
        "long_sentence_share": round(
            sum(1 for n in sentences if n > 40) / max(len(sentences), 1), 3),
        "colons_in_prose_per_k": round(
            sum(len(PROSE_COLON.findall(t)) for _, t, sec in paras
                if not positive["terminology_heading"].search(sec or "")) * per_k, 2),
        "semicolons_per_k": round(body.count(";") * per_k, 2),
        "paragraph_words_median": statistics.median(para_words) if para_words else 0,
        "long_paragraph_share": round(
            sum(1 for n in para_words if n > 100) / max(len(para_words), 1), 3),
        "vague_opener_share": round(
            sum(1 for s in sentence_texts if VAGUE_OPENER.match(s)) / max(len(sentence_texts), 1), 3),
        "passive_sentence_share": round(
            sum(1 for s in sentence_texts if PASSIVE.search(s)) / max(len(sentence_texts), 1), 3),
        "that_clauses": that_clauses,
        "that_omission_share": round(that_dropped / that_clauses, 3) if that_clauses else None,
        "contractions_per_k": round(len(CONTRACTION.findall(unit_text)) * per_k, 2),
        "first_person_per_k": round(len(FIRST_PERSON.findall(unit_text)) * per_k, 2),
        "second_person_per_k": round(len(SECOND_PERSON.findall(unit_text)) * per_k, 2),
        "undefined_acronyms": len(undefined),
        "bullets": len(bullets),
        "bold_lead_bullet_share": round(bold_lead / max(len(bullets), 1), 3),
        "em_dashes_per_k": round(em_dashes * per_k, 2),
        "bold_per_k": round(bold * per_k, 2),
        "emoji": emoji,
        "arrows_in_prose_per_k": round(arrows * per_k, 2),
        "rhetorical_questions_per_k": round(len(rq) * per_k, 2),
        "normative_caps_per_k": round(pos["normative_caps"] * per_k, 2),
        "normative_lower_per_k": round(pos["normative_lower"] * per_k, 2),
        "quantities_per_k": round(pos["quantities"] * per_k, 2),
        "cross_refs_per_k": round(pos["cross_refs"] * per_k, 2),
        "terminology_section": pos["terminology_heading"] > 0,
    }
    for cat in compiled:
        m[f"{cat}_weighted_per_k"] = round(weighted(cat) * per_k, 2)

    index = {
        "vocabulary": m["vocabulary_weighted_per_k"],
        "filler": m["filler_weighted_per_k"],
        "rhetoric": m["rhetoric_weighted_per_k"] + 1.5 * m["rhetorical_questions_per_k"],
        "tone": m["tone_weighted_per_k"],
        "typography": m["em_dashes_per_k"] + 0.5 * m["bold_per_k"]
        + 5 * emoji * per_k + 0.5 * m["arrows_in_prose_per_k"]
        + 0.4 * max(m["colons_in_prose_per_k"] - 2.5, 0),
        "structure": 10 * max(m["bullet_word_share"] - 0.2, 0)
        + 0.3 * max(m["headings_per_k"] - 15, 0)
        + 4 * m["bold_lead_bullet_share"] * min(m["bullet_word_share"] * 3, 1)
        + 4 * max(m["one_sentence_paragraph_share"] - 0.3, 0)
        + 20 * max(m["long_sentence_share"] - 0.06, 0)
        + 20 * max(m["long_paragraph_share"] - 0.04, 0)
        + weighted("headings") * per_k
        + weighted("syntax") * per_k,
        "precision": m["hedge_weighted_per_k"]
        - 0.15 * min(m["normative_caps_per_k"] + m["normative_lower_per_k"], 20)
        - 0.15 * min(m["quantities_per_k"], 10),
    }
    index = {k: round(v, 2) for k, v in index.items()}
    scores = {a: _score(index[a], scoring.get(a)) for a in AXES}
    measured = [a for a in AXES if scores[a] is not None and a in weights]
    subtotal = (round(10 * sum(scores[a] * weights[a] for a in measured)
                      / sum(weights[a] for a in measured), 1) if measured else None)

    hit_list = {}
    for cat, labels in hits.items():
        rows = sorted(labels.items(), key=lambda kv: -kv[1]["w"] * len(kv[1]["lines"]))
        hit_list[cat] = [
            {"pattern": label, "count": len(v["lines"]), "weight": v["w"],
             "examples": [{"line": ln, "text": t} for ln, t in v["lines"][:max_hits]]}
            for label, v in rows
        ]
    hit_list["rhetorical_questions"] = [{"line": ln, "text": t} for ln, t in rq[:max_hits * 2]]
    hit_list["undefined_acronyms"] = undefined[:15]
    hit_list["vague_openers"] = [s[:140] for s in sentence_texts if VAGUE_OPENER.match(s)][:max_hits * 2]

    return {"file": str(path), "metrics": m, "index": index,
            "mechanical_scores": scores, "mechanical_subtotal": subtotal,
            "weights": {k: v for k, v in weights.items() if not k.startswith("_")},
            "hits": hit_list,
            "short_doc": total_words < 400}


def _undefined_acronyms(units, text, known):
    """List acronyms the doc never expands, most frequent first.

    An acronym counts as expanded if it appears in parentheses, as in
    "Ground Support Equipment (GSE)", is followed by its expansion in
    parentheses, or starts a definition line, as in "GSE: ground support
    equipment".

    Skips code points and hex numbers (U+E001F), names that follow a dot
    (.NET), and the known and ignored words in patterns.json.
    """
    seen = {}
    for ln, t, _ in units:
        for m in ACRONYM.finditer(t):
            a = m.group(1)
            if len(a) > 6 or a in known or a + m.group(2) in known:
                continue
            before = t[max(0, m.start() - 2):m.start()]
            if before.endswith(("U+", ".")) or (len(a) >= 4 and HEX_NUMBER.fullmatch(a)):
                continue
            row = seen.setdefault(a, {"acronym": a, "count": 0, "line": ln})
            row["count"] += 1
    out = []
    for a, row in seen.items():
        q = re.escape(a)
        if re.search(rf"\(\s*{q}s?\s*\)|\b{q}s?\s+\([a-z]|^\s*(?:[-*]\s+)?(?:\*\*)?{q}(?:\*\*)?\s*[:—]", text, re.M):
            continue
        out.append(row)
    return sorted(out, key=lambda r: (-r["count"], r["line"]))


def _score(x, band):
    """Map an index to 0-10. At or below band.good scores 10; at or above band.bad scores 0."""
    if not band:
        return None
    good, bad = band["good"], band["bad"]
    frac = (bad - x) / (bad - good)
    return round(max(0.0, min(1.0, frac)) * 20) / 2


def _excerpt(text, start, end, width=60):
    a = max(0, start - width)
    b = min(len(text), end + width)
    s = text[a:b].strip()
    return ("…" if a > 0 else "") + s + ("…" if b < len(text) else "")


def print_text(r):
    m = r["metrics"]
    print(f"File: {r['file']}")
    print(f"Words: {m['words_total']} (prose {m['words_prose']}, bullets {m['words_bullet']}, tables {m['words_table']})")
    if r["short_doc"]:
        print("Note: under 400 words. Densities are noisy; weigh the reading more than the numbers.")
    print("\nMechanical scores (0-10, higher reads more like an RFC):")
    for a in AXES:
        print(f"  {a:<11} {r['mechanical_scores'][a]!s:>5}   index {r['index'][a]}")
    print(f"  Measured subtotal (0-100, axes weighted): {r['mechanical_subtotal']}")
    print("\nMetrics:")
    for k, v in m.items():
        if not k.startswith("words_"):
            print(f"  {k}: {v}")
    print("\nHits:")
    for cat, rows in r["hits"].items():
        if not rows:
            continue
        print(f"  [{cat}]")
        if cat == "rhetorical_questions":
            for e in rows:
                print(f"    L{e['line']}: {e['text']}")
            continue
        if cat == "undefined_acronyms":
            for e in rows:
                print(f"    {e['acronym']} x{e['count']}, first at L{e['line']}")
            continue
        if cat == "vague_openers":
            for e in rows:
                print(f"    {e}")
            continue
        for row in rows:
            print(f"    {row['pattern']} x{row['count']} (w{row['weight']})")
            for e in row["examples"]:
                print(f"      L{e['line']}: {e['text']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap.add_argument("--max-hits", type=int, default=3, help="example lines per pattern")
    ap.add_argument("--patterns", default=str(HERE / "patterns.json"))
    args = ap.parse_args()
    if not Path(args.file).is_file():
        sys.exit(f"error: no such file: {args.file}")
    r = scan(args.file, args.patterns, args.max_hits)
    if r["metrics"]["words_total"] == 0:
        sys.exit(f"error: no prose found in {args.file}; is it a design doc?")
    if args.json:
        json.dump(r, sys.stdout, indent=2, ensure_ascii=False)
        print()
    else:
        print_text(r)


if __name__ == "__main__":
    main()
