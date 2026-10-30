# Processes

<!-- include: REFERENCE.md :: ## Processes | body -->

Each published process has a page generated from its `process.yaml` and its folder's README.md.
The publication rules of [Contributing](../contributing.md) apply: only a process with
`publication.status: public` gets a page (`internal` and `candidate` processes are left out
entirely), and its README.md is left out when `publication.exclude` names it. A new public folder
under `processes/` gets its page and nav entry without a change to these docs.
