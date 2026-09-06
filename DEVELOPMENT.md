# Developing World Brief with an AI agent

## Two branches, two purposes

- `master` is the production branch connected to the existing Streamlit app.
- `codex/dev` is the integration and preview branch. New work starts here.
- A preview deployment is not created automatically by making a branch.
- Do not merge or push development changes into master until preview acceptance.

## A repeatable development cycle

1. **Describe a reader need.** Say who needs what and give a concrete example:
   "A reader wants Spanish news about solar power in Chile."
2. **Specify acceptance before implementation.** Decide what country means:
   where a publisher is based, where an event happened, or a chosen news edition.
   Define expected results, empty states, update times, and limits.
3. **Ask the agent to inspect the project.** It should report the current branch,
   uncommitted changes, affected files, and existing tests before editing.
4. **Implement on development.** Keep the change focused and explain its tradeoffs.
   Never put credentials into source files.
5. **Test at three levels.** Unit tests check logic; interface tests check user
   flows; real browser/device tests check navigation, layout, and deployment.
   Mocked tests cannot prove a publisher is online or that LINE opens a link.
6. **Review a pull request.** Inspect changed files, CI output, and preview behavior.
   Record the exact commit tested. A green check is evidence, not blanket approval.
7. **Accept and release.** After the reader flow passes, merge to master. Check the
   live page and one original article after deployment.
8. **Observe and recover.** Record failures. Revert the specific release commit if
   necessary; preserve history. Reverting can restore known bugs, so check behavior.

## Useful instructions to give an agent

> Inspect the current code and implement [reader need] on codex/dev.
> First define acceptance criteria. Preserve my uncommitted work.
> Run meaningful tests and show the evidence and remaining limitations.
> Do not merge into master. Prepare a reviewable change and teach me why it works.

For a bug:

> Reproduce [steps] using [device/browser]. Separate confirmed causes from guesses.
> Add a regression test where possible. If you cannot access the device, say so.
> Verify the deployed preview, not just generated HTML.

## Commands (PowerShell, from the project directory)

```powershell
git status --short --branch
git switch codex/dev
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502
git diff --check
git diff
```

Port 8502 keeps development separate from an already-running local app on 8501.
After reviewing files, commit the intended paths and push codex/dev.

## Preview and release gates

Deploy a second Streamlit app using this repository, branch codex/dev, and app.py.
Keep the production app on master. Preview setup and branch protection are pending;
this document does not mean they have been configured.

Before a release, record:
- commit and preview URL;
- automated-test result and CI run URL;
- desktop and Android Chrome result;
- actual LINE result, or clearly "not tested";
- sources/languages/countries checked, plus unavailable coverage;
- the rollback commit and any known regressions it would restore.

GitHub Actions runs the existing offline suite on pushes and pull requests.
It does not make external news requests and does not automatically deploy or merge.
