"""
sample for QZNMA

[1] Quasi-Zenith Satellite System Interface Specification
    Satellite Positioning, Navigation and Timing Service (IS-QZSS-PNT-006),
    July, 2024

Note:
    to use the package for QZSNMA, the user needs to
    install the public keys provided by QSS.

@author Rui Hirokawa

"""

import os
from binascii import unhexlify
import numpy as np
from cssrlib.gnss import prn2sat, uGNSS
from cssrlib.qznma import qznma, uNavId
import matplotlib.pyplot as plt

if not os.path.exists('../data/pubkey/qznma/002.der'):
    print('please install public key file from QSS.')
    exit(-1)

dtype = [('wn', 'int'), ('tow', 'float'), ('prn', 'int'),
         ('type', 'int'), ('len', 'int'), ('nav', 'S512')]
msg_nav_t = {uNavId.GPS_LNAV: 'LNAV', uNavId.GPS_CNAV: 'CNAV',
             uNavId.GPS_CNAV2: 'CNAV2',
             uNavId.GAL_FNAV: 'F/NAV', uNavId.GAL_INAV: 'I/NAV'}

# prn_ref = -1
prn_ref = 199
navmode = uNavId.GPS_LNAV  # 1:LNAV, 2:CNAV, 3:CNAV2
doy = 305
flg_gnss = True

qz = qznma()
qz.monlevel = 1

if navmode == uNavId.GPS_LNAV:
    navfile = '../data/doy2024-305/305a_qzslnav.txt'
elif navmode == uNavId.GPS_CNAV:
    navfile = '../data/doy2024-305/305a_qzscnav.txt'
elif navmode == uNavId.GPS_CNAV2:
    navfile = '../data/doy2024-305/305a_qzscnav2.txt'

v = np.genfromtxt(navfile, dtype=dtype)

if navmode == uNavId.GPS_CNAV:
    v = v[v['type'] == 26]  # L5 CNAV only

if flg_gnss:
    navfile_n = '../data/doy2024-305/305a_qzsl6.txt'
    navfile_gpslnav = '../data/doy2024-305/305a_gpslnav.txt'
    navfile_gpscnav = '../data/doy2024-305/305a_gpscnav.txt'
    # navfile_gpscnav2 = '../data/doy2024-305/305a_gpscnav2.txt'
    navfile_galinav = '../data/doy2024-305/305a_galinav.txt'
    navfile_galfnav = '../data/doy2024-305/305a_galfnav.txt'

    # load navigation message
    qz.load_navmsg_lnav(navfile_gpslnav)
    qz.load_navmsg_cnav(navfile_gpscnav)
    qz.load_navmsg_inav(navfile_galinav)
    qz.load_navmsg_fnav(navfile_galfnav)

    vn = np.genfromtxt(navfile_n, dtype=dtype)


# tow_ = np.unique(v['tow'])
tow_ = np.arange(v['tow'][0], v['tow'][-1])
nep = len(tow_)
# nep = 1200

nsat = np.zeros((nep, 4), dtype=int)
vstatus = np.zeros(nep, dtype=int)

for k in range(nep):
    vi_ = v[v['tow'] == tow_[k]]

    for vi in vi_:
        msg = unhexlify(vi['nav'])
        sat = prn2sat(uGNSS.QZS, vi['prn'])
        qz.decode(tow_[k], msg, None, sat, navmode)

    if flg_gnss:
        vin_ = vn[(vn['tow'] == tow_[k]) & (vn['type'] == 1)]
        if prn_ref > 0:
            vin_ = vin_[vin_['prn'] == prn_ref]

        for vin in vin_:
            msg_n = unhexlify(vin['nav'])
            qz.decode(tow_[k], None, msg_n, sat, navmode)

    nsat[k, 0] = qz.count_tracked_sat(tow_[k])
    nsat[k, 1:] = np.array([qz.nsat[d] for d in qz.nsat])

if True:

    tmax = 500

    fig, ax = plt.subplots()
    # plt.plot(tow_-tow_[0], nsat[:, 0], label='tracked')
    plt.plot(tow_-tow_[0], nsat[:, 1], label='GPS ' +
             msg_nav_t[qz.navmode[uGNSS.GPS]])
    plt.plot(tow_-tow_[0], nsat[:, 2], label='GAL ' +
             msg_nav_t[qz.navmode[uGNSS.GAL]])
    plt.plot(tow_-tow_[0], nsat[:, 3], label='QZS '+msg_nav_t[navmode])
    plt.grid()
    plt.legend()
    plt.xlim([0, tmax])
    # ax.set_xticks(np.arange(0, 300, 30))
    plt.ylabel('number of satellites')
    plt.xlabel('time [s]')
    # plt.savefig('qznma-{0:d}-nsat-{1:d}.png'.format(doy, tmax))
    plt.show()
