# A Delete That Reported "In Use" Had Already Emptied the Folder

> Column: Lab Log | Collection: Engineering | Source: wiki/bugs/plugin-repo deletion and backup restore (desensitized) | Status: drafted, coming soon

Conclusion first: when deleting a directory reports "in use", do not read it as "nothing was deleted". In one real deletion, by the time the error appeared, all contents were already gone and only an undeletable empty shell remained. Reading the error as "everything is still intact" was the most expensive misreading in the incident.

## The symptom: a half-finished empty shell

An old plugin repository that had already been migrated was to be deleted. The delete command removed all contents, but the directory itself failed to delete, reporting that a file was being used by another process. The result was an empty directory: it looked cleanly deleted, but it was a half-finished state.

This state is easy to misread. The wording of the error suggests the operation was blocked, and the first instinct is often: since it did not delete, try again, or leave it alone for now. The truth was the opposite: the contents were gone, and the directory remained only because a handle had not been released. The error described a failed finish, not a deletion that never started.

Telling a half-finished state apart requires looking at the contents, not at the directory. That the directory exists proves only that the finish did not complete. Content counts, repository status, and whether key files are readable prove how far the deletion actually went. Taking the existence of the directory as evidence that the contents survive means judging the most critical question by the least informative signal.

## The holders: the wrapper died, the child lived on

The holders fell into two groups, pointing at two different blind spots in checking.

The first was a test gateway started earlier in the session by a background task. Ending the task ended only the outer wrapper process; the child process was still alive, its script path bound to that directory, holding a handle. Judging by whether the outer layer had exited made the ending look clean when it was not.

The second was a running desktop client. It also appeared in the process list matched by path, which shows that a running application can hold a handle on the directory too. Checking only whether the directory was open would not have found this kind of hold.

So the pre-deletion holder check has to ask the precise question: does any process have its working directory or script path inside this directory. After ending a task, check again whether any child process survived. An outer exit does not mean the whole process chain exited.

## The real loss: the only local copy of work in progress

The empty shell itself was worthless. What mattered was what had been cleared along with it. The repository still held a package under active development, including several modules and their tests written that same day, which existed only there. The migration had assumed that the new repository already held a package of the same name, but in fact the new repository held only a few other packages, and this one was not among them.

This is the class of items that must be confirmed individually before deletion: uncommitted work, packages that exist only locally, and files not yet merged into their new location. The way to confirm is not to ask whether the old repository is still in use, but to name each item: is this package in the new location, in which directory, are the files there. A general claim of "already migrated" cannot carry that check, and a matching name does not mean a completed migration.

## What counts as a successful restore

Fortunately, a full backup had been made before deletion, excluding rebuildable dependency directories. After restoring, the restore counted as established only when three checks all passed:

1. **File count**: the file count after restore matched the backup exactly.
2. **Repository**: the repository was intact and its status check was normal.
3. **Spot checks**: the hashes of key sources, tests, and built outputs matched the backup byte for byte.

The dependency directories were not in the backup, since they are rebuildable products that can be reinstalled when needed, and that does not weaken the restore conclusion. But the order is the point: the backup came before the deletion, not after it was remembered. A backup discussed after deletion is no longer a backup; it is a rescue.

## A pre-deletion checklist

The postmortem condenses into a pre-deletion checklist:

1. **Back up first**: a full backup, excluding rebuildable products, that can itself be verified on its own.
2. **Check holders next**: confirm that no process has its working directory or script path inside the directory, and recheck for surviving child processes after ending a task.
3. **Name the unmigrated items next**: confirm item by item that locally unique contents in the directory to be deleted have landed in their new location, and never assume that a matching name means a completed migration.
4. **Restore first on error**: when a directory deletion reports "in use", restore from backup immediately instead of retrying the deletion. Retrying deletes an already empty shell, and it can drag out the window before anyone notices what is missing.

## One sentence to close

A delete error tells you only that the finish failed, not that the contents are still there: back up before deleting, restore before retrying, and never use a retry to verify a directory that is already empty.
