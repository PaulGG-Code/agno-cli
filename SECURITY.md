# Security Policy

## Supported Versions

We are committed to providing security updates for the following versions of Agno CLI:

| Version | Supported          |
| ------- | ------------------ |
| 2.4.x   | :white_check_mark: |
| 2.3.x   | :white_check_mark: |
| 2.2.x   | :x:                |
| < 2.2   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in Agno CLI, please follow these steps:

### 1. **DO NOT** create a public GitHub issue
Security vulnerabilities should be reported privately to prevent potential exploitation.

### 2. **Email the security team**
Send a detailed report to the repository owner with the following information:

- **Subject**: `[SECURITY] Agno CLI Vulnerability Report`
- **Description**: Clear description of the vulnerability
- **Steps to reproduce**: Detailed steps to reproduce the issue
- **Impact assessment**: Potential impact of the vulnerability
- **Suggested fix**: If you have suggestions for fixing the issue
- **Your contact information**: So we can follow up with you

### 3. **What happens next**
- You will receive an acknowledgment within 48 hours
- We will investigate the report and provide updates
- Once confirmed, we will work on a fix
- We will coordinate disclosure with you
- A security advisory will be published when the fix is ready

## Security Considerations

### API Key Management

Agno CLI handles sensitive API keys for various services. We implement the following security measures:

- **Local Storage**: API keys are stored locally in `~/.agno_cli/config.yaml`
- **File Permissions**: Configuration files use restricted permissions (600)
- **Environment Variables**: Support for environment variable-based configuration
- **No Logging**: API keys are never logged or displayed in output
- **Encryption**: Consider using system keyrings for additional security

### File System Operations

The CLI has extensive file system access capabilities. Security measures include:

- **Path Validation**: All file paths are validated to prevent directory traversal
- **Safe Operations**: File operations are performed with appropriate error handling
- **User Confirmation**: Destructive operations require user confirmation
- **Permission Checks**: Respects file system permissions

### Multi-Agent System Security

The multi-agent system has specific security considerations:

- **Agent Isolation**: Agents operate in isolated contexts
- **State Persistence**: Agent states are stored securely
- **Communication Security**: Inter-agent communication is logged and monitored
- **Tool Access Control**: Agents have controlled access to system tools

### External API Security

When interacting with external APIs:

- **Rate Limiting**: Implemented to prevent API abuse
- **Error Handling**: Secure error handling to prevent information leakage
- **Input Validation**: All inputs are validated before API calls
- **HTTPS Only**: All external communications use HTTPS

## Security Best Practices for Users

### 1. **API Key Security**
```bash
# Use environment variables instead of config files
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"

# Or use system keyrings
pip install keyring
```

### 2. **Configuration Security**
```bash
# Set proper file permissions
chmod 600 ~/.agno_cli/config.yaml

# Use secure configuration directory
export AGNO_CONFIG_DIR="~/.agno_cli"
```

### 3. **Network Security**
- Use VPN when accessing sensitive data
- Avoid using Agno CLI on public networks for sensitive operations
- Regularly rotate API keys

### 4. **File System Security**
- Review file operations before execution
- Use `--confirm` flags for destructive operations
- Regularly audit file permissions

## Security Features

### 1. **Input Validation**
- All user inputs are validated and sanitized
- Path traversal attacks are prevented
- SQL injection protection in database operations
- XSS protection in web-related operations

### 2. **Error Handling**
- Secure error messages that don't leak sensitive information
- Graceful degradation when services are unavailable
- Comprehensive logging for security auditing

### 3. **Authentication & Authorization**
- API key validation
- Service-specific authentication
- Permission-based access control

### 4. **Data Protection**
- No sensitive data in logs
- Secure data transmission
- Local data encryption options

## Security Audit

### Regular Security Reviews
- Monthly dependency vulnerability scans
- Quarterly security code reviews
- Annual penetration testing
- Continuous security monitoring

### Dependency Management
```bash
# Check for vulnerable dependencies
pip install safety
safety check

# Update dependencies regularly
pip install --upgrade agno-cli
```

## Incident Response

### Security Incident Classification

| Severity | Description | Response Time |
|----------|-------------|---------------|
| Critical | Remote code execution, data breach | 24 hours |
| High | Privilege escalation, data exposure | 72 hours |
| Medium | Information disclosure, DoS | 1 week |
| Low | Minor security issues | 2 weeks |

### Response Process

1. **Detection**: Identify and assess the security incident
2. **Containment**: Isolate affected systems and prevent further damage
3. **Eradication**: Remove the root cause of the incident
4. **Recovery**: Restore systems to normal operation
5. **Lessons Learned**: Document and improve security measures

## Security Updates

### Release Process
- Security fixes are prioritized for immediate release
- Patches are backported to supported versions
- Security advisories are published with detailed information
- Users are notified through multiple channels

### Update Notifications
- GitHub Security Advisories
- Release notes with security information
- Email notifications for critical vulnerabilities
- Social media announcements

## Responsible Disclosure

### Timeline
- **Initial Response**: 48 hours
- **Status Update**: 1 week
- **Fix Development**: 2-4 weeks (depending on severity)
- **Public Disclosure**: After fix is available

### Recognition
- Security researchers are credited in advisories
- Hall of Fame for significant contributions
- Bug bounty program (future consideration)

## Security Tools and Resources

### Recommended Security Tools
```bash
# Dependency scanning
pip install safety bandit

# Code analysis
pip install bandit

# Security testing
pip install pytest-security
```

### Security Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python-security.readthedocs.io/)
- [CLI Security Guidelines](https://clig.dev/#security)

## Compliance

### Data Protection
- GDPR compliance for EU users
- CCPA compliance for California users
- Local data storage options
- Data minimization principles

### Privacy
- No telemetry or data collection
- Local processing by default
- Transparent data handling
- User control over data

## Security Contacts

### Primary Contact
- **Repository Owner**: Paul Gedeon
- **Response Time**: 48 hours for initial response

### Alternative Contacts
- **GitHub Security**: Use GitHub's security advisory feature
- **Community**: Post in discussions (for general security questions only)

## Security History

### Recent Security Updates
- **v2.4.8**: Enhanced input validation for file operations
- **v2.4.7**: Improved API key handling and logging
- **v2.4.6**: Fixed potential path traversal vulnerability

### Security Advisories
- All security advisories are published on GitHub
- CVE numbers are assigned for significant vulnerabilities
- Detailed remediation steps are provided

---

**Last Updated**: July 2025

**Version**: 1.0

For security-related questions or concerns, please contact the repository owner directly. Do not post security issues in public forums or GitHub issues. 