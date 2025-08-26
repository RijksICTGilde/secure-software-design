# Hardening

In this exercise we will focus on hardening systems using CIS Benchmarks and monitoring systems using falco.

## CIS

[CIS Benchmarks](https://www.cisecurity.org/benchmark) are an excellent resource for secure configuration best practices. Developed collaboratively by the community, they provide guidance on hardening specific systems. These benchmarks are free for non-commercial use and cover a wide range of technologies, including PostgreSQL, Kubernetes, Linux, NGINX, AWS, Azure and more.

CIS Benchmarks typically include:

- **Recommendations:** Suggested configurations for improved security.
- **Rationale:** The reasoning behind each recommendation.
- **Audit Commands:** Commands to verify compliance.

We added two pdf files in this directory. One for ubuntu 24 and one for kubernetes. Have a look at CIS_Kubernetes_Benchmark_V1.12_PDF.pdf. If you open page 19 you will see and example of a recommendation 1.1.1.

Visit the [CIS Benchmarks](https://www.cisecurity.org/benchmark) website and download a benchmark of your choice. For example, you can explore the [Ubuntu Linux benchmark](https://www.cisecurity.org/benchmark/ubuntu_linux).

## Kubernetes Scanning

In this exercise, we will spin up a Kubernetes cluster using KIND (Kubernetes in Docker) and scan it using CIS Benchmarks with automated tools.

### Setting Up a Kubernetes Cluster

We will set up a local Kubernetes cluster using KIND. Follow these steps:

1. Install KIND by following [this guide](https://kind.sigs.k8s.io/docs/user/quick-start/#installing-from-release-binaries).
2. Navigate to this directory and execute:

   ```bash
   kind create cluster --config config.yaml
   ```

   This command creates a Kubernetes v1.32.5 cluster locally as Docker containers

---

## Scanning with kube-bench

[kube-bench](https://github.com/aquasecurity/kube-bench) automatically checks CIS Benchmark for Kubernetes. We will install kube-bench on the master node container and scan it for hardening recommendations.

### Installing kube-bench

Install kube-bench in the `kind-control-plane` container. Replace `amd64` with `arm64` if you are using an ARM-based machine (e.g., newer Mac models):

```bash
docker exec kind-control-plane curl -L https://github.com/aquasecurity/kube-bench/releases/download/v0.6.2/kube-bench_0.6.2_linux_amd64.tar.gz -o kube-bench_0.6.2_linux_amd64.tar.gz

docker exec kind-control-plane curl -L https://github.com/aquasecurity/kube-bench/releases/download/v0.6.2/kube-bench_0.6.2_linux_arm64.tar.gz -o kube-bench_0.6.2_linux_arm64.tar.gz

docker exec kind-control-plane tar -xvf kube-bench_0.6.2_linux_amd64.tar.gz
```

Once installed, kube-bench is ready to scan the master node.

### Running kube-bench

Run the following commands to scan the master node:

```bash
docker exec -it kind-control-plane bash

./kube-bench --config-dir `pwd`/cfg --config `pwd`/cfg/config.yaml
```

This will generate a list of passed and failed tests. Below is a sample output:

```plaintext
[FAIL] 1.2.22 Ensure that the --audit-log-path argument is set (Automated)
[FAIL] 1.2.23 Ensure that the --audit-log-maxage argument is set to 30 or as appropriate (Automated)
[FAIL] 1.2.24 Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate (Automated)
[FAIL] 1.2.25 Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate (Automated)
```

### Fixing Issues

Let’s address test `1.2.22` as an example. The CIS Benchmark specifies the following fix:

```plaintext
1.2.22 Edit the API server pod specification file `/etc/kubernetes/manifests/kube-apiserver.yaml`
on the master node and set the `--audit-log-path` parameter to a suitable path and
file where you would like audit logs to be written, for example:
--audit-log-path=/var/log/apiserver/audit.log
```

Apply the fix using the `sed` command:

```bash
sed -i "/- --authorization-mode=Node,RBAC/a\    - --audit-log-path=/var/log/apiserver/audit.log" /etc/kubernetes/manifests/kube-apiserver.yaml
```

Re-scan to verify the issue is resolved. Note that changes take effect after a restart, which is outside the scope of this exercise.

Feel free to fix additional issues identified by kube-bench.

---

## Falco

[Falco](https://falco.org/) is a useful tool to get notified when suspicious things happen in your system. By default it has rules, but you can also add your own rules. To learn more about the rules see the [documentation](https://falco.org/docs/concepts/rules/). Some of the default rules are explained [here](https://falco.org/docs/#what-does-falco-check-for)

A Vm should be available to test falco. connect to it using the credentials provided. falco is already running. You can see the configuration here:

```bash
cat /etc/falco/falco.yaml
```

by default falco logs entries to stdout and syslog but you can also export the data to other sources like files, http endpoints. We configured falco to expose information in a file

```bash
sudo cat /var/log/falco.txt
```

Falco ships with some default rules that we will trigger to get entries in /var/log/falco.txt. to find existing rules you can check

```bash
cat /etc/falco/falco_rules.yaml
```

An example rule looks like:

```yaml
- rule: Search Private Keys or Passwords
  desc: >
    Detect attempts to search for private keys or passwords using the grep or find command. This is often seen with
    unsophisticated attackers, as there are many ways to access files using bash built-ins that could go unnoticed.
    Regardless, this serves as a solid baseline detection that can be tailored to cover these gaps while maintaining
    an acceptable noise level.
  condition: >
    spawned_process
    and ((grep_commands and private_key_or_password) or
         (proc.name = "find" and (proc.args contains "id_rsa" or
                                  proc.args contains "id_dsa" or
                                  proc.args contains "id_ed25519" or
                                  proc.args contains "id_ecdsa"
          )
        ))
  output: Grep private keys or passwords activities found | evt_type=%evt.type user=%user.name user_uid=%user.uid user_loginuid=%user.loginuid process=%proc.name proc_exepath=%proc.exepath parent=%proc.pname command=%proc.cmdline terminal=%proc.tty exe_flags=%evt.arg.flags
  priority:
    WARNING
  tags: [maturity_stable, host, container, process, filesystem, mitre_credential_access, T1552.001]
```


lets trigger this rule

```bash
sudo find . -iname id_rsa
```

Now check the new entries in /var/log/falco.txt

You can create any rule you like. if you want to create a new rule you can add them in cat /etc/falco/falco_rules.local.yaml. For more information about creating new rules see <https://falco.org/docs/concepts/rules/basic-elements/>

If you want to restart falco you can reload it

```bash
sudo systemctl restart falco
```

---

## Conclusion

Thank you for completing this exercise! If you have suggestions for improvement, feel free to create a pull request.
