# The Cache Billing Trap: Three Buckets Must Be Mutually Exclusive

> Column: Lab Log ｜ Collection: AI Infrastructure ｜ Source: wiki/bugs/2026-07-11-sub2api-gpt56-cache-write-double-billing ｜ Status: first draft

Cache billing on a model gateway has three buckets: regular input, cache reads, cache writes. They must be mutually exclusive — every token belongs in exactly one bucket. Miss one subtraction and you bill twice. This time a selective upstream port dropped a single subtraction, and write tokens got charged at both the regular input price and the cache-write price.

## Where 2.25x came from

Official pricing charges cache writes at 1.25x the regular input price. Write volume arrives in `cache_write_tokens`, reads in `cached_tokens`, and `input_tokens` is the gross total including the breakdown. The correct bucketing:

```
uncached_input = input_tokens - cached_tokens - cache_write_tokens
cost = uncached_input × input_price
     + cached_tokens × cache_read_price
     + cache_write_tokens × cache_write_price
     + output_tokens × output_price
```

The broken branch computed only `input_tokens - cache_read_tokens`, then fed cache-write tokens into write billing separately. Whenever upstream returned a nonzero write volume, those tokens sat in the regular-input bucket and entered the write bucket a second time. At the official 1.25x write price, the effective charge became 2.25x — 80% above official — before service tiers, long-context, and user multipliers.

The same omission had collateral damage: the biller used `input_tokens + cache_write_tokens` to judge total context, potentially pushing requests under 272k into the long-context tier early.

## Production data: real bug, zero actual overcharge

The interesting part: this bug never fired in production. An audit of 3,952 historical requests for that model found zero with `cache_creation_tokens > 0`; cache reads had 3,900 hits totaling about $251. With write volume permanently at zero, there was no evidence of overcharging — and nothing to refund or claw back.

That doesn't change the nature of the defect: the day upstream starts returning nonzero write volume, double billing takes effect immediately. Treating "hasn't fired" as "fine" is its own kind of luck.

## Why tests didn't catch it

Layered tests all passed: parsing tests proved "we can read the write volume," pricing tests proved "we can price it." Nobody covered the vertical loop — raw usage into bucketing into cost breakdown and stats, end to end.

More insidious: the test helper itself used the old formula `input - cache_read`, so implementation and tests were wrong in perfect agreement. And the dedicated test file carried a build tag that the ordinary full test run skips. Tests and implementation confirming each other's wrong assumption makes the gate decorative.

## The lesson on selective upgrades

This used a "selective upgrade" strategy: no full upstream merge, hand-ported by topic. The upstream patch actually contained four things: write-volume alias parsing, price handling, mutually exclusive bucketing, and an end-to-end regression test. The local port took the first two and dropped the last two.

The process-level root cause was a missing coverage matrix: every upstream semantic hunk mapped to its local landing spot and its end-to-end test. The v0.1.150 ledger marked the topic "fully absorbed," later versions audited only the delta, and the wrong baseline was trusted by default — the defect rode along.

The fix itself was simple: subtract the write volume in bucketing, add the missing regression test, and carry the write-volume field through protocol conversion. Only after the full suite passed was the topic truly absorbed.

## In short

Billing code isn't correct when unit prices are right; it's correct when every cent has exactly one home. Three mutually exclusive buckets is self-evident — but self-evident rules don't enforce themselves. Vertical loop tests do, plus porting discipline that gives every upstream semantic change a local landing spot.
