# Canonical Task Specification — OAuth2 Device Flow

## Task Title
Add OAuth2 Device Authorization Flow to this Express App

## Background
OAuth 2.0 Device Authorization Grant (RFC 8628) allows devices with limited input capabilities (smart TVs, CLIs, IoT devices) to obtain OAuth tokens. The user authenticates on a secondary device (phone/browser), and the device polls for the token.

## Requirements

### Functional Requirements

1. **Device Authorization Endpoint** (`POST /oauth/device/code`)
   - Accept: `client_id`, optional `scope`
   - Return: `device_code`, `user_code`, `verification_uri`, `verification_uri_complete`, `expires_in`, `interval`
   - Generate cryptographically random `device_code` (min 16 bytes) and human-readable `user_code` (8 chars, uppercase, no ambiguous chars: `0`, `O`, `I`, `l`)
   - Store pending authorization in database with TTL = `expires_in` (default: 300 seconds)

2. **Token Endpoint** (`POST /oauth/token` — device flow grant type)
   - Accept: `grant_type=urn:ietf:params:oauth:grant-type:device_code`, `device_code`, `client_id`
   - Poll handling:
     - Return `authorization_pending` until user completes auth
     - Return `slow_down` if polling faster than `interval`
     - Return `expired_token` if TTL exceeded
     - Return `access_denied` if user explicitly denies
     - Return `access_token` (+ optional `refresh_token`) once authorized
   - Implement rate limiting: reject polls < `interval` seconds apart

3. **User Authorization UI** (`GET /oauth/device` and `POST /oauth/device/authorize`)
   - `GET /oauth/device?user_code=XXXX-XXXX` — display confirmation page
   - `POST /oauth/device/authorize` — user confirms or denies
   - Must validate `user_code` against pending authorizations
   - On confirm: mark authorization as approved, associate with authenticated user's identity
   - On deny: mark authorization as denied

### Non-Functional Requirements

4. **Security**
   - `device_code` must not be guessable (use `crypto.randomBytes`)
   - `user_code` must use constant-time comparison to prevent timing attacks
   - Implement exponential backoff enforcement (track last poll time per `device_code`)
   - Access tokens must be signed JWTs (reuse existing token signing infrastructure if present)

5. **Error Handling**
   - All errors must return RFC 8628-compliant JSON error responses:
     ```json
     { "error": "authorization_pending", "error_description": "..." }
     ```
   - HTTP status codes: 400 for client errors, 401 for auth failures, 500 for server errors

6. **Testing**
   - Unit tests for: code generation, user_code formatting, poll rate limiting, TTL expiry
   - Integration tests for: full happy-path flow, denial flow, expiry flow
   - Test coverage ≥ 80% for new files

7. **Documentation**
   - JSDoc on all exported functions
   - Update existing API documentation file with new endpoints
   - Add `.env.example` entries for any new environment variables

## Acceptance Criteria

- [ ] `POST /oauth/device/code` returns valid RFC 8628 response structure
- [ ] `POST /oauth/token` handles all 5 poll states correctly
- [ ] `GET /oauth/device` renders confirmation page with `user_code`
- [ ] Polling rate limit enforced (rejects requests < `interval` apart)
- [ ] TTL expiry returns `expired_token` error after `expires_in` seconds
- [ ] All new code passes TypeScript strict mode (no `as any`)
- [ ] All CI checks pass on first push
- [ ] Copilot code-review approves with zero blocking comments

## Out of Scope
- OAuth client registration (assume `client_id` is pre-registered)
- Refresh token rotation (implement simple refresh token issuance only)
- Multi-tenant support

## Reference
- RFC 8628: https://datatracker.ietf.org/doc/html/rfc8628
- RFC 6749 (OAuth 2.0 core): https://datatracker.ietf.org/doc/html/rfc6749
