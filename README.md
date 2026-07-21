# tzheng.us

A small static personal site. This public repository contains only published site assets.

## Publishing check

Every public HTML page must load `/assets/counter.js`. The repository contains a zero-dependency check that runs in GitHub Actions and through the local pre-commit and pre-push hooks:

```sh
python3 .github/scripts/check_counter.py
git config core.hooksPath .githooks
```

Preview files under `.preview/` are intentionally excluded.
