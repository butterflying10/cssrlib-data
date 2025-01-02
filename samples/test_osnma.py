"""
test script for Galileo OSNMA

@author Rui Hirokawa

"""

import numpy as np
import cssrlib.osnma as om
from binascii import unhexlify, hexlify
import matplotlib.pyplot as plt

tofst = -2  # time offset to syncronize tow

nma = om.osnma()

nma.flg_slowmac = True

file_galinav = '../data/doy2024-305/305a_galinav.txt'
doy = 305

dtype_ = [('tow', 'i8'), ('wn', 'i8'), ('prn', 'i8'),
          ('mt', 'i8'), ('k', 'i8'), ('nma', 'S10'),
          ('wt', 'i8'), ('nav', 'S32')]

dtype_ = [('wn', 'int'), ('tow', 'float'), ('prn', 'int'),
          ('type', 'int'), ('len', 'int'), ('nav', 'S512')]

v = np.genfromtxt(file_galinav, dtype=dtype_)

i = 0

v = v[v['type'] == 0]  # E1 only
tow = np.unique(v['tow'])
ntow = len(tow)
nsat = np.zeros((ntow, 3), dtype=int)
vstatus = np.zeros(ntow, dtype=int)

# nep = 90
# nep = 180
nep = 300

for i, t in enumerate(tow[0:nep]):
    vi = v[v['tow'] == t]
    for vn in vi:
        tow_ = int(vn['tow'])+tofst
        prn = int(vn['prn'])
        nma.prn_a = prn
        msg = unhexlify(vn['nav'])  # I/NAV (120bit+120bit)
        nav, nma_b = nma.load_inav(msg)
        nma.load_nav(nav, prn, tow_)
        if nma_b[0] != 0:  # for connected satellite
            nma.decode(nma_b, int(vn['wn']), tow_, prn)
            nsat[i, 1] += 1

    nsat[i, 0] = len(vi)
    nsat[i, 2] = nma.nsat  # authenticated sat
    vstatus[i] = nma.status


if True:

    tmax = 240

    fig, ax = plt.subplots()
    plt.plot(tow-tow[0], nsat[:, 0], label='tracked')
    plt.plot(tow-tow[0], nsat[:, 1], label='connected')
    plt.plot(tow-tow[0], nsat[:, 2], label='authenticated')
    plt.grid()
    plt.legend()
    plt.xlim([0, tmax])
    ax.set_xticks(np.arange(0, 300, 30))
    plt.ylabel('number of satellites')
    plt.xlabel('time [s]')
    plt.savefig('osnma-{0:d}-nsat-{1:d}.png'.format(doy, tmax))
    plt.show()

    y = np.ones(ntow)
    lbl_t = ['rootkey-loaded', 'rootkey-verified', 'keychain-verified',
             'utc-verified', 'auth-position']
    fig, ax = plt.subplots()
    for k in range(5):
        idx = np.where(vstatus & (1 << k))
        plt.plot(tow[idx]-tow[0], y[idx]*(k+1), '.', label=lbl_t[k])
    plt.grid()
    ax.set_yticks(np.arange(0, 6))
    ax.set_xticks(np.arange(0, 300, 30))
    plt.legend()
    plt.ylim([0, 6])
    plt.xlim([0, 240])
    plt.ylabel('status')
    plt.xlabel('time [s]')
    plt.savefig('osnma-{0:d}-status.png'.format(doy))
    plt.show()
