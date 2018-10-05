METHOD_CHOICES = (
    ('aes-256-cfb', 'aes-256-cfb'),
    ('aes-128-ctr', 'aes-128-ctr'),
    ('rc4-md5', 'rc4-md5'),
    ('salsa20', 'salsa20'),
    ('chacha20', 'chacha20'),
    ('none', 'none'),
)

PROTOCOL_CHOICES = (
    ('auth_sha1_v4', 'auth_sha1_v4'),
    ('auth_aes128_md5', 'auth_aes128_md5'),
    ('auth_aes128_sha1', 'auth_aes128_sha1'),
    ('auth_chain_a', 'auth_chain_a'),
    ('origin', 'origin'),
)


OBFS_CHOICES = (
    ('plain', 'plain'),
    ('http_simple', 'http_simple'),
    ('http_simple_compatible', 'http_simple_compatible'),
    ('http_post', 'http_post'),
    ('tls1.2_ticket_auth', 'tls1.2_ticket_auth'),
)
