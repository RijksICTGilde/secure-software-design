# Secrets Management

Managing secrets, such as database passwords, is a critical aspect of secure software development. Developers often use methods like configuration files, environment variables, or secret files to handle these secrets. In this exercise, we will explore ways to securely pass database credentials to applications and share them among developers through a Git repository.

---

## Encryption

One method to securely manage secrets is by encrypting them in a file. This allows you to safely check secrets into a Git repository. Deployment tools and other developers can decrypt the file to access the secrets.

### Using SOPS and Age

We will use [SOPS](https://github.com/getsops/sops) and Age for encryption. These are encryption tools developed for OPS people to securely send secrets to applications. There are many other options to achieve the same result.

#### Installing SOPS

For ARM architecture, adjust the download URL accordingly.

```bash
# Download the binary
curl -LO https://github.com/getsops/sops/releases/download/v3.10.2/sops-v3.10.2.linux.amd64
mv sops-v3.10.2.linux.amd64 /usr/local/bin/sops
chmod +x /usr/local/bin/sops
```

SOPS supports multiple encryption methods. We will use Age for simplicity.

#### Installing Age

Install [Age](https://github.com/FiloSottile/age/releases) and generate an encryption key:

```bash
age-keygen -o age-key.txt
```

Open `age-key.txt` to find your public key. Create a file to share secrets with other developers, such as Berry:

```bash
echo '<publickey>,age17w3z32w22uvja2t6tsjq8fc6klch5x3neq0hgdqfn0mutl6ah3aqxhwrej' > public-age-keys.txt
```

Replace \<publickey\> with youyr public key from age-key.txt

#### Encrypting and Decrypting Files

Encrypt a file using the public keys:

```bash
export SOPS_AGE_RECIPIENTS=$(<public-age-keys.txt)
sops --encrypt --age ${SOPS_AGE_RECIPIENTS} test.yaml > test.yaml.enc
```

Decrypt the file with your key:

```bash
export SOPS_AGE_KEY_FILE=$(pwd)/age-key.txt
sops --decrypt --input-type yaml --output-type yaml test.yaml.enc
```

You can also decrypt the file using Berry's key:

```bash
export SOPS_AGE_KEY_FILE=$(pwd)/berry-age-key.txt
sops --decrypt --input-type yaml --output-type yaml test.yaml.enc
```

Anyone listed in `public-age-keys.txt` can decrypt the file, including deployment systems or other developers. [Sealed-secrets](https://github.com/bitnami-labs/sealed-secrets) is often use to automate this in kubernetes.

#### Automating Encryption with Git

To automatically encrypt and decrypt files in Git, configure the following in a clean git repo. To create a clean git repo execute the following

```bash
mkdir /tmp/test
cd /tmp/test
mkdir ./scripts
git init
```

Now we can configure this git repo

1. Set up Git filters:

   ```bash
   git config --local filter.sops.smudge $(pwd)/scripts/decrypt.sh
   git config --local filter.sops.clean $(pwd)/scripts/encrypt.sh
   git config --local filter.sops.required true
   ```

2. Add a `.gitattributes` file:

   ```plaintext
   test.yaml filter=sops
   ```

3. Create encryption and decryption scripts:

   ```bash
   echo -n '#!/bin/bash

   scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
   cd "${scriptDir}/.." || exit 1

   export SOPS_AGE_RECIPIENTS=$(<public-age-keys.txt)
   exec 3<<< "$(cat $1)"
   sops --encrypt --input-type yaml --output-type yaml --age ${SOPS_AGE_RECIPIENTS} --encrypted-regex "^(username|password)$" /dev/fd/3
   ' >> scripts/encrypt.sh
   chmod u+x scripts/encrypt.sh

   echo -n '#!/bin/bash

   scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
   cd "${scriptDir}/.." || exit 1

   export SOPS_AGE_KEY_FILE=$(pwd)/age-key.txt
   exec 3<<< "$(cat $1)"
   sops --decrypt --input-type yaml --output-type yaml /dev/fd/3
   ' >> scripts/decrypt.sh
   chmod u+x scripts/decrypt.sh
   ```

you have now setup automatic encryption and description. Try it out but creating a test file test.yaml

Anyone with their public key in `public-age-keys.txt` can decrypt the file. However, files must be re-encrypted if a new public key is added.

---

## Secret Manager

[HashiCorp Vault](https://www.hashicorp.com/en/products/vault) is a powerful secret manager. An open-source alternative is [OpenBao](https://openbao.org/). In this exercise, we will use Vault.

### Setting Up Vault

1. Start Vault:

   ```bash
   docker compose up
   ```

2. Open [http://localhost:8200](http://localhost:8200) in a web browser.
3. Define key shares and thresholds (set both to 1 for this test case, though not recommended for production).
4. Initialize Vault and copy the `initial root token` and `key1`.
5. Unseal Vault using `key1` and log in with the `initial root token`.

### AppRole Authentication

AppRole allows applications to authenticate using:

- **Role ID:** Similar to a username (safe to share or embed in source code).
- **Secret ID:** A one-time password (should be kept secret and can be short-lived).

AppRole provides stronger security, better lifecycle management, and is purpose-built for applications if you compare it to a username/password method. You often add the RoleID to your code, and generate a Secret ID in your CD pipeline.

Refer to the [AppRole documentation](https://developer.hashicorp.com/vault/docs/auth/approle) for details and examples on how to use it.

#### Adding Authentication Methods

1. Click `Access` > `Enable a new method` > `Username & Password` > `Enable method`.
2. Create a new user under `View method` > `Create user`.
3. Assign policies to the user to define permissions.

#### Policies

Policies define what tokens can do. By default, Vault includes `default` and `root` policies. Create an `admin` policy:

```hcl
path "*" {
    capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}
```

Attach the policy to a user:

1. Go to `Access` > `Userpass` > `username` > `Edit user`.
2. Expand the `Tokens` panel and add `admin` to `Generated Token's Policies`.

Log in with the new user to verify permissions.

---

## Key-Value Secret Engine

Vault supports various secret engines. Enable the Key-value(KV) secret engine by following the [Vault tutorial](https://developer.hashicorp.com/vault/docs/get-started/operations-qs#enable-the-key-value-secret-plugin).

Install the [Vault CLI tool](https://developer.hashicorp.com/vault/install) and configure it:

```bash
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='your usertoken or root token'
```

Execute the following command to create a user:

```bash
vault write auth/userpass/users/opsuser \
    password=p@ssw0rd
```

Explore the secrets in the GUI using your root or admin token.

## Database Secret Engine

In this part we will explore the database password rotation and secret generation. [Learn more](https://developer.hashicorp.com/vault/docs/secrets/databases/postgresql).

lets first connect to our database so we can see what happens when enabling vault

1. goto <http://localhost:5050> in your preferred browser
2. username=`rig@admin.com`
3. password=`admin`

Once logged in you can select a database and connect.

1. select  `Servers` > `Postgres Vault - admin`
2. password=admin

When logged in goto `Login/Groups Roles` and check which users exist. You will see 3 users. all of them are admin on all database. This is just for testing. In real life you would not make them all admin on all databases.

lets setup Vault to manage access to the database. The secret engine generates database credentials dynamically based on configured roles for the PostgreSQL database.

Login into the GUI and enable a database engine:

1. Click `Secret Engines` > `Enable a engine` > `databases` > `enable engine`

Lets configure the database engine
2. Create database connaction `Secret Engines`> `database/`> `Connections` > `Create connection`
3. Database plugin=Postgresql
4. Connection name=testdb
5. connection URL=postgresql://{{username}}:{{password}}@postgres:5432/test?sslmode=prefer
6. Username=test
7. Password=test
8. Select `create database`
9. Select `enable and rotate`

The credentials will be rotated, so now only vaults knows the credentials.

unfortunately the gui setup does not setup the database engine correctly.  We need the CLI or API explorer to fix this. Lets use the API explorer

1. Click `tools` > `API Explorer`
2. Find the `Post /database/config/{name}`
3. add the following payload

```json
{
    "allowed_roles": [],
    "connection_details": {
      "backend": "database",
      "password_authentication": "scram-sha-256",
      "connection_url": "postgresql://{{username}}:{{password}}@postgres:5432/test?sslmode=prefer",
      "max_connection_lifetime": "0s",
      "max_idle_connections": 0,
      "max_open_connections": 4,
      "username": "test"
    },
    "password_policy": "",
    "plugin_name": "postgresql-database-plugin",
    "plugin_version": "",
    "root_credentials_rotate_statements": []
}
```

We will now need to setup a role

1. Click `Secret Engines` > `database/` > `Create new (in Roles)`
2. Role name=my-role
3. connection name=testdb
4. type of role=dynamic (static is for already existing users)
5. creation_statements=`CREATE ROLE "{{name}}" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';         GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{{name}}";`
6. select `Create role`

The role to create database credentials is now created. Lets create some credentials and try it out.

1. click `Secret Engines` > `database/` > `Roles` > `my-role` > `Generate Credentials`

Lets check if the credentials are created

lets first connect to our database so we can see what happens when enabling vault

1. goto <http://localhost:5050> in your preferred browser
2. username=`rig@admin.com`
3. password=`admin`

Once logged in you can select a database and connect.

1. select  `Servers` > `Postgres Vault - admin`
2. password=admin

When logged in goto `Login/Groups Roles` and check which users exist, do you see new ones?

## Additional Vault Feature

Vault had many other usefull features. The list a few i used in the past.

- **SSH Secret Engine:** [Learn more](https://developer.hashicorp.com/vault/docs/secrets/ssh).
- **TOTP (Time-Based One-Time Password):** [Learn more](https://developer.hashicorp.com/vault/docs/secrets/totp).

The SSH Secret Engine allows you to sign SSH-keys that you use to connect to a server. The server will be configured to check if the key is signed. Since the signing can have a short expiration (for example 8 hours) you can better control access to the server.

The TOTP secret engine allows you to store TOTP root token. They need to be store when generating the basic TOTP (when you scan it with your Phone). This will allow you to enable TOTP for services, but still manage access for multiple people who do not have access to the device.

## secret scanning

It might be usefull to add secrets scanning to your repo so you do not accidently check in secrets. There are many tools that help you do this. In this example we will use gitleaks

```bash
docker run -v ${PWD}/secrets-repo/:/secrets-repo/ zricethezav/gitleaks:v8.28.0 dir /secrets-repo/ --report-path /secrets-repo/gitleaks-report.json 
```

you can create [custom rules](https://github.com/gitleaks/gitleaks?tab=readme-ov-file#configuration) and also enabled gitleaks in a [pre-commit](https://github.com/gitleaks/gitleaks?tab=readme-ov-file#pre-commit) hook or in your CI/CD.


Thank you for completing this exercise! If you have suggestions for improvement, feel free to create a pull request.

