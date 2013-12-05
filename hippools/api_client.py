from requests import get, delete

# temp
API_HOST = 'http://127.0.0.1:5001/api/v1'


def allocate(pool, ip_count):
    r = get('%s/pools/%s?ip_count=%s' % (API_HOST, pool, ip_count))
    return r.json()


def deallocate(pool, ipset_id):
    r = delete('%s/pools/%s?ipset_id=%s' % (API_HOST, pool, ipset_id))
    try:
        err = r.json()
    except:
        return True
    raise Exception(err['mesage'])
