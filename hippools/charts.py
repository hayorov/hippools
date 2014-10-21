from flask import make_response
import matplotlib
import operator
from pool_tools import check_ip_is_free

matplotlib.use('Agg')

import matplotlib.pyplot as plt
from config_parser import ALL_IP_POOLS

from cStringIO import StringIO

html = '''
<html>
    <body>
        <img src="data:image/png;base64,{0}" />
    </body>
</html>
'''

pools_for_ping = [
    '1f2781f86c6e83a43b3c2473d3110225',
    'cd5f760c1a5627f986ed8bd5c5ca6238',
    '4625c6fc11a18c2c8a4b89af45d1bb27',
    '290ce2e56f36d0704ff3f45d56892c0d',
    '7bb7e0d4d923b9947be76e9e353563f5',
    'bee6acdba999cf19f9d07d8e82bb0ba0',
    'c5a139b68e2f08cd4526739b424d71d3',
    '87190362a7303e4d587fa0e4630809e0',
    '2428c28f0a5aa8aa43d3fee85af42371',
    '1799f6341c29161289cd5df34037776e',
    '75bf2110ac8031746b8a673666fda566',
    '004dbf4eee72c6284ab1c06f3d8ece5b',
    '4ba798b3464a12d63569f012ca2e3e4f',
    'db7d7c029bd7ceb6eafc6ec2d8830cb7',
    '09ed42d459466127e92b726926b729a9',
    'd50041be35be8d107a698217e578660e',
    '71a6c2876e5c04907183729ec327c2bf',
    'f4c89f0dfaede35a07b14227e160a863',
    '9dce93008b0da05ed4aea40214cd3618',
    '14228733ca6ecee0ff369b313d9f9f9c',
    '8a69f23f696f9849400857c7955830de',
    'f2329842adb92469b24e3ee026a7a295',
    '7b45845e5e9850907ab3c764cdb2d876',
    'c1c75ff28c3fa5ac36823585e9b78a15',
]


def chart_index():
    # The slices will be ordered and plotted counter-clockwise.
    labels = []
    sizes = []
    for pool_name in ALL_IP_POOLS:
        size = getattr(ALL_IP_POOLS[pool_name], 'size') + getattr(ALL_IP_POOLS[pool_name], 'used_size')
        labels.append('%s\nTotal IP %s' % (pool_name, size))
        sizes.append(size)
    plt.cla()
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True)
    plt.axis('equal')

    io = StringIO()
    plt.savefig(io, format='png')
    response = make_response(io.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response
    # data = io.getvalue().encode('base64')
    # return html.format(data)


def chart_utilisation(pool_name):
    labels = []
    sizes = []
    plt.cla()
    free = getattr(ALL_IP_POOLS[pool_name], 'size')
    used = getattr(ALL_IP_POOLS[pool_name], 'used_size')
    labels.append('%s\nFree IP %s' % (pool_name, free))
    sizes.append(free)
    labels.append('%s\nUsed IP %s' % (pool_name, used))
    sizes.append(used)
    plt.pie(sizes, labels=labels,
            autopct='%1.1f%%', shadow=True)
    plt.axis('equal')
    io = StringIO()
    plt.savefig(io, format='png')
    data = io.getvalue().encode('base64')
    return html.format(data)


def print_allocated(pool_name):
    sizes = []
    for ip_set_hash, pool in getattr(ALL_IP_POOLS[pool_name], '_db')['allocated'].items():
        print("'%s': %s," % (ip_set_hash, pool.size))
        #if ip_set_hash in pools_for_ping:
        #    print('%s %s pool free ? %s ' % (pool.size, ip_set_hash, test_ip_pools(pool)))
        sizes.append('%s' % pool.size)
    sort_dict = dict((x, sizes.count(x)) for x in set(sizes))
    print sort_dict
    print(sorted(sort_dict.iteritems(), key=operator.itemgetter(1)))
    get_free_pools(pool_name)


def collect_chart_fragmentation_data(pool_name):
    print_allocated(pool_name)
    bounds = []
    pool = getattr(ALL_IP_POOLS[pool_name], '_db')['pool']
    x_min = x_max = 0
    is_inited = False
    for i in pool.iter_cidrs():
        first = int(i.first)
        last = int(i.last)
        if not is_inited:
            x_min = first
            x_max = last
            is_inited = True
        if x_max < last:
            x_max = last
        bounds.append((first, last - first))

    return {'x_min': x_min, 'x_max': x_max, 'bounds': bounds}


def test_ip_pools(pool):
    is_free = True
    for ip_element in pool.iter_cidrs():
        for ip in ip_element:
            if not check_ip_is_free(str(ip)):
                print ip
                is_free = False
                break
        if not is_free:
            break
    return is_free


def chart_fragmentation(pool_name):
    fig = plt.figure(figsize=(60, 3))
    # create a horizontal plot
    ax1 = fig.add_subplot(511)
    fragmentation_data = collect_chart_fragmentation_data(pool_name)

    ax1.broken_barh(fragmentation_data['bounds'], (0, 1), edgecolor=None)
    ax1.set_xticklabels([])
    ax1.set_yticklabels([])
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_xlim(fragmentation_data['x_min'], fragmentation_data['x_max'])
    ax1.shrink = 0
    io = StringIO()
    plt.savefig(io, format='png')
    data = io.getvalue().encode('base64')
    return html.format(data)


def get_free_pools(pool_name):
    pool = getattr(ALL_IP_POOLS[pool_name], '_db')['pool']
    for ip_element in reversed(pool.iter_cidrs()):
        print('%s - %s\t%s' % (str(ip_element.first), str(ip_element.last), ip_element.size))

