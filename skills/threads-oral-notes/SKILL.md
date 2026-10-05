---
name: threads-oral-notes
description: >-
  When drafting or publishing Threads from first-person thoughts, spoken notes,
  travel or AI reflections; use for human-sounding Traditional Chinese posts,
  light language polish, topic_tag choice, confirm-before-publish, and light
  post-publish review.
---
Turn a user's raw first-person idea, voice note, or journal fragment into a high-quality Threads post. Preserve their judgment and facts. Light language polish is allowed.

## Goal

Posts should feel like a real person thinking aloud: one clear take, concrete detail, low AI texture. Optimize for read-through and replies, not for hashtag volume.

## Hard rules

1. Never publish before the user confirms the exact draft.
2. Keep the user's original judgments, conclusions, and factual claims. Do not invent experiences they did not state.
3. Traditional Chinese for Threads body text unless the user asks otherwise.
4. One `topic_tag` only. No body `#` tags unless the user insists.
5. Stay within 500 characters after draft; validate before showing the draft.
6. Do not put outbound links in the main post. If a source or blog link is needed, put it in the first reply after publish.
7. Never echo access tokens.

## Language polish (allowed)

You may adjust wording so the post reads better aloud and online:

- Compress filler, repeats, and spoken tangents
- Fix grammar, particle choice, and rhythm in Traditional Chinese
- Reorder clauses so the judgment lands in the first two lines
- Soften accidental harshness only when it clearly comes from spoken haste, not from the user's stance
- Prefer concrete verbs and sensory detail already present in the note

Do not:

- Upgrade a tentative take into a confident manifesto
- Add metaphors, slogans, or "lessons" the user did not imply
- Replace their voice with generic influencer or AI essay tone
- Invent scenes, numbers, feelings, or quotes

When polish changes a phrase the user might care about, keep the meaning identical and prefer their distinctive words when those words already land well.

## What travels well on Threads

Prefer posts that:

- Open with a concrete judgment or tension in the first two lines
- Come from lived detail: a place, a conversation, a tool used, a bodily feeling
- End with an observation or quiet question, not a sales CTA
- Sound spoken: short paragraphs, few decorative symbols, minimal quotation marks, no heavy numbered lists
- Invite reply by leaving one unfinished edge ("你们呢", a doubt, a tradeoff)

Avoid:

- Generic AI phrasing, hype, slogan titles, arrow-heavy outlines
- Dumping every thought; cut to one spine
- Stacking hashtags or broad tags like 生活 / 想法
- Links in the body that send people off-platform

## Rewrite workflow

1. **Extract the spine.** From the raw note, name: the core judgment, 1–3 concrete details, and optional closing beat.
2. **Choose form.** Usually one text post. Use a short reply-chain only if the user has two distinct beats that cannot live in 500 characters.
3. **Rewrite with light polish.** Keep first person. Compress, order, and smooth language. Do not upgrade their opinion into a more confident one.
4. **Pick `topic_tag`.** Medium grain, same language as the body when possible: a person, product, city, or clear domain. Prefer tags the user already reused successfully when known. If keyword search is available, compare 2–3 candidates and pick the one with real posts; otherwise ask or use the clearest medium-grain tag.
5. **Validate length.** Write drafts to disk if useful and run a length check. Show only drafts that already pass the 500-character limit.
6. **Show draft + tag + optional first-reply link.** Ask which platforms or whether to post Threads only. Wait for confirmation.
7. **Publish** with the official Threads API text flow and `topic_tag`. Prefer `auto_publish_text=true` for plain text when that path is already working for this account; otherwise create container then publish. Read back `permalink` and return it.
8. **Aftercare when asked.** Check replies and insights later. Draft reply text for confirmation; do not auto-reply.

## API notes (official Graph)

- Base: `https://graph.threads.net/v1.0`
- Auth: env `THREADS_ACCESS_TOKEN`; never print it
- Text publish: `POST /me/threads` with `media_type=TEXT`, `text`, `topic_tag`, and either `auto_publish_text=true` or a later `threads_publish`
- Image / video / carousel need a public media URL and a wait until container status is finished before publish
- Permalink: `GET /{id}?fields=permalink`
- Optional helpers when scoped: keyword/tag search for topic candidates, insights, replies, location search, mentions
- Do not delete or hide replies unless the user explicitly asks

## Quality checklist before showing the draft

- [ ] First lines carry the judgment without a throat-clearing intro
- [ ] At least one sensory or situational detail from the user's note
- [ ] Language is smoothed but still sounds like the user
- [ ] No AI-looking ornaments (heavy quotes, dashes-as-style, emoji spam)
- [ ] One topic tag, accurate and not too broad
- [ ] Under 500 characters
- [ ] Link, if any, planned for first reply rather than body
- [ ] Judgments and facts unchanged from the source note

## After publish

Return the permalink. If the draft planned a source link, post it as the first reply only after the root post succeeds. Offer a later check of replies or views; do not nag.
