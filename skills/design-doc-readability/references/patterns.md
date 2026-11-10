# Patterns

The patterns behind each axis, with an example of each and an RFC-style
rewrite. The scanner's regexes are in `../scripts/patterns.json`. This file
also lists patterns the scanner can't match, which you find by reading.

A pattern is a tell only in aggregate. One "robust" in a 5,000-word doc
means nothing. Grade the habit, not the instance.

## Vocabulary

| Pattern | Example | Rewrite |
| --- | --- | --- |
| delve, dive into | "Let's delve into the cache design." | "The cache works as follows." |
| leverage | "The broker leverages Redis." | "The broker stores tokens in Redis." |
| seamless, effortless | "Clients integrate seamlessly." | "A client needs one call to get a token." |
| robust, comprehensive | "A robust, comprehensive retry strategy." | "Retries use exponential backoff from 1 s to 30 s." |
| crucial, pivotal, paramount | "Consistency is crucial." | "Two pods MUST NOT hold different tokens for one audience." |
| landscape, realm, tapestry | "In the evolving security landscape..." | Delete. Start with the fact. |
| empower, unlock, elevate | "This unlocks faster builds." | "Builds take 4 minutes instead of 11." |
| plays a key role, serves as | "The scheduler plays a key role in refresh." | "The scheduler refreshes tokens." |
| load-bearing | "The lock is load-bearing." | "Removing the lock lets two writers race." |
| quietly | "The cache quietly drops the entry." | "The cache drops the entry and logs nothing." |
| the shape of | "The shape of the API is simple." | "The API has two calls." |

## Filler

A phrase that introduces content the reader needs next is not filler. The
Kubernetes docs write "Here is one example of a control loop: a thermostat
in a room", and the example follows. Grade the phrases that frame without
adding anything, such as the ones below.

| Pattern | Example | Rewrite |
| --- | --- | --- |
| it's worth noting | "It's worth noting that tokens expire." | "Tokens expire after 60 minutes." |
| Importantly, Notably | "Importantly, the pod never writes to disk." | "The pod never writes a token to disk." |
| at its core | "At its core, TRS is a cache." | "TRS is a cache." |
| here's the thing | "Here's the thing: every team rebuilt this." | "Each of the 14 services has its own refresh code." |
| this doc aims to explore | "This document aims to explore token refresh." | "This document specifies a token refresh service." |
| in summary, in conclusion | "In summary, TRS improves reliability." | Delete the section if it repeats the doc. |
| this is where X comes in | "This is where TRS comes in." | Delete. Describe TRS. |
| think of it as | "Think of it as a concierge for credentials." | Delete the metaphor. Say what it does. |

## Rhetoric

| Pattern | Example | Rewrite |
| --- | --- | --- |
| It's not X, it's Y | "It's not a cache; it's a platform." | "TRS caches tokens and refreshes them." |
| not just X, but Y | "Not just faster, but safer." | State each claim with its evidence. |
| The reveal | "The result? Fewer outages." | "Token expiry caused 6 of 23 incidents. TRS removes that cause." |
| Fragment chain | "No cron jobs. No secrets. No pages." | "Services no longer run refresh jobs." |
| Self-answered question | "Why a DaemonSet? Because..." | "We chose a DaemonSet because..." |
| Triplet | "Simple, fast, and reliable." | Keep the one adjective the doc supports with a number. |
| Contrast stacking | "...a lease rather than a lock... a hint, not a guarantee... the client, not the server..." | State what is true. Mention the alternative only where a reader would expect it. |

Not matched by the scanner, so watch for these while reading:

- A paragraph that ends on a short punchline sentence.
- "X. And that's the point." and similar closing beats.
- Antithesis in pairs: "Easy to start, hard to outgrow."
- Lists of exactly three items, again and again, where the content doesn't
  come in threes.
- Personification: "the proxy refuses", "the scheduler wants", in places
  where it hides who does what.

## Tone

| Pattern | Example | Rewrite |
| --- | --- | --- |
| Hype adjective | "A powerful, elegant API." | "An API with two calls." |
| Intensifier | "This is truly important." | Delete "truly". Say why it matters. |
| Enthusiasm | "We're excited to propose..." | "This document proposes..." |
| Minimizer | "Simply call the endpoint." | "Call the endpoint." |
| Chat residue | "Feel free to leave comments!" | Delete. |

## Typography

- **Em dashes** as the default way to join clauses. Use a period, a comma,
  or parentheses. RFCs, being ASCII, use none.
- **Bold** for emphasis. Bold a term once, where it is defined, or not at
  all.
- **Emoji**, including check marks in lists. Use words.
- **Arrows** (→, ->) in prose. Use a verb.
- **Colon setups**: "One rule: never..." where a sentence would do.

## Structure

- **The bold-label bullet list**: `- **Security**: Short-lived credentials
  bolster security.` Write a paragraph, or a list of plain items.
- **Fragments in bullets** that carry the argument. If the bullets need
  "because" between them, they are a paragraph.
- **Thin sections**: a heading with one or two sentences under it. Merge
  them.
- **Formula headings**: "Why this matters", "Key benefits", "The key
  insight", "Conclusion", headings phrased as questions.
- **Stacked sentences** over 40 words, joined by dashes, semicolons, and
  parentheses. Split them.

## Precision

| Pattern | Example | Rewrite |
| --- | --- | --- |
| may/could potentially | "This could potentially cause a failure." | "If the pod restarts, clients on that node can't refresh for up to 4 s." |
| can help ensure | "Retries can help ensure availability." | "A client retries 3 times before it fails." |
| vague magnitude | "Significantly reduces latency." | "Reduces p99 latency from 800 ms to 120 ms." |
| vague quantity | "Various services use tokens." | "14 services use tokens." |
| aims to | "TRS aims to refresh tokens early." | "TRS refreshes a token 10 minutes before it expires." |

## Terminology (reading only)

- Elegant variation: one concept, several names.
- Coined metaphors used as names: "the funnel", "the moat", "the
  ceiling", with no definition.
- Undefined acronyms.
- A term used before it is defined, with the definition several sections
  later.

## Economy (reading only)

- The same point in the summary, the body, and the conclusion.
- Preambles: "Before we get into the details, it's important to understand
  some background."
- Meta commentary: "as argued below", "this is discussed at length later".
- Status prose that narrates the doc's own history in the body.

## From the USU technical writing standards

The USU guidelines name these patterns. They are general faults of technical
prose, not signs of generated text, but they make a doc harder to read.

| Pattern | Example | Rewrite |
| --- | --- | --- |
| Opinion or emotion | "We believe the cache will help." | "The cache serves 80% of reads in staging." |
| Redundancy | "The end result is exactly identical." | "The result is identical." |
| Wordy phrase | "Due to the fact that the pod restarts..." | "Because the pod restarts..." |
| Vague word | "Startup is really quite slow." | "Startup takes 40 s." |
| Non-specific reference | "Raise the limit a bit." | "Raise the limit from 50 to 80 requests per second." |
| Generalization | "Everyone knows retries are safe." | "Retries are safe because every write is idempotent (Section 4)." |
| Inflated word | "The agent utilizes the cache to facilitate reads." | "The agent reads from the cache." |
| Vague opener | "This means the job retries." | "A failed health check means the job retries." |
| Hidden actor | "The token is refreshed before it expires." | "The scheduler refreshes the token before it expires." |
| Acronym not expanded | "Each backup is encrypted with the DEK." | "Each backup is encrypted with the data encryption key (DEK)." |
| Cliché | "Multi-region is easier said than done." | "Multi-region needs a second database and a failover runbook." |
| Tense shift | "Before the host wrote the file, it checks the path." | "Before the host writes the file, it checks the path." |

The scanner also reports, without scoring:

- `passive_sentence_share`: the share of sentences with a passive verb.
  The gold docs are near 30%. Look only for passives that hide the actor.
- `contractions_per_k`, `first_person_per_k`, `second_person_per_k`: for
  checking register and narrative person against the rubric.
- `undefined_acronyms` and `vague_openers`: lists to check by reading.
