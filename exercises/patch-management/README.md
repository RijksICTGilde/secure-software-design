# Patch Management

In this exercise, we will explore tools to detect and update dependencies. Keeping dependencies up-to-date is crucial for preventing security vulnerabilities. While some platforms use proprietary tools like GitHub's Dependabot, we will use opensource tools to update the dependencies of an example project.

Patch management is important since outdated dependencies have a higher risk of containing exploits. Although it is now a discussion if you should always update immediately or wait for a few weeks/months since there jave been some supplychain attacks happening lately.

You can do patch management manual or automatically. In this part we will explore both.
---

## Prerequisites

- A container engine like Docker or Podman.
- Python 3.

---

## Package Managers

Many package managers include commands to update dependencies. These commands often respect the version ranges specified during installation. Some tools, like Yarn, allow you to ignore version ranges and upgrade packages interactively (e.g., `yarn upgrade-interactive --latest`).

### Using Poetry

First, install the Python package manager Poetry. Refer to the [Poetry documentation](https://python-poetry.org/docs/#installation) for installation instructions.

Next, update the dependencies of the Python example project. Navigate to the `project-repo` directory and execute the following command:

```bash
poetry update --dry-run
```

This command simulates the update process. You will see a list of packages that can be updated.

---

## Renovate

[Renovate](https://docs.renovatebot.com/) is a tool that provides dependency updates for various languages, platforms, and registries, including npm, Java, Python, .NET, Scala, Ruby, Go, Docker, and more. In practice, you would install Renovate to manage updates across all repositories on a platform (e.g., Bitbucket, GitHub, GitLab) and configure it to automatically create pull requests for updates using a `renovate.json` configuration file.

### Example: Scanning a Python Project

In this example, we will scan the dependencies of a simple Python project. The global configuration for Renovate is defined in `config.js`, and the repository-specific settings are in `renovate.json`. Ensure you are in the current directory and run the following command:

```bash
docker run --rm -e RENOVATE_CONFIG_FILE=/config.js \
  -v "$(pwd)/config.js:/config.js" \
  -v "$(pwd)/project-repo/:/usr/src/app/" \
  ghcr.io/renovatebot/renovate:41.86
```

This command generates a `report.json` file. Review the file to identify which packages need updating and what branches would be created if the dry-run mode were disabled. You can use a tool like `jq` to make the JSON output more readable.

## Update cli

[Update CLI](https://www.updatecli.io/docs/prologue/introduction/) is another patch management tool that helps you to update any dependency. Its much simpler then renovate to use. Install the [cli tools](https://www.updatecli.io/docs/prologue/installation/) and lets try it.

```bash
updatecli diff --config manifest.yaml
updatecli apply --config manifest.yaml
```

With update CLI you can define your own logic on what to update, this makes it extreemly flexible. See the [documentation](https://www.updatecli.io/docs/core/autodiscovery/) for more information if you are interested.

---
