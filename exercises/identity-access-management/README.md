# Identity & Access Management

Identity & Access Management (IAM) is crucial for security. It defines who can access what resources within an application.

## Authentication

Many applications implement their own user management, which is often error-prone and time-consuming. Most organizations support Single Sign-On (SSO) using SAML or OpenID Connect. OpenID Connect is a widely adopted standard for authentication, supported by tools such as Keycloak, Dex, Authentik, Zitadel, Authelia, and SaaS solutions like Okta and Microsoft Entra.

In this example, we use **Keycloak**. The features discussed are available in other tools as well.

### Getting Started

Start the example environment:

```bash
docker compose build
docker compose up
```

Once started (may take ~20 seconds), access the following URLs:

| Service         | URL                        |
|-----------------|---------------------------|
| Keycloak        | [http://localhost:8080](http://localhost:8080) |
| Custom Backend  | [http://localhost:8000](http://localhost:8000) |
| Custom Frontend | [http://localhost:3000](http://localhost:3000) |

Keycloak is preconfigured. Below are the credentials for this tutorial (feel free to explore other features):

- **Admin User**
  - Username: `admin@rig.nl`
  - Password: `admin`
- **Test User RIG**
  - Username: `test@rig.nl`
  - Password: `test`
- **Test User I-interrim rijk**
  - Username: `test@iir.nl`
  - Password: `test`

---

### Consent Management

Tracking user consent is often required for compliance. Keycloak supports this by default.

**Steps:**

1. Log in to Keycloak as the admin user.
2. Navigate to `Clients` > `Secret frontend`.
3. Scroll to `Login settings` and enable `Consent required`.
4. Save changes.

**Test:**

- Log in to the frontend as `test@rig.nl`.
- Log in to Keycloak as admin, then go to `Users` > `test@rig.nl` > `Consent` to view registered consents.

---

### Required Actions

You may require users to perform specific actions upon login (e.g., accept Terms and Conditions).

**Enable Terms and Conditions:**

1. Log in to Keycloak as admin.
2. Go to `Authentication` > `Required actions`.
3. Enable `Terms and Conditions` and set as default action.
4. Create a new user and observe the login process.

**For Existing Users:**

1. Log in to Keycloak as admin.
2. Go to `Users` > `test@rig.nl`.
3. Set required actions and save.
4. Log in as `test@rig.nl` to see the effect.

---

### Impersonation

Impersonation allows developers to log in as another user for debugging.

**Steps:**

1. Log in to Keycloak as `admin@rig.nl`.
2. Go to `Users` > `test@irr.nl`.
3. In the top-right actions menu, select `Impersonate`.
4. Visit the frontend and check your credentials; you appear as `test@irr.nl`.

---

### Password Policies

Set password policies to enforce security requirements.

**Steps:**

1. Log in to Keycloak as admin.
2. Go to `Authentication` > `Policies` > `Add a policy`.
3. Set a minimal length to a high number.
4. Create a new user to test the policy.

**Note:** To apply the policy to existing users, set a new `Required action`.

---

### Multi-Factor Authentication (MFA)

MFA enhances security. There are several possibilities for MFA Like OTP and passkeys. Enabling MFA requires modifying authentication flows.

**Restart Environment (if needed):**

```bash
docker compose down -v
docker compose up
```

**Enable MFA:**

1. Log in to Keycloak as admin.
2. Go to `Authentication` > `Flows` > `Browser`.
3. Click `Action` > `Duplicate` (top right).
4. Name the new flow `Browser MFA`.
5. In steps, set `Conditional 2fa` from `Conditional` to `Required`.

**Set Up MFA for Admin:**

1. Log in to Keycloak as admin.
2. Go to clients and click the URL after `account-console`.
3. Navigate to `Account beveiliging` > `Aanmelden` > `Stel authenticator applicatie in`.
4. Use your OTP tool to set up MFA.

**Activate the Flow:**

1. Go to `Authentication` > `Flows` > `Browser MFA`.
2. Click `Action` > `Bind flow`, select `browser flow`, and save.

**Test:**

- Log out and log in as admin to test MFA.
- To revert, rebind the original `Browser` flow.

**Tip:** Explore additional flow options by clicking `Add Execution` in the Flow page.

---

### Federation

Federation allows your IAM system to connect with external identity providers, enabling seamless login for users from other organizations or systems. This is especially useful for testing or integrating with providers outside your own environment.

- Users from external identity providers can log in without creating new accounts.
- You can set a default identity provider or customize login flows as needed.

**Note:** Some organizations may restrict federation for security reasons.

To enable federation, you must be authorized by the external Identity Provider.

To set up federation with another provider:

1. In Keycloak, go to `Identity provider` > `OpenID Connect v1.0`.
2. Set an alias (e.g., `ssorijk`).
3. Share your `Redirect URI` with the external Identity Provider.

The external provider will create a client and send you the Client ID, Client Secret, and Discovery Endpoint.

Example credentials:

```bash
Client ID: security-test-tutorial
Client Secret: WHtibBoReXcg5sUPkbeo6jsGaxrdavvB
Discovery Endpoint: https://id.icbr.prd1.gn2.quattro.rijksapps.nl/realms/test/.well-known/openid-configuration
```

This will create the identity provider configuration. Now, sign in to the frontend application and select `ssorijk` as the login option.

Log in using credentials from the external identity provider:

- **IDP User**
  - Username: `test@otherdomain.nl`
  - Password: `test`

### Role-Based Access Control (RBAC)

OpenID Connect supports RBAC and ABAC. RBAC uses roles for authorization, either globally or per application. The roles are stored in the JWT token.

**JWT Token Structure:**

- `resource_access`: Roles per application/client
- `realm_access`: Roles across multiple applications
- `Organization`: Used for multi-tenant setups

Login into the frontend application and check your roles.

**Important:** Tokens displayed in the frontend are not secure for authorization. Always validate tokens in the backend.

#### Creating Roles

**Realm Role:**

1. Log in to Keycloak as admin.
2. Go to `Realm roles` > `Create Role`.
3. Name it `testrole` and save.
4. Assign `testrole` to `test@iir.nl` via `Users` > `Role mapping`.

**Client Roles:**

1. Log in to Keycloak as admin.
2. Go to `Clients` > `secret-frontend` > `Roles` > `Create role`.
3. Create roles: `admin`, `editor`, `viewer`.
4. Assign `admin` role to `test@iir.nl` via `Users` > `Role mapping`.

**Test:**

- Log in to the frontend as `test@iir.nl`.
- Inspect the JWT token for assigned roles.

This will move the role management to the IDP. This is not always ideal because sometimes you want to manage this inside the application. Some application build in the authorization system based on roles. An example of this is Grafana. Follow [the link](https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-authentication/generic-oauth/#configure-role-mapping) how they setup access using the role_attribute_path

**Note:** Role management can be integrated into your application using Keycloak API or SDK. This however requires your application to have elevated permissions in keycloak.

---

## Attribute-Based Access Control (ABAC)

Attribute-Based Access Control (ABAC) enables more fine-grained access control in Keycloak compared to Role-Based Access Control (RBAC). With ABAC, you can define permissions at the resource level, such as granting access to individual documents. To use ABAC, your application must integrate with Keycloak's API using the `uma-ticket` protocol, which is part of UMA 2.0—not OpenID Connect. This allows you to evaluate complex policies and manage access dynamically based on user attributes and resource properties.

**Enable ABAC:**

1. Log in to Keycloak as admin.
2. Go to `Clients` > `secret-backend`.
3. Enable `Authorization` under `Capability config`.

**Explore:**

- A new `authorization` tab appears for `secret-backend`.
- Import example authorization from `./keycloak/policy.json`.
- Evaluate and create policies. Feel free to create your own.

Try to create some policies and evaluate them. See if you can create an interesting scenario.

**Application Integration:**

- Use Keycloak's API from applications (Java: `keycloak-authz-client`, Python: HTTPS request).

**Java Example:**

```java
AuthzClient authzClient = AuthzClient.create();
AccessTokenResponse response = authzClient.authorization(userAccessToken)
    .authorize("document#view");

if (response.getToken() != null) {
    // access granted
} else {
    // access denied
}
```

**Python Example:**

```python
token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
data = {
    "grant_type": "urn:ietf:params:oauth:grant-type:uma-ticket",
    "audience": CLIENT_ID,
    "permission": f"{resource}#{scope}"
}
response = requests.post(token_url, data=data)
```

## Custom Attributes

You can add custom attributes to users for additional information across applications.

- Example: The frontend displays a `Pet` attribute.
- Add attributes as needed in Keycloak.

If you want to create your own attributes:

1. Click `Realm Settings` > `User profile` > `Create attribute`
2. Set Attribute[name]
3. for 'display name', make sure to press the globe symbol to add translations for all languages
4. In attribute group select user-metadata
5. for `Enabled when` se;ect `Scoptes are requested` and select `profile`
6. then select the permissions and enable `user` for both fields

## Other Keycloak Features

Keycloak offers many more features not covered here, such as:

- **Social Login Integration:** Connect with providers like Google, Facebook, GitHub, and more.
- **User Federation:** Integrate with LDAP or Active Directory for centralized user management.
- **Session Management:** Configure session timeouts, revocation, and tracking.
- **Event Logging & Auditing:** Monitor authentication events and user activity.
- **Custom Themes:** Customize login and account management pages.
- **Email & SMS Notifications:** Send verification, password reset, and alert messages.
- **Fine-Grained Admin Permissions:** Delegate admin tasks with granular access controls.
- **Service Accounts:** Enable machine-to-machine authentication.
- **Internationalization:** Support multiple languages for user-facing screens.

For specific problems or advanced use cases, consult Keycloak documentation or an expert.

---

### end

Stop the application

```bash
docker compose down
```

---

## Authorization (ReBAC)

OpenID Connect provides authorization information through roles embedded in JWT tokens. However, this approach is strictly role-based and requires you to implement role-handling logic within your application.

A new standard, **AuthZen**, is currently under development to standardize APIs for authorization. While several tools already support global fine-grained authorization, they do not yet use standardized APIs. Examples of such tools include Cerbos, OpenFGA, and Cedar.

In the Netherlands, VNG is actively working on fine-grained authorization solutions. For more details, refer to the [VNG documentation](https://vng-realisatie.github.io/ftv/).

In this exercise, you will work with [OpenFGA](https://openfga.dev/docs/authorization-concepts) to explore fine-grained authorization concepts based on ReBAC, which stands for Relationship-Based Access Control.

ReBAC is a superset of RBAC: you can fully implement RBAC with ReBAC. ReBAC also lets you natively solve for ABAC when attributes can be expressed in the form of relationships. For example ‘a user’s manager’, ‘the parent folder’, ‘the owner of a document’, ‘the user’s department’ can be defined as relationships.

Interresting to know is that Google implements ReBAC in its google suite. See [Zanzibar](https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/) for more information if you are interrested.

**Benefits of AuthZen:**

1. Move authorization logic outside application code for easier management and auditing.
2. Increase development velocity with a standardized solution.
3. Centralize authorization decisions and audit logs for compliance.

### Basic components

AuthZen contains 4 components:

1. **Policy Administration Point**  
  Central repository for authorization policies. It defines rules and relationships that determine who can access which resources. Policies are versioned and auditable.

2. **Policy Decision Point**  
  Evaluates access requests against policies in the Policy Administration Point. It determines whether a user is allowed to perform an action on a resource, based on current context and relationships.

3. **Policy Enforcement Point**  
  Integrates with applications and services to enforce authorization decisions. It intercepts requests, queries the Policy Decision Point, and allows or denies access accordingly.

4. **Policy Information Point**  
  Records all authorization decisions and policy changes. Enables compliance, monitoring, and troubleshooting by providing a detailed history of access requests and policy evaluations.

These components work together to provide centralized, fine-grained, and auditable authorization for modern applications.

### what does the language look like for OpenFGA

To understand AuthZen a bit more lets explore the [policy language](https://openfga.dev/docs/configuration-language).

### OpenFGA Example

If you want to deepdive into OpenFGA you can read about the [Concepts](https://openfga.dev/docs/concepts). Or you can just dive into it and start OpenFGA:

lets first [install](https://github.com/openfga/cli?tab=readme-ov-file#installation) the fga CLI

Once installed we can start an openfga instance

```bash
docker run -p 8080:8080 -p 8081:8081 -p 3000:3000 openfga/openfga:v1.10.0 run
```

This will open some ports for interaction

- Port 8080: HTTP API
- Port 8081: gRPC API
- [playground](http://localhost:3000/playground)

We will now try to implement the [Google drive example](https://openfga.dev/docs/modeling/advanced/gdrive). Frist create a store

```bash
fga store create --name drive --model openfga/model.fga
```

make sure to get the authorization_model_id from the response

```bash
export FGA_MODEL_AUTH=authorization_model_id
```

The model created looks like this

```bash
type document
  relations
    define owner: [user]
    define writer: [user]
    define commenter: [user]
    define viewer: [user]
```

Configure the cli to use the store

```bash
export FGA_STORE_ID=$(fga store list  | jq -r '.stores | first | .id')

```

```bash
fga model get
fga query check --store-id=$FGA_STORE_ID --model-id=$FGA_MODEL_AUTH user:beth commenter document:2021-budget
fga tuple write --store-id=$FGA_STORE_ID --model-id=$FGA_MODEL_AUTH user:anne owner document:2021-budget
fga query check --store-id=$FGA_STORE_ID --model-id=$FGA_MODEL_AUTH user:anne owner document:2021-budget
fga query check --store-id=$FGA_STORE_ID --model-id=$FGA_MODEL_AUTH user:anne writer document:2021-budget
```

In the last check you would expect anne to have access as a write. But we did not define this in our model. Lets change the model

```yaml
model
  schema 1.1

type user

type document
  relations
    define owner: [user]
    define writer: [user] or owner
    define commenter: [user] or writer
    define viewer: [user] or commenter
```

```bash
fga model write --store-id $FGA_STORE_ID --file openfga/model1.fga
```

make sure to update the authorization model

```bash
export FGA_MODEL_AUTH=authorization_model_id
```

lets try some tests

```bash
fga model get
fga query check --store-id=$FGA_STORE_ID --model-id=$FGA_MODEL_AUTH user:beth commenter document:2021-budget
fga query check --store-id=$FGA_STORE_ID --model-id=$FGA_MODEL_AUTH user:anne writer document:2021-budget
```

This shows the basics of what fga can do. You can slowly build up your authorization model, and use an SDK to query the system from your software. In an official production setup you would manage the permissions in a repository like git.

We can bring the model even further

```bash
fga model write --store-id $FGA_STORE_ID --file openfga/model2.fga
```

make sure to update the authorization model

```bash
export FGA_MODEL_AUTH=authorization_model_id
```

now lets setup the permissions

```bash
fga tuple write --store-id=${FGA_STORE_ID} --model-id=$FGA_MODEL_AUTH user:anne member domain:xyz 
fga tuple write --store-id=${FGA_STORE_ID} --model-id=$FGA_MODEL_AUTH user:beth member domain:xyz 
fga tuple write --store-id=${FGA_STORE_ID} --model-id=$FGA_MODEL_AUTH user:charles member domain:xyz 
fga tuple write --store-id=${FGA_STORE_ID} --model-id=$FGA_MODEL_AUTH domain:xyz#member viewer document:2021-budget 
```

and check the result

```bash
fga query check --store-id=$FGA_STORE_ID --model-id=$FGA_MODEL_AUTH user:charles viewer document:2021-budget
```

if you want to try even mode advanced models [continue here](https://openfga.dev/docs/modeling/advanced/gdrive#03-folder-permission-propagation). they will create folder permission and file sharing.


In the above example we mainly used the cli. But in a real setup you would have several components working together.
