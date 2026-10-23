# "Admin Account" Doesn't Mean "Admin Privileges"

> Column: Experiment Log ｜ Collection: Infrastructure ｜ Source: wiki/bugs/Windows low-integrity directory causing NSIS install exit (verified)

Conclusion first: on Windows, "the account is an administrator" and "the process actually holds administrator privileges" are two different things. A desktop client's installer, launched from an engineering directory, made its setup wizard vanish the moment "install for all users" was selected: no error, no UAC prompt. The root cause was neither the account nor UAC, but the file itself: the installer had inherited a low integrity label from its parent directory, and Windows starts a process at the lower of the user integrity level and the file integrity level. The installer's elevation child process never reached the level it needed and exited directly.

## The symptom: a silent disappearance

Double-click the installer → the setup wizard appears → select "install for all users" → the wizard vanishes. No error dialog, no UAC elevation prompt, no log hint. The usual first guesses: is UAC broken? Is the installer corrupt? Does the account lack privileges?

Eliminated one by one: the account was genuinely in the Administrators group; the same installer copied to an ordinary Downloads folder popped the UAC prompt and continued normally. The file was fine, the account was fine — the problem followed the directory.

## The controlled experiment: same file, different directory

Hash comparison of the installers in the original directory and the Downloads folder: identical digests, no difference in the file itself. Then the same diagnostic program read process integrity in each directory: low integrity with a failed elevation check on one side, high integrity with a passed check on the other. In both diagnostics, the account type read as Administrator.

Identical account identity, yet the actual process integrity differed. **"Is an administrator" describes the account; "can elevate" describes the process.**

## The definition: integrity level is a second gate

Beyond ACLs (who can read and write), Windows has Mandatory Integrity Control: integrity levels. When a process is created, the system takes the lower of the user token's integrity and the executable file's integrity as the new process's integrity.

A low integrity label propagates down from a parent directory through inheritance: once a directory carries the low label, files landing inside it pick it up. The installer, dropped into the engineering directory by the build flow, inherited the low label along the way. From then on, no matter which account double-clicked it, the file side held the process's integrity down.

NSIS's "install for all users" path goes through an elevated child process. That child needs to write into system-level directories; denied the integrity it required, it exited directly with code 0x666666, taking the outer wizard with it. There wasn't even a chance for a UAC prompt: the prompt only appears when elevation is possible — when elevation was never on the table, the process simply left.

## The troubleshooting order: check the file before the account

The order this postmortem settled on:

1. **Read the exit code first**: a vanishing installer is not "no response" — NSIS gave 0x666666. An exit code is a direction.
2. **Check the file's mandatory label**: run `icacls <installer>` and look for Low Mandatory Level; if present, walk up the parent directories to find where the label came from.
3. **Read actual integrity, not the account name**: measure the process's real integrity level with a diagnostic. Membership in Administrators, or "run as administrator", is no substitute for that one reading.
4. **Isolate the variable**: copy the installer to an ordinary directory with no low-integrity inheritance and launch it there; confirming "a different directory fixes it" rules out "the file is corrupt" for good.

And three don'ts: don't reconfigure the account over this, don't turn off UAC, don't batch-reset the engineering directory's ACLs. The label's origin — which tool set it, and when — is still unverified; changing ACLs now would be treating an undiagnosed condition.

## Closing

Next time an installer vanishes without a word, don't blame the account or UAC first: ask which directory the file came from, then use icacls to see what it inherited.
