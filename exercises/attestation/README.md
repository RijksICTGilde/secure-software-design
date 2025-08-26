
# attestations

Build attestations describe how an image was built, and what it contains. The attestations are created at build-time and become attached to the final image as metadata. If you use services like github with github action this is done  by default. 

The purpose of attestations is to make it possible to inspect an image and see where it comes from, who created it and how, and what it contains. This enables you to make informed decisions about how an image impacts the supply chain security. It also enables the use of policy engines for validating images based on policy rules you've defined.

Two types of build annotations are available for containers:

* Software Bill of Material (SBOM): list of software artifacts that an image contains, or that were used to build the image.
* Provenance: how an image was built.

there are several tools to manage attestations. [sigstore](https://docs.sigstore.dev/),[in-toto](https://in-toto.io) and [slsa](https://slsa.dev/)

## Prerequisite

A container engine like docker or podman. Python3.

## container attestations

go into the current directory and execute.

```bash
docker buildx build --provenance=true --sbom=true --tag test:attestation --output type=local,dest=out .
```

BuildKit produces attestations in the [in-toto](https://in-toto.io/) format, a standard supported by the Linux Foundation. Look at the out folder. You should see a provenance.json and a sbom.spdx.json. have a look and see if you understand what the two files explain.

Locally attestations are hard because the local docker engine does not support storing the information. So you need to build and push in one command.  lets check a github action created container that does attestation.

```bash
docker buildx imagetools inspect ghcr.io/minbzk/bureaublad-api:pr-28
```

This container is multi platform container. It references to two platforms arm and amd. but it also contains two unknown platforms. these are the attestations. lets inspect them

```bash
docker buildx imagetools inspect ghcr.io/minbzk/bureaublad-api:pr-28@sha256:98ec787df3de3a02b9154c32147f8c917a7c2d0034e57de118ae0171f83c85bb --raw
docker buildx imagetools inspect ghcr.io/minbzk/bureaublad-api:pr-28@sha256:06651e443c194c5902ca7ff39ff68c7cd48cfe173f8a6357911892a701076897 --raw
```

as you can see is that both are in intoto format. It seems these containers does not contain an SBOM. To get the contect of these attestation we need another tool called [oras](https://oras.land/docs/installation). install it


lets download one manifest
```bash
oras copy ghcr.io/minbzk/bureaublad-api:pr-28@sha256:98ec787df3de3a02b9154c32147f8c917a7c2d0034e57de118ae0171f83c85bb --to-oci-layout output
```

look in the output/blobs folder for the attestation file. 

A closer analysis of the file demonstrates that the generated attestations are not cryptographically signed! That means that anyone who possesses (or stole) access tokens to push images can create a tampered attestations.

## software attestations

lets try the official [in-toto demo](https://github.com/in-toto/demo) to create cryptographically signed piece of software in a supply chain.
