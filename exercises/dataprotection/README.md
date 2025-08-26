# Data Protection

Data protection is a critical aspect of secure software design, especially when handling Personally Identifiable Information (PII). This tutorial covers essential techniques for protecting sensitive data through detection, anonymization, tokenization, and encryption.

---

## Table of Contents

1. [Personally Identifiable Information (PII) Detection](#personally-identifiable-information-pii-detection)
2. [Data Anonymization](#data-anonymization)
3. [Tokenization](#tokenization)
4. [Format Preserving Encryption](#format-preserving-encryption)

---

## Personally Identifiable Information (PII) Detection

### Overview

[Presidio](https://microsoft.github.io/presidio/) is an open-source framework for PII detection and de-identification. It helps organizations automatically identify sensitive information in text data to ensure compliance with privacy regulations

**Key Features:**

- Automatic PII detection (names, phone numbers, emails, etc.)
- Customizable detection rules and patterns
- Multiple anonymization strategies
- Support for multiple languages

### Try Online Demo

Experiment with Presidio's capabilities using the live demo:
[https://huggingface.co/spaces/presidio/presidio_demo](https://huggingface.co/spaces/presidio/presidio_demo)

### Local Setup

Start the Presidio service locally:
```bash
docker compose up
```

### Exercise 1: PII Detection

Once Presidio is running, analyze text for PII:

```bash
curl -X POST http://localhost:5002/analyze \
-H "Content-Type: application/json" \
-d '{
  "text": "My phone number is 555-123-4567.",
  "language": "en"
}'
```

**Expected Output:**
The response will identify detected PII entities with:

- Entity type (e.g., `PHONE_NUMBER`)
- Confidence score
- Character positions in the text

---

## Data Anonymization

### Exercise 2: Text Anonymization

Use the analysis results to anonymize the detected PII:

```bash
curl -X POST http://localhost:5004/anonymize -H "Content-Type: application/json"  -d '
    {
        "text": "My phone number is 555-123-4567",
        "anonymizers": {
            "PHONE_NUMBER": {
            "type": "replace",
            "new_value": "--Redacted phone number--"
            }
        },
        "analyzer_results": [
        {
            "start": 19,
            "end": 31,
            "score": 0.95,
            "entity_type": "PHONE_NUMBER"
        }
    ]}'
```

**Result:** The phone number will be replaced with `--Redacted phone number--`.

### Anonymization Strategies

Presidio supports multiple anonymization methods:

- **Replace:** Substitute with a placeholder value
- **Redact:** Remove the sensitive data entirely
- **Hash:** Replace with a cryptographic hash
- **Mask:** Partially obscure the data (e.g., `XXX-XX-1234`)
- **Encrypt:** Use reversible encryption (requires key management)

for the full list see [documentation](https://microsoft.github.io/presidio/anonymizer/)

### Advanced Features

For more advanced use cases, explore the [Presidio documentation](https://microsoft.github.io/presidio/learn_presidio/):

- Custom entity recognizers
- Multi-language support
- Integration with machine learning models
- Batch processing capabilities

---

## Tokenization

### Overview

Tokenization replaces sensitive information with mathematically unrelated tokens that preserve referential integrity while protecting the original data. Unlike encryption, tokens cannot be reversed without access to the tokenization system.

### Tools and Solutions

- **Commercial:** HashiCorp Vault (paid feature)
- **Open Source:** Databunker, CipherSweet

### Exercise 3: Databunker Tokenization

Start the Databunker service:

```bash
docker compose up
```

**Access the GUI:** [http://localhost:3000/site](http://localhost:3000/site)

- Use the root token login method
- Root Token: `DEMO`

### Create a Tokenized Record

Store sensitive user data and receive a token:

```bash
curl -s http://localhost:3000/v1/user -X POST \
  -H "X-Bunker-Token: DEMO" \
  -H "Content-Type: application/json" \
  -d '{"first":"John","last":"Doe","login":"john","email":"<user@gmail.com>"}'
```

**Response:** You'll receive a unique token that you can use in your application or store in a database.

### Retrieve Original Data

Use the token to retrieve the original sensitive data:

```bash
curl -s -H "X-Bunker-Token: DEMO" -X GET http://localhost:3000/v1/user/login/john
```

### Security Best Practices

1. **Token Vault Isolation:** Keep the tokenization system separate from your main application
2. **Access Controls:** Implement strict authentication and authorization
3. **Audit Logging:** Track all tokenization and detokenization requests
4. **Key Rotation:** Regularly rotate encryption keys used by the tokenization system
5. **Network Security:** Use TLS and network segmentation to protect token vault communications

---

## Format Preserving Encryption (FPE)

Format Preserving Encryption encrypts data while maintaining its original format. This is particularly useful when:

- Legacy systems expect specific data formats
- Database schema constraints cannot be changed
- Preserving data patterns is required for functionality

### Examples

- **Credit Card:** `4532-1234-5678-9012` → `4532-8976-3421-7845`
- **Phone:** `(555) 123-4567` → `(555) 987-6543`

there are many libraries that can achieve this.
