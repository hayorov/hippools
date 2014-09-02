import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
from config_parser import ALL_IP_POOLS

from cStringIO import StringIO

html = '''
<html>
    <body>
        <img src="data:image/png;base64,{}" />
    </body>
</html>
'''


def chart_index():
    # The slices will be ordered and plotted counter-clockwise.
    labels = []
    sizes = []
    for pool_name in ALL_IP_POOLS:
        size = getattr(ALL_IP_POOLS[pool_name], 'size') + getattr(ALL_IP_POOLS[pool_name], 'used_size')
        labels.append('%s\nTotal IP %s' % (pool_name, size))
        sizes.append(size)
    plt.cla()
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')

    io = StringIO()
    plt.savefig(io, format='png')
    data = io.getvalue().encode('base64')

    return html.format(data)


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
            autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')
    io = StringIO()
    plt.savefig(io, format='png')
    data = io.getvalue().encode('base64')

    return html.format(data)


def chart_fragmentation(pool_name):
    bounds = []
    fig = plt.figure(figsize=(22, 3))
    # create a horizontal plot
    ax1 = fig.add_subplot(221)
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
        bounds.append((first, last-first))

    ax1.broken_barh(bounds, (0, 1))
    ax1.set_xticklabels([])
    ax1.set_yticklabels([])
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_xlim(x_min, x_max)
    io = StringIO()
    plt.savefig(io, format='png')
    data = io.getvalue().encode('base64')
    return html.format(data)

