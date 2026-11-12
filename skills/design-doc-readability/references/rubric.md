# Rubric

Score each axis from 0 to 10, in steps of 0.5. The anchors below describe 10,
7, 4, and 1. Score between anchors when a doc falls between them.

## The standard

The gold standard is three sources:

- **IETF RFCs**, for specifications: what a system must
  do, stated so that it can be tested.
- **The Kubernetes architecture docs** (kubernetes.io/docs/concepts/architecture),
  for explanation: what a system's parts are, how they work together, and
  why, with an example for each idea.
- **The USU Engineering Writing Center's Technical Writing Standards and
  Style Guidelines** (engineering.usu.edu, updated August 2025), for the
  rules of technical prose. The section below maps each rule to an axis.

The RFCs and the Kubernetes docs share these traits. They are the target.

- **Declarative sentences.** One claim per sentence. The subject is the thing
  that acts: "The server closes the connection," not "Connection closure is
  handled." The verb is something the subject does: a server sends,
  closes, and rejects. It doesn't bite, swallow, or eat.
- **Defined terms.** A terminology section, or a definition at first use.
  After that, one word for one concept. A "client" never becomes a "caller"
  or a "consumer" later.
- **Requirements stated as requirements.** RFCs use the RFC 2119 keywords
  (MUST, SHOULD, MAY). A design doc doesn't need capitals, but it states
  what the system does and doesn't do, in the present or future tense,
  without hedging.
- **Numbers.** Timeouts, sizes, limits, and rates are given as numbers with
  units.
- **Plain typography.** RFCs are ASCII. The Kubernetes architecture docs
  use no em dashes, and bold little beyond a label in a list. Emphasis is
  rare. Lists enumerate real
  sequences or sets. Paragraphs carry the argument.
- **Examples.** The Kubernetes docs explain each idea with a concrete
  case: a thermostat for a control loop, the Job controller for the
  controller pattern, node heartbeats for leases. A design doc does the
  same with a sample payload, a sequence of calls, or a worked case.
- **No sales voice.** No enthusiasm, no persuasion by tone, no addressing
  the reader as a friend. Rationale is stated, not sold.
- **Cross-references by section number** or by link, and a security
  considerations section.

When the doc specifies behavior, hold it to the RFC standard. When it
explains how a system's parts fit together, hold it to the Kubernetes
standard. Most design docs do both.

## USU technical writing standards

Each rule from the USU guidelines, and where it is graded. "Scanner" means
the scanner reports it; the reviewer still checks the hits.

| USU rule | Axis | How it is checked |
| --- | --- | --- |
| Use active voice. Passive is acceptable when the action matters more than the actor, or the actor is unknown. | Precision | Reviewer. The scanner reports `passive_sentence_share` but doesn't score it (see below). |
| Bias-free, gender-neutral, professional language. | Tone | Reviewer. |
| Opinion-free and emotion-free: avoid feel, think, believe, like, love. | Tone | Scanner: "opinion or emotion". |
| Paragraphs of four to six lines, with a topic sentence and one main idea. | Structure, Economy | Scanner: `long_paragraph_share` (over 100 words). Reviewer: topic sentences. |
| Sentences of 10 to 20 words. | Structure | Scanner: `sentence_words_mean` and `long_sentence_share`. |
| Transitions between sentences and paragraphs. | Economy | Reviewer (see below). |
| No wordy, awkward, or confusing sentences. | Economy | Scanner: "wordy phrase". Reviewer: the rest. |
| Jargon suited to the audience. Spell out an acronym at first use, unless it is well known. | Terminology | Scanner: the `undefined_acronyms` list. Reviewer: jargon. |
| No redundancies ("true fact", "exactly identical"). | Filler | Scanner: "redundancy". |
| No non-specific references or words ("a bit"). | Precision | Reviewer, with the scanner's vague magnitude and quantity hits. |
| No filler words (that, very, just). | Filler, Precision | Scanner: "vague word" for "very"; reviewer for "just". Don't mark down "that" (see "Concise and compressed" below). |
| No abstract or vague language (really, quite, many, a lot, huge). | Precision | Scanner: "vague word". |
| No generalizations ("everyone knows", "nobody ever"). | Precision | Scanner: "generalization". |
| Familiar words, not complicated ones. | Vocabulary | Scanner: "inflated word" (utilize, facilitate, commence). |
| Don't begin sentences with a vague "it" or "this". | Precision | Scanner: the `vague_openers` list. Reviewer: whether the referent is clear. |
| Avoid contractions. | None | Not graded (see below). The scanner reports `contractions_per_k`. |
| Use the narrative person that fits the document type. | Tone | Reviewer (see below). The scanner reports first and second person per 1,000 words. |
| Keep verb tense consistent, and shift it only when time changes. | Precision | Reviewer. |
| Examples and metaphors may clarify. Avoid clichés and slang. | Vocabulary | Scanner: "cliché". Reviewer: slang, and metaphors used as names (Terminology). |
| Format (margins, fonts, spacing). | None | Not graded: it applies to printed documents, not Markdown. |

### Where the standards disagree

- **Passive voice.** USU prefers the active voice. The gold docs use the
  passive at least as often as the LLM-drafted docs in the calibration set:
  RFCs in 30% of sentences, the Kubernetes docs in 20%, and the internal
  docs in 18%. So the passive isn't a sign of generated text, and the
  scanner doesn't score it. Mark it down only where it hides who
  acts in the design: "the token is refreshed" when the reader needs to
  know which component refreshes it.
- **Contractions.** USU says to avoid them. The Kubernetes docs use about
  1.5 per 1,000 words, and RFCs almost none. They don't affect
  readability, so they are not graded.
- **Narrative person.** USU calls for third person in formal technical
  documents, first person in informal ones, and second person in
  instructions. The Kubernetes docs use "you" (about 15 times per 1,000
  words) because they tell the reader what to do as they explain. Apply
  USU's rule by
  section: third person or "we" for the design, and "you" for a procedure
  or runbook. Don't mark down "we" in an internal design doc.
- **Transitions.** USU asks for transitions. Generated text overuses a few
  of them ("Moreover,", "Furthermore,", "Additionally," at the start of
  paragraph after paragraph). A transition that states a real relation of
  time, comparison, or contrast is good. The same connective opening most
  paragraphs is a habit (Filler).
- **Concluding phrases.** USU lists "to summarize" and "in conclusion" as
  transitions. In a design doc, a section that only restates the doc is
  filler, so those phrases still count there.
- **Sentence length.** USU's 10 to 20 words is a target for the average,
  not a cap. The gold docs average about 17 words, and one sentence in
  ten is over 27 (Kubernetes) to 33 (RFCs).
- **Concise and compressed.** USU asks for no filler words and no wordy
  phrases. Generated text also has the opposite fault: it drops words
  that a reader uses to parse a sentence. Clark, Martin, and Mahowald,
  "Why is AI-generated language so hard to understand?"
  (arXiv:2610.29162, 2026), found that recent models drop the optional
  "that" ("the token the broker issued"), turn nouns into verbs
  ("calendar it"), stack three or more nouns, give inanimate subjects
  verbs for living things ("the check bites"), and use rare word pairs.
  Each was more common in model text than in paraphrases of the same
  text. Against human text, rare word pairs and inanimate subjects were
  more common for all nine frontier models in the study, and longer
  dependencies, noun stacks, and dropped "that" for most of them in chat.
  The reading studies that the paper cites link each of these features to
  harder comprehension. So "that" is not filler, and a shorter sentence is
  not better if a reader has to parse it twice. Cut words that say
  nothing. Keep the words that show how a sentence is built. Shortening
  "in order to" to "to" is still fine.

  The paper is a preprint. It measured English chat, code, and essays.
  It didn't measure design docs, and its effects were smallest in the
  essays, which are closest to a design doc. Its human baselines are
  subtitles, StackExchange, and student essays. So grade these features
  as a habit across the doc, never one instance at a time. Human writers
  use the short forms too: a short object relative without "that" that
  reads at once is not a fault.

## Weights

| Axis | Weight | Measured by the scanner |
| --- | --- | --- |
| Vocabulary | 15 | yes |
| Filler | 10 | yes |
| Rhetoric | 15 | yes |
| Tone | 10 | yes |
| Typography | 10 | yes |
| Structure | 10 | yes |
| Precision | 10 | yes |
| Terminology | 10 | no |
| Economy | 10 | no |

Vocabulary and rhetoric weigh most because they are what readers notice
first and trust least.

## 1. Vocabulary

Words a model reaches for that technical writers rarely use: delve,
leverage, seamless, robust, crucial, pivotal, holistic, tapestry, landscape,
realm, empower, unlock, streamline, foster, navigate (figuratively),
load-bearing, quietly, genuinely. Also, from USU: inflated words where a
familiar one would do (utilize, facilitate, commence), clichés ("easier said
than done", "low-hanging fruit"), and slang. See [patterns.md](patterns.md).

Also: rare word pairs that a technical writer wouldn't put together, such
as "verified red" or "the papercut users feel". They aren't on any list,
so find them by reading.

- **10:** None, or one or two that are terms of art.
- **7:** A few, scattered. Most paragraphs are clean.
- **4:** One every few paragraphs. The reader starts to notice.
- **1:** In most paragraphs. Several of the strongest tells (delve,
  tapestry, testament).

## 2. Filler

Words that announce, frame, or summarize instead of saying something: "It's
worth noting that", "Importantly,", "Let's dive in", "At its core", "Here's
the thing", "In summary", "This document aims to explore". Also, from USU:
redundancies ("end result", "exactly identical", "each and every") and
wordy phrases ("due to the fact that", "in order to").

- **10:** Every sentence states content. Section openings start with the
  subject.
- **7:** An occasional "Note that" or "In short".
- **4:** Several framing phrases, and a summary section that repeats the
  doc.
- **1:** Framing in most sections, and a conclusion that restates the
  introduction.

## 3. Rhetoric

Constructions that persuade by shape rather than by content:

- Negative parallelism: "It's not X, it's Y", "not just X, but Y", "isn't
  about X; it's about Y".
- The reveal: "The result? ...", "Here's the catch:".
- Fragment chains: "No cron jobs. No expired secrets. No pages."
- Rhetorical questions answered at once: "Why does this matter? Because..."
- Reflexive triplets: three adjectives or three parallel clauses where one
  would do.
- Contrast stacking: "rather than" and ", not Y" in sentence after sentence.

RFCs contrast things when the contrast is the point, about once in 5,000
words.

- **10:** Contrasts appear only where two options are actually being
  compared.
- **7:** A few set pieces, mostly in the introduction.
- **4:** A recurring habit. The reader can predict the next one.
- **1:** The doc's argument is carried by these shapes.

## 4. Tone

Hype, enthusiasm, intensifiers, and chat residue: powerful, elegant,
incredibly, truly, "We're excited to", "Simply", "just works", exclamation
marks, "Feel free to", "I hope this helps". Also, from USU: opinion and
emotion ("I feel", "we believe", "we're confident"), language that isn't
bias-free or gender-neutral ("the operator ... his"), and a narrative person
that doesn't fit the section (see above).

Also: an inanimate subject with a chat-register verb for a living thing,
such as "`refresh()` swallows the error" or "this edge case bites". The
scanner counts these as "inanimate subject, animate verb": a verb from a
short list that the gold docs almost never use this way (swallows, bites,
eats, hammers), after a code span, a pronoun, or a determiner and up to
three words. It skips subjects that name people, such as "the user", "an
attacker", and "the caller", so "An attacker steals the cookie" is not a
hit. Conventional verbs such as "the client knows" are not on the list.
Where one of those hides a mechanism, it is graded under Precision. A
sentence counts on only one of the two axes: if the scanner counted it
here, don't mark it down again in Precision. The pattern allows an adverb
before the verb ("the path quietly swallows"). The hit is for the verb;
"quietly" and "simply" are separate tells, scored under Vocabulary and
Tone, so the scanner counts each word once.

- **10:** Neutral throughout. Claims are supported by facts, not by
  adjectives or beliefs.
- **7:** One or two adjectives that sell, or one stated belief.
- **4:** The doc sounds like a product announcement in places.
- **1:** Marketing copy, or the residue of a chat.

## 5. Typography

Em dashes, bold, emoji, arrows in prose, and colons used to set up a reveal.
The gold docs use almost no em dashes: RFCs are ASCII, and the Kubernetes
architecture docs have none. They bold a term only where it is defined or
labels an item in a list.

- **10:** Under 2.5 em dashes per 1,000 words. Bold only where a term is
  defined. No emoji.
- **7:** Em dashes or bold in most paragraphs, but not every sentence.
- **4:** Em dashes are the default joint between clauses. Bold is used for
  emphasis throughout.
- **1:** Emoji in headings or lists, arrows in prose, bold on every bullet.

## 6. Structure

How the doc is laid out.

- Bullets used where paragraphs belong: the argument is a list of
  fragments.
- The bold-label bullet: `- **Reliability**: Centralized refresh reduces...`
- Many headings with a sentence or two under each.
- One-sentence paragraphs used for emphasis.
- Headings such as "Why this matters", "Key benefits", "Conclusion", and
  headings phrased as questions.
- Sentences longer than 40 words that stack clauses.
- Paragraphs longer than USU's four to six lines (about 100 words). In the
  gold docs, 1% to 3% of paragraphs run that long.
- Object relative clauses without "that": "the key it wraps", "the names
  the client already uses". The scanner counts this sentence pattern
  here, as "reduced object relative". The gold docs use the form rarely,
  and keep "that" more often than generated docs do (see "Concise and
  compressed").

Check each "reduced object relative" hit by reading it. A short one that
reads at once is how human writers use the form, so discount it. A hit
that nests one clause in another, or that puts many words between a noun
and its verb, is the habit: "The lease the node the scheduler picked
holds expires in 10 s." As on the other measured axes, move the score
by up to 3 points from what that reading shows, and give a line number.
Some hits are not object relatives. A complement clause with its "that"
dropped can match ("Tell the user the request failed"), and so can a
phrase that opens a sentence ("In the past the system used polling",
though the scanner skips "the past", "the end", "the way", and similar
nouns). Take those hits out of the Structure count. Complement clauses
are graded only under Economy.

- **10:** Numbered sections. Paragraphs of a few sentences carry the
  argument. Lists enumerate sets and steps.
- **7:** A few bullet lists that should be prose, a few thin sections, or a
  few overlong paragraphs.
- **4:** Most sections are bullets. The bold-label bullet is the main form.
- **1:** Slide-deck layout. Headings every few lines, and no paragraph
  longer than two sentences.

## 7. Precision

Hedging and vagueness against specific, checkable statements.

Hedges: "may potentially", "can help ensure", "aims to", "various",
"significantly", "in many cases". From USU: vague words ("really",
"quite", "a lot", "huge"), non-specific references ("adjust it a bit"),
generalizations ("everyone knows"), sentences that open with "This" or "It"
when the referent isn't clear, passive voice that hides the actor, and
shifts in verb tense. Also: personification that hides a mechanism, such
as "the proxy refuses" or "the scheduler wants" where the reader needs to
know what happens. RFCs write "the recipient wants" and "a client
decides", so mark it down only where the verb stands in for a mechanism
that the doc doesn't state. The chat-register verbs, such as "swallows"
and "bites", are scored under Tone; don't count them again here.
Specifics: numbers with units, stated limits, "MUST" and "MUST NOT",
named components, section cross-references.

- **10:** Every claim that could be a number is one. Every sentence names
  what acts. Requirements say what happens, and what happens on failure.
- **7:** Mostly specific, with a few vague magnitudes or unclear "this"
  references.
- **4:** Benefits stated as adjectives ("significantly faster") without
  numbers. Risks "could potentially" occur.
- **1:** Nothing in the doc could be tested.

## 8. Terminology (reviewer only)

Whether a reader can tell what each word refers to.

Look for: a terminology section or definitions at first use; one term per
concept; no elegant variation (client, caller, consumer, user for one
thing); no coined metaphors used as names ("the funnel", "the moat",
"the north star") unless defined; jargon suited to the doc's readers.

USU asks for the full term first, then the acronym in parentheses: "Ground
Support Equipment (GSE)". Well-known acronyms are exempt. The scanner's
`undefined_acronyms` list is a starting point: drop the ones the doc's
readers know, and count the rest. RFCs leave some acronyms unexpanded too,
so judge by the audience, not by the count.

- **10:** Every term of the design is defined once and used the same way.
  Every acronym the readers might not know is expanded.
- **7:** A few undefined terms or acronyms, or one concept with two names.
- **4:** The reader has to infer what several terms mean. Metaphors stand in
  for definitions.
- **1:** Terms drift through the doc. A reader can't tell whether two names
  are one thing.

## 9. Economy (reviewer only)

Whether each sentence carries one idea, earns its place, and can be read
once. Economy fails in two ways: padding and compression.

Padding: the same point made in the introduction, a section, and a
summary; sentences that stack three or four clauses with dashes,
semicolons, and parentheses; paragraphs that restate the heading; meta
commentary about the doc ("as argued below", "this section will"); long
preambles before the first fact. From USU: a paragraph without a topic
sentence, or with more than one main idea; wordy or awkward sentences; and
missing transitions, where the reader can't tell how one sentence follows
from the last.

Compression: words cut until the reader has to rebuild the sentence. Look
for a dropped "that" before a clause, where the sentence misleads without
it ("The client found the token expired"); nouns used as one-off verbs
("we can feature-flag it", "calendar the review"); three or more nouns
stacked into a phrase that the doc never defines ("lease renewal backoff
window"); and a subject so long that the reader loses it before the verb.
A stack that is a term of art or a defined term ("TLS record layer") is
fine. Object relatives without "that" are scored under Structure, from
the scanner's hits; don't count them again here. See
[patterns.md](patterns.md).

The scanner reports `that_omission_share`: of the places where it finds
an optional "that" (complement clauses and object relatives), the share
where the doc leaves it out. It is a signal and is not scored. A high share
tells you to read for dropped "that". Compare it with the gold docs'
share in [calibration.md](calibration.md), and score only what the reading
finds.

- **10:** Nothing could be cut without losing content, and nothing was cut
  that a reader needs. A reader can skim the first sentence of each
  paragraph.
- **7:** Some repetition, a few overloaded sentences, or a few compressed
  phrases.
- **4:** The doc could lose a third of its length, or it is compressed
  throughout. Many sentences need two readings.
- **1:** Most of the doc restates itself, or most sentences need two
  readings.
