# Internal Signing Is Not a Bypass: Manage Trust First

> Column: Garden ｜ Collection: AI Infrastructure ｜ Source: wiki/projects/desktop-client-internal-signing-verification (desensitized) ｜ Status: drafted, upcoming

Conclusion first: without an official developer certificate, internal self-signing can carry a desktop client through automatic updates, but it is not a bypass. It moves the work of trust management from the certificate authority to your own hands. Getting a signature out is only the first step; before self-signing enters official distribution, four things need rules: who trusts it, how far that trust reaches, how it is recovered if lost, and who holds the private key.

## Self-Signing Is Not Official Endorsement

The first distinction is between self-signing and official signing and notarization. An official certificate comes with a ready-made chain of trust: the system recognizes the issuer, and users need no extra step. Internal self-signing has no such chain; the system does not trust it by default, and a block at install time is normal.

That means two things. First, trust must be explicitly granted by the user; it cannot be assumed, and it cannot travel automatically with the installer: shipping the certificate inside the package does not mean the user's machine trusts it. Second, the official distribution process must not change until self-signing is verified: verification must use isolated test packages, while the official client and the official update source stay untouched until every precondition is confirmed.

Calling self-signing "the same as official signing" costs twice: when it fails on another machine, nobody can say why; and when an isolated verification is written up as "automatic updates supported", a real migration that was never tested gets claimed as done.

## Trust Must Be Scoped Precisely

Trust is not a switch; it is a set of specific parameters: which machine trusts, under which account, for what purpose, and which existing settings are affected.

One reusable practice is to narrow trust to the minimum scope: only on the verification machine, only under the current account, only for the code-signing purpose. A separate test keychain stays locked, and the system's existing keychain search order is left alone. The value of this is traceability: if something goes wrong, you can say where the trust was added, for whom, and for what; when it must be revoked, you know where to go.

The two common shortcuts are the opposite: granting trust globally so every purpose shares it, or changing the search order so a test identity quietly enters the official path. Both destroy the boundary of a "test passed" conclusion: you no longer know whether the official path passed, or a path contaminated by the test identity did.

## Failure Must Leave the Old Version Standing

The core of update verification is not "can the new version install", but "if it cannot, is the old version still there". A complete isolated verification covers at least four cases:

1. **Deferred after download**: the user does not confirm yet, and the old version keeps running, uninterrupted.
2. **Replacement after confirmation**: once confirmed, the new version replaces the old one and restarts into a usable state.
3. **Failed checksum**: when a deliberately wrong checksum is supplied, the update must stop, and the old version keeps running.
4. **Data preserved**: whether the update succeeds or fails, isolated credentials and session records must survive; a successful update must not cost the user their state.

Together these make an update rollback-safe. Testing only the second case tests only the fair-weather path; real users hit the first, third, and fourth. An old version surviving a failed checksum is worth recording more than a successful update, because it proves the update mechanism did not push the user out in the worst case.

## A Backup Must Be Restored in Rehearsal, Not Just Stored

The most self-deceiving part of signing-identity backup is "stored means covered". An encrypted backup on two machines sounds solid; but if it has never been restored and used to actually sign something, it is only an unverified assumption.

The reusable bar is: the rehearsal must go all the way to a real signature. Retrieve the encrypted backup, import it into a temporary keychain, use it to actually sign once, confirm the signature is valid, then clean up the temporary copy and restore the original search order. The rehearsal's value is not in the backup file, but in proving the recovery path works: who holds the recovery passphrase, whether that custody survives losing a machine, and whether temporary copies were cleaned up. Those questions only surface in rehearsal.

Equally, the rehearsal's gaps must be written down honestly: if the machine or account holding the recovery passphrase is lost, the backup may be unrecoverable; if there is not yet an independent off-site recovery method, that is a known risk of the current scheme, not a footnote to omit from the report. A backup is complete only as "stored" plus "restored" plus "known gaps".

## Key-Handover Tradeoffs Must Be Stated

There is no perfect way to hold a private key, only tradeoffs stated openly. An encrypted backup is safer but has a longer recovery chain; a password-free copy is more convenient but cannot be recalled once leaked. What matters is not which one was chosen, but whether the tradeoff was explicitly accepted by the responsible person and written into the handover rules.

Three red lines do not bend:

1. **Only to explicitly authorized packagers**: the private key never travels with the client installer, never sits in an ordinary download directory, and never enters a shared location anyone can reach.
2. **The handover format is whatever actually imports**: when one packaging format is rejected by the system on import, the handover material switches to a format that actually works, rather than insisting on the form of "encryption" while leaving the recipient unable to use it.
3. **When old and new backups coexist, say how they relate**: the encrypted backup stays, the password-free copy is an added tradeoff, not a quiet replacement; the public certificate fingerprint is unchanged, so the recipient can check the identity was not swapped.

Hiding a tradeoff passes the risk to the next person to take over; writing it down tells them what they are actually taking over.

## The Unverified List

The boundaries of this verification deserve to be kept verbatim:

1. Other colleagues' machines have not yet granted certificate trust, and the system-block behavior there is untested.
2. The migration path for the existing informally signed official version is unverified.
3. Real-account login and recovery after an interrupted install have not been walked through.
4. Wiring the internal signing identity into the official packaging process is not done.

These four are not "do casually next"; they are "until they are done, internal-signing updates cannot be claimed as an official capability". The list draws the range within which the conclusion holds, and stops later readers from mistaking an isolated sample for an official release package.

## Close

Internal signing is not a shortcut around the official process; it is taking over the management of trust, backup, and handover: scope trust precisely, leave the old version standing on failure, rehearse backup all the way to a real signature, state key tradeoffs openly, and keep the unverified list verbatim.
