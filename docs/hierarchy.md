# ProPopuli conversation hierarchy

Proprietary terminology (see [LICENSE](../LICENSE)). Smallest unit first; each level is contained in the next.

```text
sample  ⊂  branch  ⊂  fractalpop  ⊂  subpop  ⊂  pop
```

| Level | Meaning | Implementation |
|-------|---------|----------------|
| **sample** | One publishable utterance (title+body or a reply line) | `Post` body/title; `Comment` body |
| **branch** | Nested subthread inside a fractalpop | `Comment.parent_id` chain |
| **fractalpop** | Local conversation: one topic and its reply tree | `Post` + `Comment`s on that post |
| **subpop** | Umbrella niche: many fractalpops under one symbol | `Hub` — shown as **s\\{slug}** |
| **pop** | The whole ProPopuli platform | All subpops and accounts |

## Routes (symbolic vs URL)

- **subpop:** display `s\introduceyourself` → `/s/introduceyourself`
- **fractalpop:** `/p/{post_id}`

## Gate

The **Reframing Gate** runs on reply **samples** (`POST /posts/{id}/comments`), not on the opening post of a fractalpop.

## Sovereignty

Users may create **subpops**. Only the platform operator (env-configured account) may remove a subpop or apply account-level bar/timeout.
