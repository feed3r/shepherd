---
status: "proposed"
date: 2025-12-30
decision-makers:
  - '@feed3r'
  - '@giubacc'
  - '@AndreaTrasacco'
proposer:
  - '@feed3r'
---

# Choose a proper Changelog generation automatic tool

## Context and Problem Statement

Since this project is approaching the first official release, we need to
investigate some tools to automatically generate the Changelog and release
notes files.

## Decision Drivers

* Tool should be simple to use and configure.
* It must integrate seamlessly with GitHub Actions.
* It should support the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
* It allows us to maintain control over the content and style of the results.

## Considered Options

* **Git Cliff**
* **Commitizen**
* **tag-changelog**
* **changelog-ci**

## Decision Outcome

Proposed option: **Git Cliff**, because it offers the best balance of flexibility, local reproducibility, and resilience to our mixed commit history. It allows us to generate professional changelogs immediately while providing a path to strictly enforce conventions in the future.

## Pros and Cons of the Options

### Git Cliff

[Git Cliff](https://github.com/orhun/git-cliff) is a highly customizable changelog generator written in Rust.

**Usage Considerations:**
It requires a `cliff.toml` configuration file where you can define templates (using Jinja2 syntax) for the changelog output. It can be run locally via CLI or in CI/CD pipelines using the official `git-cliff-action`. It reads the git history and generates the changelog based on the configuration.

*   **Note:** Although written in Rust, it **does not** require a Rust toolchain, `cargo`, or `Cargo.toml` in your project. It runs as a standalone pre-compiled binary, so no other dependencies are required.


* **Good**, because it is highly customizable via a TOML configuration file and template system.
* **Good**, because it is very fast (written in Rust).
* **Good**, because it has an official GitHub Action that simplifies integration.
* **Good**, because it natively supports Conventional Commits.
* **Good**, because it supports local generation and preview, allowing more control and rapid testing without waiting for CI pipelines.
* **Neutral**, requires learning its specific configuration format.

### Commitizen

[Commitizen](https://commitizen-tools.github.io/commitizen/) is a tool designed to define a standard way of committing rules and communicating it (using the conventional commits specification).

**Usage Considerations:**
It is a Python-based tool (`pip install commitizen`). It is often used to enforce commit rules but also includes a `cz bump` command that calculates the next version, updates version files, and generates a changelog. It is opinionated about the format.

* **Good**, because it is a Python tool, fitting the project's ecosystem.
* **Good**, because it handles version bumping in addition to changelogs.
* **Bad**, because it is more opinionated and less flexible in output formatting compared to Git Cliff.
* **Bad**, because it acts as an "enforcer" of standards, making it less resilient to our existing mixed commit history.

### Tag-Changelog

[Tag-Changelog](https://github.com/marketplace/actions/tag-changelog) is a GitHub Action that generates a changelog from git tags.

**Usage Considerations:**
This is purely a GitHub Action. It is triggered by the creation of a git tag. It fetches commits since the previous tag and creates a changelog text. It is designed primarily to populate the "Release Notes" body in GitHub Releases. Updating a `CHANGELOG.md` file in the repo requires additional manual steps or scripting.

* **Good**, because it's simple and requires zero configuration to get started.
* **Good**, because it supports Conventional Commits.
* **Bad**, because it only returns the generated text and doesn't easily support updating the repository's `CHANGELOG.md` file.
* **Bad**, because it lacks local reproducibility, meaning you cannot preview the output without triggering a CI run.

### Changelog-CI

[Changelog-CI](https://github.com/marketplace/actions/changelog-ci) is another GitHub Action for generating changelogs.

**Usage Considerations:**
It generates a changelog upon release creation. It supports configuration via a `changelog-ci-config.json` file (or similar) to group commits (e.g., Features, Bug Fixes). It can commit the updated `CHANGELOG.md` back to the repository.

* **Good**, because it is designed specifically for GitHub Actions integration.
* **Good**, because it supports grouping entries by labels or commit types.
* **Bad**, because it has fewer advanced templating configuration options compared to Git Cliff.
* **Bad**, because it lacks local reproducibility, complicating the testing and configuration process.

## Current Git History Analysis

An analysis of the `shepherd` repository history reveals a mixed adherence to the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) standard. While recent commits largely follow the convention (e.g., `feat:`, `fix:`), older commits and some merge commits do not.

**Implication:**
*   **Git Cliff** is particularly suitable here because it is resilient; it can be configured to group non-compliant commits into a generic "Other" category rather than failing or excluding them entirely.
*   **Recommendation:** To maximize the value of the automated changelog, we should strictly enforce Conventional Commits for all future contributions (potentially via a CI check or git hook).

## Conclusion

**Git Cliff** is the most suitable choice for our project due to its flexibility and, most importantly, its ability to run in a local environment. This allows for testing and assessment without the need to create new tags or commits.
Another strong point is its programmability; the ability to customize output using Jinja2 templates offers significant advantages. While this might seem like overkill for the initial phase, it is likely to prove useful as the project evolves.
