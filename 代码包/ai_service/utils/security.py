"""
SSRF Protection & Security Utilities
- URL domain whitelist validation
- Internal IP detection
- Image URL safety check
"""
import ipaddress
import socket
from urllib.parse import urlparse
from 代码包.ai_service.config import IMAGE_CONFIG, logger


def is_internal_ip(hostname: str) -> bool:
    """
    Check if a hostname resolves to an internal/private IP address.
    Returns True if IP is internal (should be blocked).
    """
    blocked_ranges = IMAGE_CONFIG['blocked_ip_ranges']

    try:
        # Parse as IP first
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        # Not an IP — resolve hostname
        try:
            ip = ipaddress.ip_address(socket.gethostbyname(hostname))
        except (socket.gaierror, ValueError):
            # Cannot resolve — treat as potentially dangerous
            logger.warning(f'Cannot resolve hostname: {hostname}, blocking by default')
            return True

    # Check against all blocked ranges
    for cidr in blocked_ranges:
        if ip in ipaddress.ip_network(cidr):
            logger.warning(f'Blocked internal IP: {ip} matches {cidr}')
            return True

    return False


def is_domain_whitelisted(hostname: str) -> bool:
    """
    Check if a hostname is in the allowed domain whitelist.
    """
    allowed_domains = IMAGE_CONFIG['allowed_image_domains']

    # Exact match or subdomain match
    for domain in allowed_domains:
        if hostname == domain or hostname.endswith('.' + domain):
            return True

    return False


def validate_image_url(image_url: str) -> tuple[bool, str]:
    """
    Full validation of an image URL for SSRF protection.

    Checks performed:
    1. URL must use http or https scheme
    2. Domain must be in whitelist
    3. Resolved IP must not be internal/private

    Returns:
        (is_valid, error_key_or_empty_string)
    """
    # 1. Parse URL
    try:
        parsed = urlparse(image_url)
    except Exception:
        return False, 'URL_FORMAT_INVALID'

    # 2. Scheme check
    if parsed.scheme not in ('http', 'https'):
        logger.warning(f'Blocked non-HTTP URL: {image_url}')
        return False, 'URL_NOT_WHITELISTED'

    # 3. Hostname extraction
    hostname = parsed.hostname
    if not hostname:
        return False, 'URL_NOT_WHITELISTED'

    # 4. Domain whitelist check
    if not is_domain_whitelisted(hostname):
        logger.warning(f'Domain not whitelisted: {hostname}')
        return False, 'URL_NOT_WHITELISTED'

    # 5. Internal IP check (DNS rebinding protection)
    if is_internal_ip(hostname):
        return False, 'URL_INTERNAL_IP'

    return True, ''


def validate_mime_type(mime_type: str) -> bool:
    """Check if MIME type is in the allowed list."""
    return mime_type in IMAGE_CONFIG['allowed_mime_types']


def validate_file_size(file_size: int) -> bool:
    """Check if file size is within the allowed limit."""
    return file_size <= IMAGE_CONFIG['max_file_size']
