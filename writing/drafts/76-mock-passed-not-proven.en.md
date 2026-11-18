# The Mock Passed. The Real Chain Didn't.

> Column: Knowledge Garden | Collection: Engineering | Source: wiki/concepts/SDD regression baseline and Mock isolation (desensitized) | Status: Drafted, coming soon

The conclusion first: a Mock regression passing proves only that the page can consume Mock data and that rendering, interaction and navigation behave as expected. It does not prove the server data is reliable, it does not prove cross-system consistency, and it certainly does not prove that real payment, signing or write-off flows work. Verification evidence has to be stated by capability level; lower-level evidence cannot stand in for a higher-level conclusion. Treating a Mock result as a real-chain result is the most common form of verification overreach.

## The regression baseline: decide what to verify before changing anything

A regression baseline moves the question "what should be verified after this change" to before the implementation: fix the scope of existing behaviour to protect, the scenario inputs, the expected results and the evidence status, then decide the record granularity by the risk of the change.

High-risk changes get an independent baseline record: cross-page changes, interface contracts, shared components, payment and signing, permission state, or core existing flows each get their own baseline, recording the required scenarios, the assertions to protect, the Mock setup, the verification results and the blockers. A single page with limited impact goes into the task record; a low-risk change keeps the ordinary verification record. When the impact grows, the regression level is raised.

The baseline also carries a hard gate: with required test items lacking results, the development stage must not enter "verified". A baseline is not a checklist filled in afterwards; it is the acceptance scope fixed before the change begins. Without it, what the regression covers and how far it goes are left to whoever happens to be running it.

## The boundary of Mock: what it can prove

Mock's value is stability: pages and request orchestration can be verified repeatedly without depending on real services. But its boundary has to be written down explicitly, or Mock quietly turns from a test double into an acceptance double.

First, what it can prove: a regression completed after the page actually hits and consumes Mock data proves frontend rendering, state, interaction, navigation and the simulated request shape. Note the qualifier in that sentence: the page has to actually consume the Mock data. A read-only request going through, or Mock data being ready, does not count. Where a page references an interface, the page must really run through the data, state, interaction and navigation checks.

Then what it cannot prove: whether the server data is reliable, whether systems agree with each other, whether real payment, SMS, signing, write-off or lease activation succeed. Those conclusions can only come from end-to-end acceptance over the real business chain; a Mock regression cannot give them.

A blurry boundary produces two mistakes. The first is extrapolating a Mock conclusion: the Mock node responds, so the page is declared implemented and the Mock node closed — while the page has never actually consumed the Mock data. The second is treating Mock data as a contract: enlarging the array a Mock returns only adds test data inside the existing response shape; it cannot introduce pagination parameters, pagination response fields or pagination interaction. Pagination needs a formal interface contract and a page-design basis; where the contract defines no pagination, the regression verifies against a one-shot array and page scrolling.

Mock isolation carries two more engineering disciplines. Route whitelisting is built on "method plus real URL", so a query and a submission on the same path cannot contaminate each other; unregistered interfaces keep hitting the original test service, and production builds force Mock off. Requests hitting an external Mock must have signing and credential headers stripped, so test account credentials are not sent to a third party; production builds also have to be checked to contain no Mock domain.

## The evidence ladder: six levels, each minding its own account

Verification evidence is stated by capability level, each level accounting only for itself:

1. **Static checks, type checks and builds**: prove the code can be analysed, compiled or packaged.
2. **Unit tests and request assertions**: prove local logic, contract mapping or interface Mock data readiness meets expectations; they cannot stand in for page acceptance.
3. **Page code referencing a Mock interface**: proves only that the integration path exists; the real page still has to confirm data sync, rendering, state, interaction and navigation.
4. **A completed Mock page regression**: proves the frontend side behaves as expected, after which the corresponding Mock node may be closed.
5. **Integration in the test environment**: proves real service responses and frontend orchestration can work together.
6. **Real business end-to-end**: the only level that can prove payment, signing, write-off, state refresh and cross-system consistency.

The point of the ladder is that conclusions cannot skip a level. All unit tests green does not let anyone write "the page is accepted"; a Mock regression passing does not let anyone write "payment is verified". Each level of evidence supports only its own level of conclusion; a higher conclusion needs higher evidence.

## The practice: layer the verification first, then conclude

1. **Set the baseline before the change starts**: decide the record granularity by risk; high risk gets its own document, and no required test item without a result may enter "verified".
2. **Mock only inside the whitelist**: register routes by method plus real URL, let unregistered interfaces use the original test service, and force Mock off in production builds while checking no Mock domain remains.
3. **Mock data being ready does not mean the page is implemented**: the page has to actually consume the Mock data and complete the data, state, interaction and navigation checks before this level counts as passed.
4. **Do not extrapolate Mock conclusions**: enlarging a returned array introduces no pagination; a Mock regression passing proves nothing about server data, cross-system consistency or the real business chain.
5. **State the evidence level when concluding**: before saying "verified", say which level the evidence belongs to; when a higher conclusion is needed, run the higher verification.

## One line to close

The Mock passed, but the real chain didn't: the regression baseline decides what to verify first, Mock is accountable only for its own level, and conclusions about the real business chain can only come from evidence on the real business chain.
