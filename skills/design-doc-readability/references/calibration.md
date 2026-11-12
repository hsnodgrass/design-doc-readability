# Calibration

The thresholds in `../scripts/patterns.json` (`scoring`) were set on
2026-11-10. The gold set is RFCs and the Kubernetes architecture docs. The
other sets show where generated prose falls. The patterns and metrics drawn
from the USU technical writing standards were checked against the same
sets. The two patterns from Clark, Martin, and Mahowald were added on
2026-11-12 and checked as described under "The syntax checks".

## Corpus

| Set | Docs | Words | Source |
| --- | --- | --- | --- |
| RFCs | 10 | 267,000 | RFC 5246, 6749, 7230, 7519, 8259, 8446, 8949, 9000, 9110, 9293, plain text from rfc-editor.org |
| Kubernetes architecture docs | 10 | 8,900 | Every page under `kubernetes.io/docs/concepts/architecture/`, as Markdown from the `kubernetes/website` repository (listed below) |
| Internal design docs | 19 | 96,000 | Markdown design docs from a private repository, not published here |
| Fixtures | 3 | 1,400 | `tests/fixtures/` in this repository |

Word counts are the scanner's: prose, list, and table words, without code,
front matter, or Hugo shortcodes.

The Kubernetes pages, under `content/en/docs/concepts/architecture/`:
`_index.md` (Cluster Architecture), `cgroups.md`, `cloud-controller.md`,
`control-plane-node-communication.md`, `controller.md`,
`garbage-collection.md`, `leases.md`, `mixed-version-proxy.md`, `nodes.md`,
and `self-healing.md`.

The Kubernetes section is small, so a single hit moves a page's score more
than it would in a long RFC.

## Results

Index per axis. Lower is better. Each threshold has the form good / bad.
Ranges leave out docs under 400 words.

| Axis | Threshold | RFCs | Kubernetes | Internal docs | LLM fixture |
| --- | --- | --- | --- | --- | --- |
| vocabulary | 1.0 / 12 | 0.18 to 1.56 | 0 to 6.6 | 0 to 3.6 | 145 |
| filler | 0.8 / 8 | 0.09 to 0.63 | 0 to 0.42 | 0 to 0.24 | 87 |
| rhetoric | 1.5 / 10 | 0.1 to 0.96 | 0 to 0.84 | 0 to 5.4 | 29 |
| tone | 1.0 / 10 | 0 to 0.88 | 0 to 1.89 | 0 to 0.95 | 38 |
| typography | 2.5 / 20 | 0.15 to 0.81 | 0 to 5.4 | 0 to 37 | 90 |
| structure | 3.0 / 12 | 0.48 to 1.65 | 0.36 to 5.8 | 0.04 to 16.3 | 29 |
| precision | 1.5 / 10 | -2.38 to 0.34 | 0.45 to 3.97 | -1.9 to 0.95 | 36 |

The `good` thresholds sit at the top of the RFC range and near the pooled
Kubernetes density: across all ten pages, Kubernetes has 1.24 weighted
vocabulary hits, 0.23 tone hits, and a precision index of 1.89 per 1,000
words. The highest Kubernetes values come from single hits on short pages.
Setting thresholds there would let most internal docs score 10.

Measured subtotals:

| Set | Lowest | Median | Highest |
| --- | --- | --- | --- |
| RFCs | 99 | 100 | 100 |
| Kubernetes | 66 | 97 | 100 |
| Internal design docs | 74 | 86 | 100 |
| LLM fixture | 0 | 0 | 0 |

Two Kubernetes pages score well below the rest:

- `self-healing.md` (66) is 259 words, below the scanner's 400-word floor
  for stable densities, and is mostly a list of bold-label bullets.
- `mixed-version-proxy.md` (87) uses "holistic" and "comprehensive" in 756
  words.

## What this shows

**RFCs and Kubernetes agree on density.** Both keep sentences short: the
average is about 17 words, and the 90th percentile is 33 words in RFCs and
27 in Kubernetes. Both use colons in prose about once per 1,000 words,
"rather than" under 0.5 times, and almost no em dashes. Kubernetes has
none.

**Kubernetes differs in voice.** It addresses the reader as "you" about 15
times per 1,000 words and uses about 1.5 contractions per 1,000 words.
Neither is graded. The rubric applies USU's rule on narrative person by
section instead.

**Typography and structure separate the sets most.** The internal docs
have a median of 1.6 em dashes and 8.2 bold spans per 1,000 words. The
Kubernetes docs have no em dashes and a median of 1.1 bold spans. About 48%
of the internal docs' words are in lists, against 21% for Kubernetes and 7%
for RFCs, and 41% of their bullets open with a bold label. No Kubernetes
page does that, apart from `self-healing.md`.

**The internal docs avoid the known word list.** They also use colons in
prose more (2 to 18 per 1,000 words), stack contrasts, and write long
sentences (their 90th percentile is 43 words). The rest of the difference
is in terminology and economy: coined metaphors used as names, and
sentences that stack clauses. The scanner can't measure those, which is
why the reviewer scores them.

## The USU checks

The USU guidelines added five scored pattern groups (redundancy, wordy
phrase, vague word, generalization, inflated word), a cliché list, an
opinion pattern, and a term for long paragraphs in the structure index. They
also added metrics that are reported but not scored.

| Metric | RFCs | Kubernetes | Internal docs |
| --- | --- | --- | --- |
| Median paragraph, words | 22 | 26 | 47 |
| Paragraphs over 100 words | 3% | 1% | 14% |
| Sentences with a passive verb | 30% | 20% | 18% |
| Sentences opening with a vague "This" or "It" | 2.3% | 3.9% | 5.3% |
| Contractions per 1,000 words | 0.16 | 1.4 | 0.8 |
| Wordy phrases per 1,000 words | 1.09 | 0.34 | 0.02 |
| Vague words per 1,000 words | 0.20 | 0.23 | 0.06 |

Paragraph length separates the gold set from the internal docs, so it is
scored. The other rows don't, or they point the wrong way:

- The gold docs use the passive at least as often as the internal docs, so
  passive voice is reported, not scored.
- Contractions vary by house style.
- Wordy phrases ("in order to", "prior to") and vague words appear most in
  the gold docs. They carry a weight of 0.25 each, so they lower a score
  only when they are frequent.
- Redundancies, generalizations, inflated words, clichés, and opinion words
  are rare everywhere, under 0.15 per 1,000 words in every set. They carry
  full weight, because they are rare in good writing.

Two gold docs lose points to a USU pattern. RFC 6749 uses "utilize" and
"facilitate" 19 times (vocabulary 9.5). The Kubernetes leases page says a
name should be "obviously linked" to its component, a generalization in
592 words (precision 7.0).

The `undefined_acronyms` list is a hint, not a score. The RFCs leave
acronyms such as OID, DER, and RSASSA unexpanded for readers who know them,
and their median is 35 such acronyms per doc, many from the reference
lists. The Kubernetes pages have a median of 0.5 (RBAC and HA are the
usual ones). In the internal docs it is 11.

## The syntax checks

Clark, Martin, and Mahowald (arXiv:2610.29162, a v1 preprint) found that
frontier models drop optional words more often than human writers do, and
use other constructions that slow readers. They used a full parser and a
classifier. Two of these constructions can be found with a regular
expression:

- "reduced object relative", in the `syntax` category, which feeds the
  structure index with weight 1: a relative clause with its "that"
  dropped, as in "the key it wraps". About 85 to 90% of its hits were
  real in a hand check of 32 hits from the RFCs and the internal docs. It
  skips nouns that start an adverbial phrase, such as "the way", "the
  time", and "in the past".
- "inanimate subject, animate verb", in the `tone` category, with weight
  2: a verb for a living thing, such as "swallows", "bites", or "hammers",
  after a code span, a pronoun, or a determiner and up to three words.
  "`refresh()` swallows the error" and "this edge case bites" both count.
  A subject that names a person, such as "the user", "an attacker", "the
  operator", or "the caller", doesn't count. The verb list leaves out verbs
  that systems docs use by convention, such as "knows", "wants",
  "decides", and "watches", because the RFCs and Kubernetes pages use them
  too. It also leaves out "steals" and "lies to", which security sections
  use for attackers.

The two patterns differ in how much of the subject they read. Letting the
Tone pattern's subject run to three words added no gold-set hits and 2
private-set hits, both real. The same change to the relative-clause
pattern raised its RFC hits from 39 to 564, most of them false, so that
pattern still reads one word before the clause.

Noun stacks, nouns used as verbs, dependency length, and rare word pairs
are left to the reviewer. Without a part-of-speech tagger, a noun-stack
pattern was right about half the time, and the RFCs use many compounds as
terms of art. A noun-as-verb list found nothing in the gold set or the
internal docs. Dependency length and word-pair rarity need a parser or a
language model.

The scanner also reports `that_omission_share`, unscored: of the clauses
where "that" is optional (a complement after "knows" or "ensures", or an
object relative), the share written without it. The count is in
`that_clauses`. Both sides use the same rules, so a clause counts once
whether or not it keeps "that". Human writers drop "that" too, so the
share is a hint for the reviewer, and it is noisy when a doc has few such
clauses.

These checks were run on 2026-11-12 over the same RFCs and Kubernetes
pages, fetched again, and over a second private set: 40 Markdown design
docs, 160,000 words. These are not the 19 internal docs in the tables
above, so their subtotals differ from those. The current scanner counts
283,000 words in the RFCs.

Per 1,000 words, for docs of 400 words or more:

| Measure | RFCs | Kubernetes | Internal docs (40) |
| --- | --- | --- | --- |
| Reduced object relatives, median | 0.06 | 0 | 1.61 |
| Reduced object relatives, range | 0 to 0.31 | 0 to 1.55 | 0 to 4.47 |
| Inanimate subject, animate verb, pooled | 0.004 (1 hit) | 0 | 0.01 (2 hits) |
| `that_omission_share`, pooled | 19% of 334 clauses | 4 of 7 clauses | 98% of 313 clauses |
| `that_omission_share`, median of docs with 5 or more such clauses | 20% (9 docs) | No doc has 5 | 100% (26 docs) |

Measured subtotals before and after the change:

| Set | Lowest | Median | Highest | Docs that changed |
| --- | --- | --- | --- | --- |
| RFCs | 99.1, no change | 100, no change | 100 | 0 of 10 |
| Kubernetes | 66.2, no change | 97, no change | 100 | 1 of 10: `cloud-controller.md`, 95.6 to 93.1 |
| Internal docs (40) | 66.2 to 65.0 | 77.1 to 76.1 | 91.2, no change | 31 of 40, by at most 6.3 |
| `llm-heavy.md` | 0 | 0 | 0 | No hits |
| `rfc-like.md` | 100 to 98.1 | | | 2 true hits |
| `compressed.md` | 93.4 to 72.2 | | | New fixture |

The lowest Kubernetes page and the lowest internal doc both score 66.2
before the change. They are different docs: `self-healing.md` has 259
words, and the internal doc has about 6,700.

The fixture `compressed.md` is written in the style that the paper
describes. It avoids the known word list and has no other Tone hits, so
before this change it scored 93. The fixture
`llm-heavy.md` is written in the older style and has none of these
constructions.

The internal docs keep "that" in 5 of 313 clauses where it is optional.
The RFCs keep it in 270 of 334. Part of that gap may come from this skill:
until 2026-11-12 the rubric passed on USU's rule that "that" is a filler
word, and these docs may have been revised after a grade from it. Read the
internal column as an upper bound on the habit, not as a clean measure of
model prose.

The rest of the paper's constructions are graded by reading only. Before
the scanner scores any of them, measure their rates on the gold set.

## Recalibrating

1. Collect gold docs: RFCs as plain text from rfc-editor.org, and
   Kubernetes pages as Markdown from
   `https://raw.githubusercontent.com/kubernetes/website/main/content/en/docs/concepts/architecture/<page>.md`.
   Collect a set of docs you judge to be LLM-heavy.
2. Run `python3 scripts/calibrate.py <files>` from the skill directory.
3. For each axis, set `good` near the top of the RFC range and the pooled
   Kubernetes density, and `bad` at the index of a doc you would grade 0 on
   that axis.
4. Add or reweight patterns in `categories` if a pattern hits gold docs
   often. Check with `--max-hits 10` that its hits are real.
5. Update the tables above, and run the tests:
   `python3 -m unittest tests.test_design_doc_readability`.

## Cross-model check

On 2026-11-10, with an earlier gold set (RFCs only), Codex and Claude each
graded the same 2,700-word internal design doc with this skill,
independently. Codex gave 73 (C) and Claude gave 72 (C). The final axis
scores differed by at most 1.5 points.
