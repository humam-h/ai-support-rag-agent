# VPN Troubleshooting

If a user cannot connect to the corporate VPN, first confirm that the user's
internet connection is working normally.

Ask the user to disconnect and reconnect to the VPN client.

If authentication fails, verify that the user's account is active and that
multi-factor authentication is working.

If the VPN connects but internal company resources cannot be reached, check
whether the user has received the expected corporate IP address and DNS
settings.

Test connectivity to an internal resource by IP address. If access by IP works
but access by hostname fails, investigate DNS resolution.

If multiple users are affected simultaneously, check the VPN gateway,
firewall rules, and recent network configuration changes.

Escalate the issue to the network team if multiple users remain unable to
access internal resources after basic troubleshooting.
