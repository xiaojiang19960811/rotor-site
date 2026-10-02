# WebRTC White Screen: Don't Rush to TURN

> Column: Lab Log ｜ Collection: AI Infrastructure ｜ Source: wiki/bugs/2026-08-05-opentalking-webrtc-private-candidate-white-screen ｜ Status: first draft

A real-time dialogue project once hit a public white screen: the page could create a session, briefly showed "connected," but the stage never got remote video, and the server logged ICE failure. The first instinct is usually "add TURN" — but TURN would have fixed nothing here. The root cause was a wrong address published in the SDP; no relay can rescue a candidate address that was wrong from the start.

## The real root cause

The media service ran in a container, and its SDP answer carried the container's private-network host candidate. A public browser can't reach that private address, so no ICE candidate pair could ever form. The deployment didn't use TURN at all; opening TURN ports doesn't auto-correct a bad host candidate.

Investigation found a second trap: the system's ephemeral port range was UDP 32768–60999, but the security group only opened 40000–60000. Even with the address rewritten correctly, a randomly chosen port below 40000 would still fail intermittently.

Two lessons: a reachable page and healthy API checks prove nothing about the media path; when ICE fails, read the SDP and the candidate addresses before adding relays.

## The fix: rewrite the address, don't add a relay

The fix was an environment variable for the public IP: it rewrites only private, loopback, link-local, or unspecified host candidates in the SDP, plus the connection and RTCP addresses; relay candidates stay untouched. The security group was reopened to match the system's actual ephemeral port range — the range comes from the machine's real configuration, not a guessed interval. The deployment docs now say "configure from the system's actual output," so the next machine doesn't relearn this.

The frontend changed too: after persistent WebRTC drops or failures, it no longer sits stuck on "connected" — it releases the session and shows an accurate public-IP/UDP-port checklist. Honest state is step one of debugging.

Verification used a real machine: a genuine public-browser session, video element ready, frame dimensions present, `ICE completed` in server logs. HTTP health checks alone don't count as acceptance.

## It recurred twice — the variable never reached the process

The issue came back twice after the fix, both times for the same reason: the config never reached the running process.

First, only the repo's `.env` was edited, but the adapter read the process environment — the answer still carried the private address. Second, someone launched the binary directly during debugging, bypassing the unified start script and env files, so the process environment had no public IP at all.

The recurrence-proof loop: the production entry point is fixed to a single persistent script that passes env files explicitly to the process; startup validates the public IP as globally routable, and reusing an existing process compares environments — mismatch fails fast. The health endpoint exposes the public-IP configuration state, and deployment acceptance must check it before running one real browser session.

## When TURN is actually needed

Complex NAT, multi-egress, and corporate networks may genuinely need STUN/TURN. But that's a conclusion reached after reading ICE logs and mapping the network topology — not a first reaction. Treating TURN as a cure-all hides the real address-publication problem and adds a relay to maintain.

## In short

The WebRTC triage order: check whether the SDP candidate addresses are right, then whether the UDP port range is fully open, and only then consider a relay. And an environment variable in a file doesn't count — it counts when it's in the process.
