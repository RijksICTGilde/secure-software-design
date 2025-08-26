# CIS Benchmarks

[CIS benchmarks](https://www.cisecurity.org/benchmark) are an excellent resource for secure configuration best practices. Developed collaboratively by the community, they provide guidance on hardening specific systems and are available for free for non-commercial use. CIS offers benchmarks for a wide range of technologies, detailing recommended security settings. Examples include PostgreSQL, Kubernetes, Linux operating systems, NGINX, AWS, and many more.

In this exercise we will spin up a Kubernetes cluster with KIND(Kubernetes in Docker) and scan it using the CIS benchmarks.

## Prerequisite

A container engine like docker or podman.

## Kubernetes scanning

We will first setup a kubernetes cluster locally using KIND.

Install KIND by following [this manual](https://kind.sigs.k8s.io/docs/user/quick-start/#installing-from-release-binaries)

Once installed make sure you go into this directory and execute

```
kind create cluster --config config.yaml
```

This should spin up a Kubernetes v1.32.5 cluster locally as docker containers. One master node and 2 worker nodes.

## kube bench

There are tools that automate checking for CIS benchmarks. [kube-bench](https://github.com/aquasecurity/kube-bench) does this for Kubernetes. We will install kube-bench on the master node container and scan it for hardening recommendations.

**Optional**: you can download the [CIS benchmarks](https://www.cisecurity.org/benchmark/kubernetes) documentation. You need to supply an email adres.

first we will install kube-bench in the kind-contol-plane container. make sure to replace amd64 with arm64 if you use an arm machine like the newer mac models. (most systems are amd64)

```
docker exec kind-control-plane curl -L https://github.com/aquasecurity/kube-bench/releases/download/v0.6.2/kube-bench_0.6.2_linux_amd64.tar.gz -o kube-bench_0.6.2_linux_amd64.tar.gz

docker exec kind-control-plane curl -L https://github.com/aquasecurity/kube-bench/releases/download/v0.6.2/kube-bench_0.6.2_linux_arm64.tar.gz -o kube-bench_0.6.2_linux_arm64.tar.gz

docker exec kind-control-plane tar -xvf kube-bench_0.6.2_linux_arm64.tar.gz (or use the arm one if you need it)
```

When your succesfully execute the above steps we have kube-bench installed.

We can now scan the master node with kube-bench and find the recommended hardening steps.

```bash
docker exec -it kind-control-plane bash

./kube-bench --config-dir `pwd`/cfg --config `pwd`/cfg/config.yaml
```

You now have a list of failed and passed test. Here a small sample of the output

```
[FAIL] 1.2.22 Ensure that the --audit-log-path argument is set (Automated)
[FAIL] 1.2.23 Ensure that the --audit-log-maxage argument is set to 30 or as appropriate (Automated)
[FAIL] 1.2.24 Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate (Automated)
[FAIL] 1.2.25 Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate (Automated)
```

We will start fixing the above failed tests. Luckily CIS benchmarks also specify how to fix the issues and sometimes even gives the full cli command to fix it.

lets find the details of test 1.2.22

```
1.2.22 Edit the API server pod specification file /etc/kubernetes/manifests/kube-apiserver.yaml
on the master node and set the --audit-log-path parameter to a suitable path and
file where you would like audit logs to be written, for example:
--audit-log-path=/var/log/apiserver/audit.log
```

lets fix it

```
sed -i  "/- --authorization-mode=Node,RBAC/a\    - --audit-log-path=/var/log/apiserver/audit.log" /etc/kubernetes/manifests/kube-apiserver.yaml
```

now scan again an see if the issue is solved.

This change will only take place after a restart. but that is out of scope for the current exercise.

Feel free to try and fix some more issues from kube-bench

## End

Thank you for trying this exercise, if you have improvements feel free to create a PR.
