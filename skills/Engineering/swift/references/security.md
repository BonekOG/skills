# Swift Security

## Security is boundary-specific

Start with the asset and attacker model: what must be protected, from whom, for how long, and on which compromised-device assumptions?

## Secrets

- Do not store tokens/passwords/private keys in UserDefaults, source code, plist files, logs, analytics, or crash breadcrumbs.
- Use Keychain access controls appropriate to the credential's lifecycle and sync requirements.
- Distinguish device unlock/biometric gating from cryptographic protection; a successful UI authentication boolean is not itself secure storage.

## Cryptography

- Prefer platform cryptographic APIs such as CryptoKit instead of custom primitives.
- Never reuse nonces where the primitive requires uniqueness.
- Use authenticated encryption when confidentiality and integrity are both required.
- Do not invent key-derivation, signature, certificate, or random-number schemes.
- Use Secure Enclave only when its key properties fit the use case; understand backup/sync/recovery implications.

## Network trust

Use the platform's normal TLS validation unless you have a well-maintained threat model that justifies pinning or custom trust. Custom trust code can reduce security if lifecycle/rotation/failure behavior is wrong.

## Privacy

- Minimize collection and retention.
- Redact sensitive fields from logs and analytics.
- Treat screenshots, pasteboard, files, notifications, widgets, and backups as potential disclosure surfaces.
- Verify entitlements and privacy manifests/usage descriptions relevant to used capabilities.

## Security review triggers

Escalate review when code touches:

- credentials or session lifecycle
- cryptographic keys/signatures/encryption
- biometric/passcode access control
- custom TLS/certificates
- deep links/universal links with privileged actions
- WebViews and JS bridges
- file protection/sharing/export
- deserialization of untrusted data
