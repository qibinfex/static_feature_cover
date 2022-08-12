import socket



DEBUG = True

ENCODING = 'utf-8'

proxies = {'http': None, 'https': None}
headers = {'Content-type': 'application/x-www-form-urlencoded'}

if DEBUG:
    PORT = 8000
    DEVELOPER = 'qibinx.feng@intel.com'
    static = '/home/pnp/code/taas_api_fature_cover/static'
    LOG_LOCATION = '/var/log/docker/container_log/taas_api_fature_cover.log'
else:
    PORT = 80
    DEVELOPER = 'cheng.a.wang@intel.com, qibinx.feng@intel.com'
    LOG_LOCATION = '/container_log/taas_api_fature_cover.log'
