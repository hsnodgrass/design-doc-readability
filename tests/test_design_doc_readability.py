"""Tests for skills/design-doc-readability/scripts/scan.py.

Run from the repository root: python3 -m unittest discover tests
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "design-doc-readability" / "scripts" / "scan.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def scan(path):
    out = subprocess.run(
        [sys.executable, "-I", str(SCRIPT), str(path), "--json"],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(out)


def patterns(result, category):
    return {row["pattern"] for row in result["hits"][category]}


class ScanTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        path = self.dir / name
        path.write_text(text)
        return path

    def test_llm_heavy_fixture_scores_low(self):
        r = scan(FIXTURES / "llm-heavy.md")
        self.assertLess(r["mechanical_subtotal"], 30)
        for axis, score in r["mechanical_scores"].items():
            self.assertLessEqual(score, 3, axis)

    def test_rfc_like_fixture_scores_high(self):
        r = scan(FIXTURES / "rfc-like.md")
        self.assertGreaterEqual(r["mechanical_subtotal"], 90)
        self.assertTrue(r["metrics"]["terminology_section"])
        self.assertGreater(r["metrics"]["normative_caps_per_k"], 0)

    def test_detects_each_family(self):
        r = scan(FIXTURES / "llm-heavy.md")
        self.assertIn("delve", patterns(scan(self.write("d.md", "We delve into it.\n")), "vocabulary"))
        self.assertIn("leverage", patterns(r, "vocabulary"))
        self.assertIn("it's worth noting", patterns(r, "filler"))
        self.assertIn("isn't X; it's Y", patterns(r, "rhetoric"))
        self.assertIn("fragment chain (No X. No Y.)", patterns(r, "rhetoric"))
        self.assertIn("reveal colon/question", patterns(r, "rhetoric"))
        self.assertIn("excited / thrilled", patterns(r, "tone"))
        self.assertIn("may/could potentially", patterns(r, "hedge"))
        self.assertIn("why this matters", patterns(r, "headings"))
        self.assertGreater(r["metrics"]["emoji"], 0)
        self.assertGreater(r["metrics"]["em_dashes_per_k"], 0)

    def test_ignores_code_front_matter_and_urls(self):
        path = self.write("code.md", (
            "---\ntitle: We leverage a seamless tapestry\n---\n\n"
            "# Title\n\n"
            "The parser reads one record at a time.\n\n"
            "```\n// leverage the seamless, robust tapestry — delve!\n```\n\n"
            "Call `leverageSeamless()` or see https://example.com/delve-tapestry.\n"
        ))
        r = scan(path)
        self.assertEqual(r["hits"]["vocabulary"], [])
        self.assertEqual(r["metrics"]["em_dashes_per_k"], 0)

    def test_macros_read_as_their_text(self):
        path = self.write("macro.md", (
            "# T\n\n"
            "Call {{domxref(\"Request.json()\", \"json()\")}} to read the body.\n\n"
            "{{Compat}}\n"
        ))
        r = scan(path)
        self.assertEqual(r["metrics"]["paragraphs"], 1)
        self.assertEqual(r["metrics"]["words_prose"], 7)

    def test_usu_patterns(self):
        path = self.write("usu.md", (
            "# T\n\n"
            "We believe the end result is that everyone knows the cache works. "
            "We will utilize it in order to reach a huge speedup. "
            "This is easier said than done.\n"
        ))
        r = scan(path)
        self.assertIn("opinion or emotion (USU)", patterns(r, "tone"))
        self.assertIn("redundancy (USU)", patterns(r, "filler"))
        self.assertIn("wordy phrase (USU)", patterns(r, "filler"))
        self.assertIn("generalization (USU)", patterns(r, "hedge"))
        self.assertIn("vague word (USU)", patterns(r, "hedge"))
        self.assertIn("inflated word (USU)", patterns(r, "vocabulary"))
        self.assertIn("cliché (USU)", patterns(r, "vocabulary"))
        self.assertEqual(r["hits"]["vague_openers"], ["This is easier said than done."])

    def test_reduced_object_relative(self):
        for text in ("Rotate the key it wraps.",
                     "Keep the names the client already uses.",
                     "Check every token the issuer signed.",
                     "The server shows the page it has loaded."):
            r = scan(self.write("orc.md", f"# T\n\n{text}\n"))
            self.assertIn("reduced object relative", patterns(r, "syntax"), text)
        for text in ("Rotate the key that it wraps.",
                     "Refresh every time it sends a request.",
                     "The key it uses to sign is in the store.",
                     "In the past the system used polling.",
                     "In the end the client retries."):
            r = scan(self.write("orc.md", f"# T\n\n{text}\n"))
            self.assertEqual(r["hits"]["syntax"], [], text)

    def test_inanimate_subject_animate_verb(self):
        for text in ("The call `refresh()` swallows the error.",
                     "The cache doesn't care which caller asked.",
                     "The check bites during deploys.",
                     "The current refresh path quietly swallows expiry errors.",
                     "In practice this edge case bites.",
                     "That approach hammers the issuer."):
            r = scan(self.write("anim.md", f"# T\n\n{text}\n"))
            self.assertIn("inanimate subject, animate verb", patterns(r, "tone"), text)
        for text in ("The client knows the key.",
                     "An endpoint that wishes to close sends a frame.",
                     "The controller watches the API server.",
                     "An attacker steals the session cookie.",
                     "The user forgets to rotate the key.",
                     "The operator hates the dashboard.",
                     "The on-call engineer forgets the runbook.",
                     "The caller forgets to close the stream."):
            r = scan(self.write("anim.md", f"# T\n\n{text}\n"))
            self.assertNotIn("inanimate subject, animate verb", patterns(r, "tone"), text)

    def test_that_omission_share(self):
        r = scan(self.write("that.md", (
            "# T\n\n"
            "The client knows that the key is valid. Rotate the key that it wraps. "
            "The server ensures the token is fresh. Keep every name the caller uses.\n"
        )))
        self.assertEqual(r["metrics"]["that_clauses"], 4)
        self.assertEqual(r["metrics"]["that_omission_share"], 0.5)
        r = scan(self.write("none.md", "# T\n\nThe parser reads one record at a time.\n"))
        self.assertEqual(r["metrics"]["that_clauses"], 0)
        self.assertIsNone(r["metrics"]["that_omission_share"])

    def test_that_clauses_are_counted_once(self):
        # A reduced relative inside a complement is one clause, not two.
        r = scan(self.write("one.md", "# T\n\nThe server shows the page it has loaded.\n"))
        self.assertEqual(r["metrics"]["that_clauses"], 1)
        # The subject doesn't reach across "and" to a second verb phrase.
        r = scan(self.write("and.md", "# T\n\nWe know the answer and will ship it.\n"))
        self.assertEqual(r["metrics"]["that_clauses"], 0)
        # The overt relative skips the same nouns as the reduced one.
        r = scan(self.write("way.md", "# T\n\nThis is the way that it works.\n"))
        self.assertEqual(r["metrics"]["that_clauses"], 0)

    def test_compressed_fixture(self):
        r = scan(FIXTURES / "compressed.md")
        gold = scan(FIXTURES / "rfc-like.md")
        syntax = {row["pattern"]: row["count"] for row in r["hits"]["syntax"]}
        tone = {row["pattern"]: row["count"] for row in r["hits"]["tone"]}
        self.assertEqual(syntax, {"reduced object relative": 4})
        # The new pattern is the fixture's only Tone hit, so the low Tone
        # score comes from it alone.
        self.assertEqual(tone, {"inanimate subject, animate verb": 7})
        self.assertEqual(r["mechanical_scores"]["tone"], 0)
        self.assertEqual(r["metrics"]["that_clauses"], 7)
        self.assertEqual(r["metrics"]["that_omission_share"], 1.0)
        self.assertLess(r["mechanical_scores"]["structure"], gold["mechanical_scores"]["structure"])
        self.assertLess(r["mechanical_subtotal"], gold["mechanical_subtotal"] - 15)

    def test_undefined_acronyms(self):
        path = self.write("acr.md", (
            "# T\n\n"
            "The Ground Support Equipment (GSE) talks to the DEK store over HTTP.\n\n"
            "GSE and the DEK store share a TCB. Threat AS-1 covers it.\n\n"
            "TCB: trusted computing base.\n"
        ))
        r = scan(path)
        self.assertEqual([e["acronym"] for e in r["hits"]["undefined_acronyms"]], ["DEK"])
        self.assertEqual(r["hits"]["undefined_acronyms"][0]["count"], 2)

    def test_acronym_check_skips_code_points_dotted_names_and_files(self):
        path = self.write("acr2.md", (
            "# T\n\n"
            "The Tags block runs from U+E0000 to U+E007F, and 0x1F4A9 is not text. "
            "Ruby and .NET aren't served. See the README and CODEOWNERS. "
            "Strings are compared after NFKC.\n"
        ))
        r = scan(path)
        self.assertEqual([e["acronym"] for e in r["hits"]["undefined_acronyms"]], ["NFKC"])

    def test_long_paragraphs_lower_structure(self):
        long_para = " ".join(["The service stores one token per audience."] * 20)
        short = self.write("short.md", "# T\n\n" + "The service stores one token.\n\n" * 20)
        long_ = self.write("long.md", "# T\n\n" + (long_para + "\n\n") * 2)
        self.assertEqual(scan(short)["metrics"]["long_paragraph_share"], 0)
        r = scan(long_)
        self.assertEqual(r["metrics"]["long_paragraph_share"], 1.0)
        self.assertLess(r["mechanical_scores"]["structure"], 10)

    def test_hugo_shortcodes_read_as_their_text(self):
        path = self.write("hugo.md", (
            "# T\n\n"
            "These {{< glossary_tooltip text=\"objects\" term_id=\"object\" >}} have a spec.\n\n"
            "{{< note >}}\nNodes register themselves.\n{{< /note >}}\n\n"
            "{{< comment >}}\nLeverage this seamless tapestry.\n{{< /comment >}}\n\n"
            "{{< feature-state for_k8s_version=\"v1.29\" state=\"beta\" >}}\n"
        ))
        r = scan(path)
        self.assertEqual(r["hits"]["vocabulary"], [])
        self.assertEqual(r["metrics"]["paragraphs"], 2)
        self.assertEqual(r["metrics"]["words_prose"], 8)

    def test_hit_reports_line_number(self):
        path = self.write("line.md", "# T\n\nFirst line.\n\nIt's worth noting that this works.\n")
        r = scan(path)
        rows = r["hits"]["filler"]
        self.assertEqual(rows[0]["examples"][0]["line"], 5)

    def test_questions_in_open_questions_section_are_not_rhetorical(self):
        path = self.write("q.md", (
            "# Design\n\nWhy does this matter? Because it does.\n\n"
            "## Open questions\n\nShould the margin be configurable?\n"
        ))
        r = scan(path)
        texts = [e["text"] for e in r["hits"]["rhetorical_questions"]]
        self.assertEqual(texts, ["Why does this matter?"])
        self.assertIn("rhetorical self-answer", patterns(r, "rhetoric"))

    def test_bullet_continuation_lines_count_as_bullets(self):
        path = self.write("wrap.md", (
            "# T\n\n"
            "- **Reliability**: centralized refresh reduces the\n"
            "  risk of expired tokens, and it is worth noting that\n"
            "  it works.\n"
            "- Second item.\n\n"
            "  Indented paragraph inside the second item.\n\n"
            "A real paragraph.\n"
        ))
        r = scan(path)
        self.assertEqual(r["metrics"]["bullets"], 2)
        self.assertEqual(r["metrics"]["paragraphs"], 1)
        self.assertEqual(r["metrics"]["words_prose"], 3)
        self.assertIn("it's worth noting", patterns(r, "filler"))
        self.assertEqual(r["hits"]["filler"][0]["examples"][0]["line"], 3)

    def test_rfc_text_page_furniture_is_skipped(self):
        path = self.write("rfc.txt", (
            "1.  Introduction\n\n"
            "   The client MUST send one request per connection.\n\n"
            "Doe                     Standards Track                    [Page 3]\n"
            "\f\n"
            "RFC 9999                 Example Protocol                 May 2026\n\n"
            "   The server MAY close the connection after 30 seconds.\n"
        ))
        r = scan(path)
        self.assertEqual(r["metrics"]["headings"], 1)
        self.assertGreater(r["metrics"]["normative_caps_per_k"], 0)
        self.assertGreater(r["metrics"]["quantities_per_k"], 0)

    def test_text_output_runs(self):
        out = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), str(FIXTURES / "rfc-like.md")],
            capture_output=True, text=True, check=True,
        ).stdout
        self.assertIn("Measured subtotal", out)

    def test_doc_with_no_prose_fails(self):
        path = self.write("empty.md", "```\ncode only\n```\n")
        p = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), str(path)], capture_output=True, text=True,
        )
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("no prose found", p.stderr)

    def test_missing_file_fails(self):
        p = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), str(self.dir / "nope.md")],
            capture_output=True, text=True,
        )
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("no such file", p.stderr)


if __name__ == "__main__":
    unittest.main()
