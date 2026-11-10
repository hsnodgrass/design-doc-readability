# Token Refresh Service

Status: Draft. Author: Platform team. Last updated: 2026-11-10.

## 1. Introduction

Services in the production cluster authenticate to the registry and the
storage API with OIDC tokens that expire after 60 minutes. Each of the 14
services that use these tokens refreshes them with its own code. In the last
two quarters, 6 of 23 paging incidents were caused by a token that expired
before it was refreshed.

This document specifies a shared token refresh service (TRS). TRS holds
tokens for its clients and refreshes each one before it expires. Clients ask
TRS for a token instead of minting one.

## 2. Terminology

Client: a service that requests tokens from TRS.

Token: an OIDC access token with an expiry time (`exp`) set by the issuer.

Refresh margin: the time before `exp` at which TRS refreshes a token. The
default is 10 minutes.

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in RFC 2119.

## 3. Goals and non-goals

TRS has three goals:

1. No client receives a token that expires in less than the refresh margin.
2. A client can get a token with one call to a local socket.
3. A failure of TRS does not stop clients that already hold a valid token.

TRS does not issue tokens, and it does not change how audiences or scopes are
chosen. Those stay with the issuer.

## 4. Design

### 4.1. Components

TRS runs as a DaemonSet, one pod per node. Each pod listens on a Unix socket
that is mounted into client pods. A pod keeps tokens in memory only. It
never writes a token to disk.

The scheduler in each pod tracks the `exp` of every token it holds. When a
token reaches its refresh margin, the scheduler requests a new one from the
issuer. If the request fails, it retries with exponential backoff, starting at
1 s and capped at 30 s.

### 4.2. Request flow

A client sends a request that names the audience it needs. If TRS holds a
token for that audience whose `exp` is more than the refresh margin away, it
returns that token. Otherwise it requests a new token, waits for it, and
returns it. A request MUST NOT wait longer than 5 s; after that, TRS returns
an error and the client SHOULD fall back to its cached token, if it has one.

## 5. Failure modes

If a TRS pod is down, clients on that node cannot get new tokens. Clients
that hold a token can keep using it until it expires, which gives the pod up
to 60 minutes to recover. The kubelet restarts a failed pod, and in the
staging cluster a restart took 4 s at the 99th percentile.

TRS does not share state between nodes. A token is therefore minted once per
node per audience, rather than once per cluster. At 300 nodes and 4 audiences
that is about 1,200 issuer calls an hour, which is within the issuer's limit
of 50 requests per second.

## 6. Security considerations

A process that can open the socket can get any token TRS holds for that node.
The socket MUST be mounted only into pods that are allowed to use every
audience configured on that node. Section 4.1 keeps tokens out of node
storage, so a stolen disk image holds no tokens.

## 7. Alternatives considered

A sidecar per pod would isolate each client's tokens, but it would add one
container to each of about 2,000 pods. A cluster-wide service would mint fewer
tokens, but a failure would affect every node at once. We chose the DaemonSet
because its failure affects one node and it adds one pod per node.

## 8. Open questions

Should the refresh margin be configurable per audience? The registry token is
used for long image pulls, and a 10-minute margin may be too short for them.
