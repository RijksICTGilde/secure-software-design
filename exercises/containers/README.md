# Container

In this exercise we will work on creating containers and scan for improvements.

## Prerequisite

A container engine like docker or podman.

## Scanning containrs for vulnerabilities with docker

docker has build in tools to scan containers.

```bash
docker scout quickview nginx:1.29.1
docker scout cves nginx:1.29.1
```

The `scout quickview` command gives you a summary of the CVES in a container. the `scout cves` give you a list of the CVEs. When you start scanning, you will see that many containers you use daily contain some CVEs. It often needs extra effort to reduce the security risk. Many organizations do not take the time to do this.

## base containers

Base containers are containers that are existing containers that you use to expand and add your own software. There are many base containers to choice from when building software. There are basic linux containers or your can get specific containers for programming language. Sometimes organizations have recommended own managed base containers. picking a base container can impact the amount of security vulnerabilities significantly. Bellow are some examples of base containers and their security impact.

| Base       | Description                                             | Details                                                                               |
| ---------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Ubuntu     | contains the full ubuntu distribution                   | Easier to develop in but can create allot of security issues                          |
| Alpine     | basic linux version based on musl libc + busybox.       | using this reduces the attack surface significantly but still a medium attack surface |
| Distroless | has no package manager, no shell, no OS utilities       | This make it hard to debug, but the attack service is very low                        |
| Scratch    | contains nothing and can only be used in specific cases | No additional attack surface                                                          |

Lets have a look at the CVEs of the base containers. Make sure you are in this folder and execute the following.

```bash
docker scout quickview ubuntu:24.04
docker scout quickview alpine:3.22.1
docker scout quickview gcr.io/distroless/base-debian12
docker build -f ./Dockerfile.scratch -t test:scratch .
docker scout quickview test:scratch
```

as you can see, the number of CVEs decreased with stricter base containers that have less dependencies. But if you started using the containers for real, it is also harder to debug or build the containers for real software. You might miss dependencies or libraries your software expects.

## Secure java & go app

In this part we are going to take two programming languages and create a container. We focus on creating a secure container.

Multi stage container can help you reduce the number of things that are in your final container. this also reduced the attack surface. Often a distroless or scratch container have multistage builds.

### java

We prepared a simple java application in java-src. The Dockerfile.java builds the application into a container.

```bash
docker build -f ./Dockerfile.java -t test:java .
docker run --rm -i test:java
```

if you scan this application you will see it contains a low number of CVEs

```
docker scout quickview test:java
```

We now rebuild it without a multistage build and without the distroless base image

```bash
docker build -f ./Dockerfile.java2 -t test:java2 .
docker run --rm -i test:java2
```

if you scan this application you will see it contains more CVEs

```
docker scout quickview test:java2
```

These are ofcource simple examples and it might be a bit more difficult for real software to create distroless containers.

### go

We prepared a simple go application in go-src. The Dockerfile.scratch builds the application into a container

```bash
docker build -f ./Dockerfile.scratch -t test:scratch .
docker run --rm -i test:scratch
```

if you scan this application you will see it contains a low number of CVEs

## scanning tools

We already introduced you to docker scout but there are many more tools. Before we go into CVE scanners we first going to explore a dockerfile best practice scanner named hadolint. It scans your dockerfile for best practices, including security recommendations.

Make sure you are in this folder and execute the following

```bash
docker run --rm -i hadolint/hadolint < Dockerfile.hadolint
```

the above command gives some tips on how ot change the badly written dockerfile. Try to fix the ones you want.

Two populair tools for scanning images are [clair](https://quay.github.io/clair/) and [trivy](https://trivy.dev/latest/docs/).

### Trivy

Trivy does allot. Find vulnerabilities, misconfigurations, secrets, SBOM in containers, Kubernetes, code repositories, clouds and more. in this exercise will will focus on finding vulnerabilities in containers. but feel free to try other options also.

make sure to install trivy reading the [documentation](https://trivy.dev/v0.18.3/installation/)

Once trivy i installed we can start using it to scan containers. compare `trivy` results with `docker scout`

```bash
trivy image ubuntu:24.04
docker scout cves ubuntu:24.04
```

First thing you notice is that the number of CVE discoveries are different. the reason for this is that they use different sources for their CVE database. Another difference is the detection scope. this means you will have to evaluate which tool you want to use for your scanning.

Lets create a new image that has known vularabilities. find them with trivy and then fix them.

```bash
docker build -f ./Dockerfile.cve -t test:cve .
trivy image test:cve --output=json
```

let find all cves that are fixable using the json output and the jq application.

```bash
trivy image --ignore-unfixed --format json test:cve
trivy image --ignore-unfixed --format json test:cve | jq '.Results[].Vulnerabilities[] | select(.PkgID == "tar@1.34+dfsg-1build3")'
```

Now try and fix the Dockerfile.cve to not show the CVEs and validate it is gone.

### Copacetic

copa is a CLI tool written in Go and based on buildkit that can be used to directly patch container images without full rebuilds. copa can also patch container images using the vulnerability scanning results from popular tools like Trivy.

for more information see the [documentation](https://github.com/project-copacetic/copacetic)

lets scan an nginx image for cves

```bash
trivy image --pkg-types os --ignore-unfixed -f json --output nginx-report.json docker.io/library/nginx:1.21.6
```

lets [install copa](https://project-copacetic.github.io/copacetic/website/installation) and fix these cves

```bash
copa patch -r nginx-report.json -i docker.io/library/nginx:1.21.6
```

copa should create a new container called docker.io/library/nginx:1.21.6-patched

lets scan it again to see the results

```
trivy image --pkg-types os --ignore-unfixed -f json --output nginx-report-patched.json  docker.io/library/nginx:1.21.6-patched
```

compare both nginx-report-patched.json and nginx-report.json.

Be aware that automatic patching can break the application. so you should always test it after patching. 

## End

Thank you for trying this exercise, if you have improvements feel free to create a PR.
