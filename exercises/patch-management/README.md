# Patch Management

In this exercise we will use some tools to detect updates of dependencies. It is important to keep updating your dependencies to prevent security vulnerabilities. Some platforms use proprietary tools like githubs dependabot. In this exercise we will try some tools to update the dependencies of an example project.

## Prerequisite

A container engine like docker or podman.

## Package manager

Many package manager include a command to update your dependecies. This is often done using the version ranges you set when installing the package. In some tools you can also ignore the ranges you set to update everything interactively.

lets first install a pyton package manager called poetry. Read the [documentation](https://python-poetry.org/docs/#installation) on how to do this.

then try to update the dependecies of the python example project. make sure you go into the project-repo directory before executing this command.

```bash
poetry update --dry-run
```

As you can see it wants to update 2 packages.

## Renovate

Renovate can provide dependency updates for most popular languages, platforms, and registries including: npm, Java, Python, .NET, Scala, Ruby, Go, Docker and more. In practical use you would want to install renovate to update all repositories you have on a platform and use a renovate.json config file to configure how renovate should update those repositories. In this example we will just scan our local directory, but in real life we would add it to a platform like bitbucket, github or gitlab and let is autocreate PRs for you.

in this example we will scan the dependencies of a simple python project. the global config for renovate are set in config.js. the repository settings are set in a renovate.json. make sure you are executing from this directory

```bash
docker run --rm -e RENOVATE_CONFIG_FILE=/config.js  -v "$(pwd)/config.js:/config.js" -v "$(pwd)/project-repo/:/usr/src/app/"  ghcr.io/renovatebot/renovate:41.86 
```

When you run this command a report.json is created. Try to have a look at which package needs updating and what branch would be created if we did not have dryrun enabled. Using a tool like jq to look at the json might make it more readable.
