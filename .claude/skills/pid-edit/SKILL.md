---
name: pid-edit
description: Change an existing P&ID sheet in pid/ - add, remove or modify equipment, lines, valves or instruments - by editing the DEXPI XML directly, then formatting, validating and rendering until clean. Use for any change to an existing sheet.
---

# Editing a P&ID sheet

Read the `dexpi-xml` skill first if you have not in this session; its Conventions and Recipes
(insert a valve or a tee, remove an item, add an instrument, change a DN) cover most edits.

1. **Find the place.** `plantcode show <id or tag>` (an XML id, `TagName`, printed instrument
   tag, `LineNumber` or `PipingComponentNumber`) prints the `file:start-end` of the object's
   block and of its drawing, its owner chain, what it references and what references it, each
   with a line number. For equipment it adds the segment and line at each nozzle and what exists
   only for it (branch segments, tees, whole lines); for a valve or instrument the whole
   instrument chain (loop, sensing, signal lines, actuating system, valve). Read those line
   ranges, not the whole file. `grep -n` is the fallback for
   text that is not an object (`grep -n 'T4750' pid/P-01.xml`).
2. **Look at the region** before you change it:
   `plantcode render pid/P-01.xml --png --crop X0,Y0,X1,Y1` (sheet mm, Y down; take the
   `at X0,Y0,X1,Y1 mm` region `plantcode show` prints for the drawing, plus a 20 mm margin). It
   writes `build/P-01_crop-X0-Y0-X1-Y1.png`, so keep that file as the before picture (or render
   `--rev HEAD` with the same crop later).
   Note free space and nearby coordinates so new symbols sit on the line and off other symbols.
3. **Plan the change in both trees**: what objects are added, removed or changed in the
   conceptual model, and which groups, symbols, node positions, lines and label texts in the
   drawing follow. Removing something: every incoming reference `plantcode show` listed must be
   deleted or re-pointed.
4. **Edit the file in place.** Use readable ids that say what the object is
   (`GlobeValve_FV101_bypass`). Let plantcode write the verbose XML (see `dexpi-xml`, "Writing
   the verbose parts"):
   - **another one like an existing object** (a spare pump, a second identical valve):
     `plantcode copy <id or tag> --prefix NEWID --tag NEWTAG --offset DX,DY`. It copies the
     drawing too, renames every id and prints what it did not copy (the pipes at the original's
     nozzles): connect the copy with fragments;
   - **a new valve, tee, pipe, segment, node or label**: `plantcode fragment <kind> --id ...
     --sheet pid/<sheet>.xml` and paste each part where its comment says;
   - **by hand**: re-pointing references (a pipe's or segment's ends, a ConnectorLine's
     `Source`/`Target`), moving or deleting existing blocks, changing data and label texts.
   Do not write a templating script or a deep-copy script for drawing XML; if copy or fragment
   cannot do something you need, say so in your report.
5. **Format, validate, render**:
   ```sh
   plantcode fmt pid/P-01.xml && plantcode validate
   plantcode render pid/P-01.xml --png --crop X0,Y0,X1,Y1
   ```
   Fix every `error`, then every new `warning`. Repeat until clean. Look at the PNG: symbols on
   their lines, lines meeting at node positions, labels readable and saying the right thing.
6. **Review the change** before committing: `plantcode diff HEAD --list` prints one line per
   changed plant item (`<kind> <class> <id> [tag]: N added, M removed, K modified`). Every line
   should be an item you meant to change. `--list --verbose` lists each change under its item,
   `--list --flat` one line per object
   (`<kind> <class> <id> [tag] (<domain>) <attrs> -> drawn as <owner|not drawn>`): no changed
   plant item should be `not drawn`. `plantcode diff HEAD` writes `build/diff.html` for a person to look at; `--json` is
   the same data for a script.
7. **Keep the lists in step** (`lists-sync` skill): a new or removed tag, line or instrument,
   and a changed DN, go into the equipment, line or instrument list.
8. **Commit** one logical change per commit, message saying what changed on which sheet and why.
   Log the change in `PROGRESS.md` (date, sheet, what, why). `git diff` shows sheets as review
   text with the XML ids as written (after `plantcode git-setup`).

Large restructures (many items, a whole new section) are often easier with a throwaway
generator script: see `pid-draft`.

Never delete a validation finding by deleting the content it is about unless that is the change
you were asked for.
