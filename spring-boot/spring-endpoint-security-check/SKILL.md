---
name: spring-endpoint-security-check
description: Checklist-driven security audit for REST endpoints in a Kotlin + Spring Boot backend (JWT, stateless, MongoDB) — verifies the endpoint can't be reached without a valid token and that one user can never read or modify another user's data (IDOR), then input validation, injection, rate limiting, and secret exposure; reports a findings table and does not patch code. Use whenever a controller/endpoint is added or changed in a Spring Boot project, or when asked to security-test, audit, or find vulnerabilities in endpoints — even without the words "security review". Trigger on phrases like "new endpoint", "is this endpoint safe", "can another user access this", "IDOR", "authorization check", "permitAll", "audit the controller", "security test". If the project has a local security-check skill, read it too — it lists project-specific known gaps and sensitive data types. For a broad OWASP pass over arbitrary code use security-review instead.
---

# Endpoint security check (Spring Boot)

Reports, never edits. Two questions matter most — spend most of the budget there:

1. **Can a request reach this endpoint, or the data behind it, without a valid token?**
2. **Can an authenticated user read or modify data that belongs to someone else?**

## How to use

1. Identify the endpoint(s) in scope and trace the full call path: controller → service → lookup →
   repository / `MongoTemplate` query. Read sibling endpoints only for comparison — a neighbor is not
   automatically a safe reference.
2. Walk sections 1–6 against that path. If the project has a local security skill with
   "sensitive data" deep dives, apply those too.
3. Output the findings table (format below). Do not modify code.

## 1. Authentication

- Handler calls `requireAuth()` (or equivalent) as its first line? With a custom JWT filter there's
  usually no `@PreAuthorize` doing it for you.
- Route covered by `anyRequest().authenticated()`, or does it fall under a `permitAll` matcher
  (`/auth/**`, `/public/**`, static assets, `/actuator/**`)? A new controller nested under a public
  prefix silently loses auth.
- Intentionally public? Check exactly what it returns — public endpoints are the easiest data leak.
- Admin endpoints: role checked from DB on every request (not only a JWT claim), non-admins get
  404/403 consistently; no shared-secret string compare (use constant-time compare if a key is
  unavoidable).

## 2. Authorization (IDOR)

Usually enforced per service, not centrally — check explicitly every time.

- Every method receiving `requesterId` + a resource id: does it compare requester to owner /
  participants / membership **before** reading or mutating? Storing `updatedBy`/`createdBy` is not a
  check. Load-then-save without comparison = HIGH.
- Write vs read permission: "can see it" (participant) ≠ "can edit it" (author/admin). Edit/delete
  usually needs author or admin; reactions/votes may intentionally allow all participants — confirm
  intent.
- Group/shared scope: membership check (and admin check for admin actions) on every operation, not
  only create.
- List/search/sync: query scoped server-side to the requester's own scope; never accept a
  client-supplied `userId`/`groupId` to choose *whose* data to return without re-checking.
- Writes pinned to the caller: request DTOs for "my X" must not carry a `userId` field the server
  trusts.
- Responses use `*Response` DTOs, never raw entities (hashes, tokens, internal flags, other users'
  ids leak through entities).
- Side channels: notification payloads, socket broadcasts, and sync responses must apply the same
  visibility rules as the main endpoint.

## 3. Input validation

- Every id string validated before `ObjectId(id)` (malformed → 500 otherwise).
- `@Valid @RequestBody` DTO with `@field:` bounds (`@NotBlank`, `@Size`, `@Email`, `@Min/@Max`);
  no unbounded strings/lists.
- File uploads: MIME allowlist + size cap + server-generated filename (no path from client).
- Enum/status params parsed safely (invalid → 400, not 500).

## 4. Injection / data layer

- Free text reaching a `Containing`/`Like`/`$regex` query → must be `Pattern.quote`d / escaped
  (ReDoS, unintended matches).
- Hand-written `@Query` strings or `Document.parse` built from input → flag; prefer derived queries
  or `Criteria` builders.
- Mass assignment: DTO → entity copy must not let the client set owner, role, `deleted`, version,
  timestamps.

## 5. Rate limiting / abuse

- Covered by the global rate-limit filter? Expensive endpoints (image processing, broad queries,
  email sending) may need a tighter bucket or per-user cooldown.
- IP-keyed limits behind a proxy: forwarded headers trusted only from known proxy CIDRs.
- Email/SMS-triggering endpoints: per-target cooldown, no account enumeration via different
  responses.

## 6. Secrets / tokens

- Response never contains tokens, hashes, secrets, other users' emails/push tokens.
- New token kinds carry a distinct `type` claim and the consuming endpoint validates it.
- Refresh tokens stored hashed; rotation atomic.

## Severity

- **HIGH** — exploitable by any (un)authenticated user with no special conditions: auth bypass,
  cross-user read/write, secret leak.
- **MEDIUM** — needs a precondition, or couldn't be fully confirmed from code alone.
- **LOW / NOTE** — defense in depth, inconsistency, theoretical.

## Output format

```markdown
## Security findings: <endpoint(s) reviewed>

| Severity | Location | Issue | Suggested fix |
|----------|----------|-------|---------------|
| HIGH | XController.kt:34 (→ XService.kt:107) | update never compares requesterId to entry owner | Load entry, require ownerId == requesterId before save |
```

No findings → single line `No issues found against the checklist.` instead of an empty table.
Then a count line ("1 HIGH, 0 MEDIUM, 2 LOW") and a note that findings are advisory — this skill
does not modify code.
