# yamlr subscribe
**Yamlr Pro Subscription & License Management**

The `yamlr subscribe` command opens the secure upgrade portal to manage or activate a Yamlr Pro / Enterprise workspace subscription.

---

## Synopsis

```bash
yamlr subscribe
```

---

## Description

Yamlr Core (`scan`, `diff`, `fmt`, `catalog`, `doctor`) is 100% free and unlimited forever.

Yamlr Pro unlocks advanced capabilities:
*   Multi-resource automated relational repairs (`yamlr heal --apply`).
*   Fleet-wide GitOps Pull Request batching (`yamlr fleet`).
*   Cryptographic manifest signing & verification (`yamlr sign`, `yamlr verify`).
*   Cross-resource topological blast radius analysis (`yamlr graph`).
*   Floating team licenses for CI/CD runners and platform engineering teams.

Once you obtain your license key, activate it instantly on any workstation or air-gapped CI runner with:
```bash
yamlr auth activate <LICENSE_KEY>
```

Team entitlement renewal does not contact a licensing service by default. To opt in to automatic renewal before a Team token expires, set `YAMLR_LICENSE_AUTO_RENEW=1`. The renewal request sends the stored signed entitlement token to the HTTPS licensing gateway. You can override the gateway origin with `YAMLR_LICENSE_GATEWAY_URL`. Without automatic renewal, activate a renewed token explicitly before the current token expires.

---

## Examples

```bash
# Open the Pro subscription portal
yamlr subscribe
```
