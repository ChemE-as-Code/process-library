The pull request of this case (`processes/hydrazine-1/`, branch `case/hydrazine-1`) fails one library CI test:
`tests/test_utilities.py::test_the_library_builds_strict_with_the_utilities` expects no errors
and no warnings from the strict LCI build. For ethylene-1 the warning was:
"processes/ethylene-1/lca/dataset.yaml: study allocation 'mass' differs from the dataset's default None: the study's is used".

1. Merge the current main first: `git fetch -q origin && git merge --no-edit origin/main`.
2. Reproduce from the repository root (`../..`) with:
   uv run --python 3.12 --with pytest --with pyyaml --with jsonschema --with openpyxl --with ./python --with bw2calc --with olca-schema==2.6.2 --with multifunctional==1.1.2 --with "cheme-as-code[units,lca] @ git+https://github.com/ChemE-as-Code/core.git@753e3577f8c63222c97dadd423c437f54d8d2c32" pytest -q tests/test_utilities.py
   (run it with `cd ../.. && ...` in one Bash call).
3. Fix the cause inside `processes/hydrazine-1/` only (e.g. declare the dataset's allocation consistently
   with lca/lca.yaml, or regenerate the dataset with cheme so they agree); no physics changes.
   Re-run the test until it passes, then `cheme validate` here.
Commit (one commit, message "hydrazine-1: consistent LCA allocation for the strict library build");
do not push. End with STATUS: DONE or STATUS: BLOCKED: <reason>.
