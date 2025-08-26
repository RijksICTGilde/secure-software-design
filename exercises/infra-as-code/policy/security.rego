package main

import rego.v1

# Disallow containers running as root, configured globally by settings runAsUser 0
deny contains msg if {
	input.kind in {"Deployment", "StatefulSet", "DaemonSet", "Job", "Pod"}
	input.spec.template.spec.securityContext.runAsUser == 0
	msg := "Pod-level runAsUser is set to 0 (root user)"
}






