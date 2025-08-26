# Container Security

In this exercise, we will focus on creating secure containers and scanning them for improvements.

---

## Prerequisites

- A container engine like Docker or Podman.

---

## Scanning Images for Vulnerabilities with Docker

Docker has built-in tools to scan images. Let’s analyze an Nginx image:

```bash
docker scout quickview nginx:1.29.1
docker scout cves nginx:1.29.1
```

- `scout quickview`: Provides a summary of CVEs in a container.
- `scout cves`: Lists the CVEs in detail.

You’ll notice that many commonly used containers contain CVEs. Reducing these vulnerabilities often requires extra effort, which many organizations overlook.

---

## Base Images

Base images are pre-existing images used to build your software. Choosing the right base image significantly impacts the number of security vulnerabilities. Below are examples of base images and their security implications:

| Base       | Description                                             | Details                                                                               |
| ---------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Ubuntu     | Full Ubuntu distribution                                | Easier to develop with but may introduce many security issues.                       |
| Alpine     | Minimal Linux version based on musl libc + busybox      | Reduces the attack surface significantly but still has a medium attack surface.       |
| Distroless | No package manager, shell, or OS utilities              | Hard to debug but offers a very low attack surface.                                  |
| Scratch    | Contains nothing; used in specific cases                | No additional attack surface.                                                        |

### Comparing CVEs in Base Images

Run the following commands to compare CVEs in different base images:

```bash
docker scout quickview ubuntu:24.04
docker scout quickview alpine:3.22.1
docker scout quickview gcr.io/distroless/base-debian12
docker build -f ./Dockerfile.scratch -t test:scratch .
docker scout quickview test:scratch
```

You’ll observe that stricter base images with fewer dependencies have fewer CVEs. However, using these images in real-world scenarios can be challenging due to missing dependencies or libraries.

---

## Secure Java & Go Applications

We will create secure images for Java and Go applications. Multi-stage builds help reduce the attack surface by minimizing the contents of the final image.

### Java

A simple Java application is prepared in the `java-src` directory. Build and run the container:

```bash
docker build -f ./Dockerfile.java -t test:java .
docker run --rm -i test:java
```

Scan the application:

```bash
docker scout quickview test:java
```

Rebuild the application without a multi-stage build and without the distroless base image:

```bash
docker build -f ./Dockerfile.java2 -t test:java2 .
docker run --rm -i test:java2
```

Scan the new application:

```bash
docker scout quickview test:java2
```

You’ll notice more CVEs in the second build. While these examples are simple, creating distroless containers for real software can be more complex.

### Go

A simple Go application is prepared in the `go-src` directory. Build and run the container:

```bash
docker build -f ./Dockerfile.scratch -t test:scratch .
docker run --rm -i test:scratch
```

Scan the application:

```bash
docker scout quickview test:scratch
```

---

## Scanning Tools

### Hadolint

[Hadolint](https://github.com/hadolint/hadolint) is a Dockerfile best practice scanner. It provides tips for improving Dockerfiles, including security recommendations. Run the following command:

```bash
docker run --rm -i hadolint/hadolint < Dockerfile.hadolint
```

Review the output and fix the issues as needed.

### Trivy

[Trivy](https://trivy.dev/latest/docs/) is a versatile tool for finding vulnerabilities, misconfigurations, secrets, SBOMs, and more. In this exercise, we’ll focus on container vulnerabilities.

Install Trivy by following the [documentation](https://trivy.dev/v0.18.3/installation/). Compare Trivy results with Docker Scout:

```bash
trivy image ubuntu:24.04
docker scout cves ubuntu:24.04
```

You’ll notice differences in the number of CVEs due to variations in CVE databases and detection scopes. Evaluate which tool best suits your needs.

#### Fixing Vulnerabilities

Build an image with known vulnerabilities:

```bash
docker build -f ./Dockerfile.cve -t test:cve .
trivy image test:cve --output=json
```

Find fixable CVEs using the JSON output and the `jq` tool:

```bash
trivy image --ignore-unfixed --format json test:cve
trivy image --ignore-unfixed --format json test:cve | jq '.Results[].Vulnerabilities[] | select(.PkgID == "tar@1.34+dfsg-1build3")'
```

Fix the `Dockerfile.cve` to eliminate the CVEs and validate the changes.

### Copacetic

[Copacetic](https://github.com/project-copacetic/copacetic) is a CLI tool for patching container images without full rebuilds. It integrates with vulnerability scanners like Trivy.

#### Example Workflow

1. Scan an Nginx image for CVEs:

   ```bash
   trivy image --pkg-types os --ignore-unfixed -f json --output nginx-report.json docker.io/library/nginx:1.21.6
   ```

2. Install Copacetic by following the [installation guide](https://project-copacetic.github.io/copacetic/website/installation).

3. Patch the image:

   ```bash
   copa patch -r nginx-report.json -i docker.io/library/nginx:1.21.6
   ```

   Copacetic creates a new container called `docker.io/library/nginx:1.21.6-patched`.

4. Scan the patched image:

   ```bash
   trivy image --pkg-types os --ignore-unfixed -f json --output nginx-report-patched.json docker.io/library/nginx:1.21.6-patched
   ```

5. Compare `nginx-report.json` and `nginx-report-patched.json`.

**Note:** Automatic patching can break applications. Always test after patching.

---

## Conclusion

Thank you for completing this exercise! If you have suggestions for improvement, feel free to create a pull request.
