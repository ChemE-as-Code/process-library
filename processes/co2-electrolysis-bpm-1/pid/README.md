# P&ID sheets

DEXPI 2.0.1 XML, one file per sheet. Start a new one with the `pid-draft` skill.

- `P-01.xml`: Skid A of #330 (train 1xx), `P-02.xml`: Skid B (train 2xx). Both are generated
  (`plant.yaml` `generator:`) by `scripts/draft_P-01.py` and `draft_P-02.py` from the frames in
  `frames/` (the empty sheets with their title blocks, as `cheme sheet new` wrote them). Never
  edit them by hand: change the script and run `cheme regen P-01 P-02` (DESIGN.md D-017).
