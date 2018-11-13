import os

key = [
    'SSRMGMT_SECRET_KEY',
    'SSRMGMT_API_USERNAME',
    'SSRMGMT_API_PASSWORD',
    'SSRMGMT_EMAIL_USER',
    'SSRMGMT_EMAIL_PASSWORD',
    'SSRMGMT_MYSQL_USER',
    'SSRMGMT_MYSQL_PASSWORD', ]


def test_env_set():
    for k in key:
        print(k, os.environ[k])


if __name__ == '__main__':
    test_env_set()
