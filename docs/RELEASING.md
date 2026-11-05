# Branches and releases

## One main branch

`main` is the only long-lived branch, and it's always usable:
- `specs/` has the source of every parser.
- The tool folders (`ALEAPP/`, `iLEAPP/`, `Cellebrite Physical Analyser/`, `Magnet AXIOM/`) contain the matching generated files.

Users download `main` (or a release) and install from the tool folders. There are no separate branches per tool or per app.

## Making a change

1. Create a short-lived branch, such as `parser/BE-2dehands` or `fix/cellebrite-timestamps`.
2. Edit `specs/...` or `framework/...`, then run:
   ```
   python obscure.py test
   python obscure.py build
   ```
3. Commit the spec change **and** the regenerated tool folders together, then open a pull request to `main`.
4. CI (`.github/workflows/ci.yml`) runs `validate`, `test` and `build --check`. It fails if a tool folder doesn't match the specs.
5. Merge the pull request and delete the branch.

## Publishing a release

Tag `main` with a version and push the tag:

```
git tag v0.1.0
git push origin v0.1.0
```

`.github/workflows/release.yml` then creates a GitHub release with one zip per tool. Each zip contains `install.py`, so it works on its own:

- `project-obscure-ALEAPP-v0.1.0.zip`
- `project-obscure-iLEAPP-v0.1.0.zip`
- `project-obscure-Cellebrite-PA-v0.1.0.zip`
- `project-obscure-Magnet-AXIOM-v0.1.0.zip`
