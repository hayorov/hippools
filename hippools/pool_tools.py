from pyping import ping


def check_ip_is_free(ip):
    ret = ping(ip, timeout=2).ret_code
    return ret == 1