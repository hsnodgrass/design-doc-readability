# Token refresh redesign

## Background

The current refresh path quietly swallows expiry errors and returns a stale
token. `refresh()` promises the caller a fresh credential, but it lies when the
upstream issuer times out. The retry loop then eats the error budget, and the
cache happily hands out the stale value until the process restarts. This is
the part of the design most incident reviews gloss over.

Every service mesh sidecar token cache rebuild costs a full issuer round trip.
The issuer rate limit window enforcement logic bites hardest during deploys,
when every pod restart storm hits the same endpoint. The old code never
reached the branch the new tests exercise. Two tests fail on the old build;
the rest cover the paths the old build skipped.

## Proposal

We gate refreshes behind a single-flight lock and calendar the rotation so
tokens rotate on a fixed cadence instead of on demand. The lock guarantees
one refresh per key. The scheduler wants a stable clock, so it reads the
monotonic source and ignores wall time. `TokenStore` remembers the last good
token and hands it back when the issuer is down, but only inside a grace
window the config owns.

The token the issuer signs carries a ten-minute expiry, and the key it wraps
rotates daily. The rotation job assumes the clock is in sync and ensures the
old key is retired before the cache sees the next token.

The refresh worker knows the issuer is degraded when two consecutive calls
time out. It then backs off and parks further attempts. We sunset the legacy
`/v1/refresh` endpoint once the new path soaks for two weeks, and we
dashboard the fallback rate so the on-call can eyeball regressions.

The design keeps the failure mode boring. The cache doesn't care which
caller asked first; it just serializes them. The fallback path forgives one
missed rotation, never two. A config flag decides whether the grace window
applies, and the flag defaults to off.

## Alternatives

We considered a token prefetch background goroutine pool design. It
complicates shutdown, because the pool fights the process lifecycle for the
last word on when a token dies. We also considered letting each caller
refresh on its own. That approach hammers the issuer and invites the exact
thundering herd problem the single-flight lock solves.

## Risks

The grace window hides real outages if it runs too long. The metric we
dashboard catches that, as long as someone watches it. A misconfigured
clock skew tolerance setting could also make the scheduler think tokens
expired early. The alert covers this, and the tests catch the obvious
cases. The team agreed the risk is acceptable.
