from requests import get, delete

# temp
HOST = 'http://127.0.0.1:5001'
API_VERSION = '/api/v1'
allocate_url = '/pools/%s?ip_count=%s'
deallocate_url = '/pools/%s?ipset_id=%s'


def allocate(pool, ip_count):
    r = get(HOST + API_VERSION + allocate_url % (pool, ip_count))
    return r.json()


def deallocate(pool, ipset_id):
    r = delete(HOST + API_VERSION + deallocate_url % (pool, ipset_id))
    try:
        err = r.json()
    except:
        return True
    raise Exception(err['mesage'])
