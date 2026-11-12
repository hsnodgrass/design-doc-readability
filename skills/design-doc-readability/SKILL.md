---
name: design-doc-readability
description: Grade a design doc for human readability and produce a score card. Measures how much the prose reads like LLM output ("LLM speak", "Claude-isms", AI slop) against the plain style of IETF RFCs and the Kubernetes architecture docs, and against the USU Engineering Writing Center's technical writing standards, across nine axes, and quotes the worst passages with rewrites. Use when the user asks to grade, score, or rate a design doc, RFC, proposal, or ADR for readability, or asks whether a doc sounds like AI wrote it. Reads the doc only; never edits it.
license: Apache-2.0. Complete terms in LICENSE.
---

# Design doc readability

Grade one design doc for how well a human can read it. The standard is the
prose of IETF RFCs and the Kubernetes architecture docs
(kubernetes.io/docs/concepts/architecture): short declarative sentences, defined
terms used the same way every time, requirements stated as requirements,
concrete examples, and no decoration. The rules of technical prose come
from the USU Engineering Writing Center's Technical Writing Standards and
Style Guidelines: active voice where the actor matters, short paragraphs
with one idea each, acronyms spelled out at first use, and no redundant,
vague, or opinionated wording. A doc that reads like that grades high. A
doc that reads like chat output from a language model grades low.

The grade is about prose, not about the design. Don't judge whether the
design is sound, complete, or correct. Don't edit the doc, even to fix what
you find, unless the user asks afterwards.

In this file, `<skill-dir>` is the directory that holds this SKILL.md.

## 1. Get the doc as a file

The user gives a path, a URL, or pasted text.

- A local Markdown or text file: use it as is.
- A URL, a Google Doc, or a doc in another tool: get its text with the tools
  you have, and save it as a `.md` file in a temporary directory.
- Pasted text: save it as a `.md` file in a temporary directory.

If you can't get the full text, stop and say so. Don't grade part of a doc.

## 2. Run the scanner

```sh
python3 <skill-dir>/scripts/scan.py <file>
```

Add `--json` for machine-readable output, or `--max-hits N` to see more
example lines per pattern. The script needs only Python 3.

It ignores code blocks, inline code, URLs, and front matter. It reports:

- A measured score from 0 to 10 for seven axes: vocabulary, filler, rhetoric,
  tone, typography, structure, and precision. 10 is RFC-like.
- A weighted subtotal over those seven axes, from 0 to 100.
- The metrics behind each score, as densities per 1,000 words.
- For each pattern, the line where each paragraph or list item that
  holds a hit starts, with an excerpt.
- Two lists to check by reading: acronyms the doc never spells out
  (`undefined_acronyms`), and sentences that open with a vague "This" or
  "It" (`vague_openers`).
- Metrics that it reports but doesn't score, such as the share of passive
  sentences, the rate of contractions, and how often the doc leaves out an
  optional "that" (`that_omission_share`). The rubric says why.

The scanner finds only what a regex can find. Recent models avoid the
well-known word list and still write prose that reads as generated, so a high
measured subtotal does not mean the doc reads well. Step 3 is not optional.

## 3. Read the doc

Read the whole doc. Use [references/rubric.md](references/rubric.md) to score
each axis, and [references/patterns.md](references/patterns.md) to recognize
the patterns the scanner can't match. The rubric maps each USU rule to an
axis, and says how to apply the rules where USU, the RFCs, and the
Kubernetes docs disagree.

For each of the seven measured axes, start from the measured score and adjust
it:

- Check the hits. Discount a false positive, such as a term of art ("realm"
  in HTTP authentication), a quotation, an error message, or a product name.
- Look for what the scanner missed, such as a rhetorical structure in words
  the catalog doesn't list.
- Look for compression. The scanner counts object relatives without
  "that" (Structure) and a short list of chat-register verbs with
  inanimate subjects (Tone). It can't find other dropped "that", nouns
  used as verbs, noun stacks, long subjects, or rare word pairs. The rubric
  says which axis each one goes to, and `that_omission_share` says where
  to look.
- Move a score by up to 3 points either way. Go further only to remove false
  positives, and say so.
- Give a reason, with a line number, for every change.

Score the last two axes, terminology and economy, from the rubric alone.

Short docs, under 400 words, give noisy densities. The scanner flags them.
For those, give the reading more weight than the numbers.

## 4. Compute the grade

The overall score is the weighted mean of the nine final axis scores, times
10. The weights are in the scanner's output (`weights` in `--json`) and in
the rubric. Round to a whole number.

| Score | Grade | Meaning |
| --- | --- | --- |
| 90 to 100 | A | Reads like an RFC. |
| 80 to 89 | B | Plain, with a few habits a careful reader notices. |
| 70 to 79 | C | The habits are frequent enough to slow a reader. |
| 60 to 69 | D | Reads as lightly edited model output. |
| 0 to 59 | F | Reads as unedited model output. |

## 5. Write the score card

Use this format. Quote the doc exactly. Keep notes to one line each.

```markdown
# Readability score card: <doc title>

<file or URL> · <N> words · **Grade <letter> (<score>/100)**

| Axis | Weight | Measured | Final | Notes |
| --- | --- | --- | --- | --- |
| Vocabulary | 15 | 9.0 | 8.0 | "load-bearing" 4 times (L12, L88). |
| Filler | 10 | ... | ... | ... |
| Rhetoric | 15 | ... | ... | ... |
| Tone | 10 | ... | ... | ... |
| Typography | 10 | ... | ... | ... |
| Structure | 10 | ... | ... | ... |
| Precision | 10 | ... | ... | ... |
| Terminology | 10 | n/a | ... | ... |
| Economy | 10 | n/a | ... | ... |
| **Overall** | 100 | <subtotal> | **<score>** | |

## Summary

<Two to four sentences. What a reader will notice first, and what the doc
does well.>

## Worst passages

1. **L<n>, <axis>.** "<exact quote>"
   Rewrite: "<the same content in RFC style>"
2. ...

## Fixes, in order of payoff

1. <A change that applies across the doc, such as "Replace the 31 em
   dashes with periods or commas.">
2. ...
```

Give three to five worst passages and three to five fixes. Each rewrite must
keep the passage's meaning and facts. Don't add claims the doc doesn't make.
Don't make a rewrite shorter by compressing it: keep "that" where it helps
the sentence parse, and don't turn nouns into verbs or stack nouns.

Print the score card in the conversation. Write it to a file only if the user
asks for one.
