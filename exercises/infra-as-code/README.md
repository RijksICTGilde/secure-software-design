# Infrastructure as Code (IaC)

This exercise guides you through scanning infrastructure code for vulnerabilities using various tools. The choice of scanning tool depends on the IaC technology you use. Most IaC system have a scanning tool available.

---

## Prerequisites

- Docker or Podman
- One of: TypeScript, Python, C#, Go, or Java

---

## Kubernetes IaC Scanning

Navigate to the `examples/kubernetes` folder, where you'll find a `Kubernetes.yaml` manifest. Try scanning the folder with any of the following tools:

### Checkov

[Checkov](https://github.com/bridgecrewio/checkov) is a static code analysis tool for infrastructure as code (IaC) and also a software composition analysis (SCA) tool for images and open source packages.

```bash
docker run -v $PWD/examples/kubernetes/:/scan/ bridgecrew/checkov:3 -d /scan/
```

- Review the output, fix one issue, and rescan.

### Trivy

[Trivy](https://github.com/aquasecurity/trivy) is a comprehensive and versatile security scanner. Trivy has scanners that look for security issues, and targets where it can find those issues

```bash
docker run -v $PWD/examples/kubernetes/:/scan/ aquasec/trivy:0.66.0 config /scan/
```

- Review the output, fix one issue, and rescan.

### Terrascan

[Terrascan](https://github.com/tenable/terrascan) is a static code analyzer for Infrastructure as Code. Try it out.

```bash
docker run -v $PWD/examples/kubernetes/:/scan/ tenable/terrascan:1.19.9 scan -i k8s -d /scan/
```

- Review the output, fix one issue, and rescan.

### Conftest (OPA)

With conftest you can create custom policies. The other tools work the same, but have predefined policies to make it more user friendly. However, the strength of conftest is in its flexibility to support your own logic that your organisation finds important.

```bash
docker run -v $PWD/examples/kubernetes/policy/:/project/policy/ -v $PWD/examples/kubernetes/:/project/scan/ openpolicyagent/conftest:v0.62.0 test /project/scan/
```

- Review the output, fix one issue, and rescan.

---

## Terraform IaC Scanning

Navigate to the `examples/terraform` folder to scan Terraform code using these tools:

### Checkov

```bash
docker run -v $PWD/examples/terraform/:/scan/ bridgecrew/checkov:3 -d /scan/
```

- Review the output, fix one issue, and rescan.

### Trivy

```bash
docker run -v $PWD/examples/terraform/:/scan/ aquasec/trivy:0.66.0 config /scan/
```

- Review the output, fix one issue, and rescan.

### Terrascan

```bash
docker run -v $PWD/examples/terraform/:/scan/ tenable/terrascan:1.19.9 scan -i terraform -d /scan/
```

- Review the output, fix one issue, and rescan.

---

## CDK8s

You can create infrastructure as code using tools like Terraform, Helm, AWS CDK, and CDK8s. While Terraform and Helm are popular for deployments, CDKs (Cloud Development Kits) are much more developer-friendly. It allows for more abstraction and allows the developer to use a language he already knows. CDK8s is a specific CDK for kubernetes.

### Getting Started with CDK8s

1. Install the [CDK8s CLI](https://cdk8s.io/docs/latest/cli/installation/).
2. Initialize a new project:

   ```bash
   cdk8s init <type>
   ```

   - Replace `<type>` with one of: `go-app`, `java-app`, `python-app`, `typescript-app`.

3. This generates an example application in your chosen language. Add content by copying relevant parts from the [documentation examples](https://cdk8s.io/docs/latest/examples/#__tabbed_1_1).
4. Generate manifests:

   ```bash
   cdk8s synth
   ```

   - Manifests are created in the `./dist` folder.

You can now scan the manifest with on of the tools trivy, terrascan or checkov
---

## AWS CDK

Many cloud providers have CDKs available to automate the process of creating infrastucture, This is true for AWS, Google Cloud, Azure, Alibaba but also for smaller alternatives like openstack. in this example we will explore AWS CDK. To see what we will create have a look inside

examples/aws/lib/aws-stack.ts. What kind of resources will we create?

Lets generate the Infra code.

goto the examples/aws folder and make sure you have [node](https://nodejs.org/en/download) installed. then execute the following

```bash
npm install
npm run cdk synth
```

This will create a cdk.out directory with the infra code. As you will see if you look inside the cdk.out/ folder AWS has its own way of describing infrastucture. For AWS its called CloudFormation. Other clouds have different documents structures, but in the end its all the same.

You can run the above tools to see the recommendations. Feel free to solve one or two.

## Notes

- Always review scan results, fix at least one issue, and rescan to verify improvements.
- Try different tools to compare findings and coverage.
- For custom policies, use OPA and Conftest with your own Rego rules.

---

If you have suggestions or improvements, feel free to create a pull request.


