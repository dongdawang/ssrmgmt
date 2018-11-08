METHOD_CHOICES = (
    ('none', 'none'),
    ('rc4', 'rc4'),
    ('rc4-md5', 'rc4-md5'),
    ('rc4-md5-6', 'rc4-md5-6'),

    ('aes-128-ctr', 'aes-128-ctr'),
    ('aes-192-ctr', 'aes-192-ctr'),
    ('aes-256-ctr', 'aes-256-ctr'),

    ('aes-128-cfb', 'aes-128-cfb'),
    ('aes-192-cfb', 'aes-192-cfb'),

    ('aes-128-cfb8', 'aes-128-cfb8'),
    ('aes-192-cfb8', 'aes-192-cfb8'),
    ('aes-256-cfb8', 'aes-256-cfb8'),
)

PROTOCOL_CHOICES = (
    ('origin', 'origin'),
    ('auth_sha1_v4', 'auth_sha1_v4'),
    ('auth_aes128_md5', 'auth_aes128_md5'),
    ('auth_aes128_sha1', 'auth_aes128_sha1'),
)

OBFS_CHOICES = (
    ('plain', 'plain'),
    ('http_simple', 'http_simple'),
    ('http_post', 'http_post'),
    ('tls1.2_ticket_auth', 'tls1.2_ticket_auth'),
)
