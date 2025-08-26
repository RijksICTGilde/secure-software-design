# API Gateway

An API gateway is a crucial security component in modern architectures. It acts as a single entry point for API requests and provides essential security features including:

- **Authorization** - Control who can access your APIs
- **Rate limiting** - Protect against abuse and DoS attacks  
- **Schema validation** - Ensure incoming requests meet expected formats
- **IP filtering** - Block malicious or unwanted traffic
- **Load balancing** - Distribute traffic across multiple backend services

Popular API gateway solutions include Kong, Nginx, Tyk, and Apache APISIX. In this tutorial, we'll explore Apache APISIX and its security features.

---

## Prerequisites

Start the APISIX environment with two test web servers:

```bash
docker compose up
```

This will create:

- **APISIX API Gateway** - Running on port 9080 (API) and 9180 (Admin)
- **Web Server 1** - Backend service for testing
- **Web Server 2** - Second backend service for load balancing

**APISIX Dashboard**: Access the web UI at [http://127.0.0.1:9180/ui/](http://127.0.0.1:9180/ui/) using admin key: `edd1c9f034335f136f87ad84b625c8f1`

---

## Exercise 1: Basic Routing

Let's create our first route that directs traffic from the gateway to a backend service.

**Create a route to the first web service:**

```bash
curl -i http://127.0.0.1:9180/apisix/admin/routes -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1" -X PUT -d '
{
  "id": "website",
  "uri": "/website",
  "upstream": {
    "type": "roundrobin",
    "nodes": {
      "web1:80": 1
    }
  }
}'
```

**Test the route:**

```bash
curl http://127.0.0.1:9080/website
```

You should see a response from the first web server.

---

## Exercise 2: Load Balancing

Load balancing distributes incoming requests across multiple backend servers, improving reliability and performance.

**Update the route to include both web servers:**

```bash
curl -i http://127.0.0.1:9180/apisix/admin/routes -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1"  -X PUT -d '
{
  "id": "website",
  "uri": "/website",
  "upstream" : {
    "type": "roundrobin",
    "nodes": {
      "web1:80": 1,
      "web2:80": 1
    }
  }
}'
```

**Test load balancing by making multiple requests:**

```bash
curl http://127.0.0.1:9080/website
```

Run this command several times and notice how responses alternate between the two web servers.

---

## Exercise 3: API Key Authentication

API keys provide a simple way to authenticate and identify API consumers. This helps track usage and prevent unauthorized access.

**Step 1: Create a consumer (API user)**

First, we need to create a "consumer" - this represents a developer or application that will use our API:

```bash
curl -i "http://127.0.0.1:9180/apisix/admin/consumers" -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1" -X PUT -d '
{
  "username": "berry",
  "plugins": {
    "key-auth": {
      "key": "secret-key"
    }
  }
}'
```

**Step 2: Enable API key authentication on the route**

Now we'll require API key authentication for our route:

```bash
curl -i "http://127.0.0.1:9180/apisix/admin/routes/website" -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1"  -X PATCH -d '
{
  "plugins": {
    "key-auth": {}
  }
}'
```

**Step 3: Test authentication**

Try these requests to see the difference:

```bash
curl -i http://127.0.0.1:9080/website
curl -i http://127.0.0.1:9080/website -H 'apikey: wrong-key'
curl -i http://127.0.0.1:9080/website -H 'apikey: secret-key'
```

- First request: **401 Unauthorized** (no API key)
- Second request: **401 Unauthorized** (wrong API key)  
- Third request: **200 OK** (correct API key)

**Additional Authentication Options**: APISIX also supports OAuth2, JWT tokens, and other authentication methods. See the [documentation](https://apisix.apache.org/docs/apisix/plugins/key-auth/) for more details.

**Disable authentication for next exercises:**

```bash
curl "http://127.0.0.1:9180/apisix/admin/routes/website" -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1"  -X PATCH -d '
{
  "plugins": {
    "key-auth": {
      "_meta": {
        "disable": true
      }
    }
  }
}'
```

---

## Exercise 4: Rate Limiting

Rate limiting protects your backend services from being overwhelmed by too many requests. This is essential for preventing DoS attacks and ensuring fair usage.

**Enable rate limiting (2 requests per 10-second window):**

```bash
curl -i "http://127.0.0.1:9180/apisix/admin/routes/website" -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1" -X PATCH -d '
{
  "plugins": {
    "limit-count": {
        "count": 2,
        "time_window": 10,
        "rejected_code": 503
     }
  }
}'
```

**Test rate limiting with multiple requests:**

This command will make 100 requests and count how many succeed vs. fail:

```bash
count=$(seq 100 | xargs -I {} curl "http://127.0.0.1:9080/website" -I -sL | grep "503" | wc -l); echo \"200\": $((100 - $count)), \"503\": $count
```

You should see that most requests return **503 Service Unavailable** due to rate limiting.

**Rate Limiting Algorithms**: APISIX offers different rate limiting plugins:

- `limit-count`: Simple counter-based limiting
- `limit-req`: Token bucket algorithm (smoother traffic shaping)
- `limit-conn`: Limits concurrent connections

**Disable rate limiting:**

```bash
curl -i "http://127.0.0.1:9180/apisix/admin/routes/website" -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1" -X PATCH -d '
{
    "plugins": {
        "limit-count": {
            "_meta": {
                "disable": true
            }
        }
    }
}'
```

---

## Additional Security Features

APISIX provides many other security plugins you can explore:

### IP Address Filtering

Block or allow specific IP addresses or ranges.

**Documentation**: [IP Restriction Plugin](https://apisix.apache.org/docs/apisix/plugins/ip-restriction/)

### URL Pattern Protection  

Block requests that match malicious patterns (e.g., SQL injection attempts).

**Documentation**: [URI Blocker Plugin](https://apisix.apache.org/docs/apisix/plugins/uri-blocker/)

### Request Validation

Validate incoming requests against predefined schemas to ensure data integrity.

**Documentation**: [Request Validation Plugin](https://apisix.apache.org/docs/apisix/plugins/request-validation/)

---

## Summary

In this tutorial, you learned how to use Apache APISIX to implement key API gateway security features:

1. **Basic routing** - Direct traffic to backend services
2. **Load balancing** - Distribute requests across multiple servers  
3. **API key authentication** - Control access to your APIs
4. **Rate limiting** - Protect against abuse and overload

These features form the foundation of API security and help protect your backend services from various threats while providing better control over API access and usage.

**Next Steps**: Explore the additional security plugins mentioned above and consider how you might combine multiple security measures for a comprehensive API protection strategy.
