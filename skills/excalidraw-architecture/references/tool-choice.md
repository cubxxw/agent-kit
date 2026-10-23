# Excalidraw and Archify choice guide

Choose by the job the artifact must do, not by which visual style looks more
professional.

## Decision table

| Question | Prefer Excalidraw | Prefer Archify |
| --- | --- | --- |
| Primary job | Think, explain, negotiate, brainstorm | Specify, verify, review, hand off |
| Structure | Still evolving; alternatives and unknowns matter | Stable enough to encode as typed facts |
| Human work | Live co-editing, comments, spatial rearrangement | Review exact topology, routes, evidence, and deltas |
| Precision | Helpful ambiguity and hand-drawn tone | Deterministic IDs, schemas, checks, and receipts |
| Source of truth | Conversation or workshop artifact | JSON IR and, optionally, pinned repository evidence |
| Reading | One authored canvas and a guided explanation | Search, focus, route, semantic depth, guided views |
| Change review | Visual before/after sketches | Exact Before / Delta / After architecture comparison |
| Output | `.excalidraw`, SVG, PNG | Checked standalone HTML plus viewer exports |
| Offline boundary | Local source and exports can stay offline | Current HTML may request remote fonts; harden first for zero-egress use |

Choose Archify when two or more of these are essential: evidence-backed nodes,
typed topology, deterministic validation, exact change review, interactive
route exploration, multiple reader views, or a formal architecture handoff.
Choose Excalidraw when two or more of these dominate: divergent exploration,
live facilitation, free spatial composition, rapid human rearrangement,
annotations, or a deliberately informal voice.

## Archify content contract for formal system docs

When the user is deciding storage, caching, and latency tradeoffs, do not make
one overloaded overview. Build a small view set from confirmed facts:

1. Use `architecture` for components, trust/ownership boundaries, the system of
   record, caches, queues, and the primary request route.
2. Use `sequence` for cache hit, cache miss, timeout, retry, and fallback timing.
3. Use `dataflow` for ingestion, transformation, lineage, retention, and
   downstream consumers.
4. Use `workflow` for deployment, approval, incident, or operational ownership.
5. Use `lifecycle` for job, cache-entry, order, session, or failure states.

Make these facts explicit when they are known:

- **Storage:** authoritative store versus derived projection, durability,
  retention, replication, encryption, and owner.
- **Cache:** placement, scope/key, TTL or invalidation owner, hit/miss path,
  fallback, and acceptable staleness.
- **Latency:** critical synchronous path, stated target or budget, timeout,
  retry, backpressure, and which work is asynchronous.
- **Failure:** degraded behavior, recovery route, operational evidence, and
  whether data can be lost or replayed.
- **Decision:** accepted choice, rejected alternative, and the cost being paid.

Never invent latency numbers, consistency guarantees, replication behavior, or
failure semantics. Mark a proposal as a proposal, and put unknowns in a review
card instead of turning them into architecture facts.

## Hybrid handoff

1. Explore alternatives in an Excalidraw workshop scene.
2. Record the accepted question, main path, boundaries, facts, proposals, and
   unresolved unknowns.
3. Start fresh Archify JSON from the matching schema and example.
4. Encode only confirmed topology; keep tradeoffs in cards or guided views.
5. Validate and deliver with Archify. Preserve the original workshop scene as
   reasoning history rather than treating its coordinates as system truth.

## Trigger examples

- “开会一起梳理三个可能的缓存方案” → Excalidraw workshop mode.
- “把讨论后的方案整理成正式 HLD，写清 Redis miss、DB 回源和 p95 预算” → Archify.
- “对比这个 PR 合并前后的服务拓扑” → Archify Before / Delta / After.
- “做一张手绘感产品架构图，大家还能继续拖拽修改” → Excalidraw delivery mode.
