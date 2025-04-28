from astropy.io import fits
from astropy.table import Table
import astropy.units as u
from pathlib import Path
import random as rd
import string

__all__ = ["random_string", "save_hdul", "common_md", "create_event_hdu", "create_gti_hdu"]

def random_string(length = 3):
   return ''.join(rd.choice(string.ascii_lowercase) for i in range(length))


def save_hdul(hdul, filename, overwrite):
    filedir = Path(filename).parent
    filedir.mkdir(parents=True, exist_ok=~overwrite)
    hdul.writeto(filename, overwrite=overwrite)
    # print(f"FITS file '{filename}' created successfully.")


def common_md(hdu_header, obs_id, ob_id=None):
    hdu_header["ORIGIN"] = 'VODF team'
    hdu_header["TELESCOP"] = 'CTAO'
    hdu_header["INSTRUME"] = 'ALL_S'
    hdu_header["HDUCLASS"] = 'VODF'
    hdu_header["HDUVERS"] = '0.1'
    hdu_header["HDUDOC"] = 'https://vodf.readthedocs.io/en/latest/'
    hdu_header['AUTHOR'] = 'VODF team'
    hdu_header['COMMENT'] = "This is a simple FITS file created for VODF tests."
    hdu_header['OBS_ID'] = str(obs_id)
    if ob_id:
        hdu_header['OB_ID'] = str(ob_id)


def create_event_hdu(obs_id, coord, nentries=3, evt_type_list=None, evt_class_list=None, ob_id=None):

    evt_id = []
    evt_time =[]
    evt_en = []
    evt_ra = []
    evt_dec = []
    evt_type = []
    evt_class = []
    evt_opt = []
    col_list = []
    for ievt in range(nentries):
        evt_id.append(str(ievt + 1))
        evt_time.append(60760 + rd.uniform(0, 100) * 1.e-3)
        evt_en.append(rd.uniform(0.05, 300))
        evt_ra.append(rd.uniform(coord.ra - 1 * u.deg, coord.ra + 1 * u.deg).value)
        evt_dec.append(rd.uniform(coord.dec - 1 * u.deg, coord.dec + 1 * u.deg).value)
        evt_opt.append(str(rd.uniform(0, 300)))
        if evt_type_list:
            evt_type.append(rd.choice(evt_type_list))
        if evt_class_list:
            evt_class.append(rd.choice(evt_class_list))

    col1 = fits.Column(name='ID', format='8A', array=evt_id)
    col2 = fits.Column(name='TIME', format='D', array=evt_time, unit='s')
    col3 = fits.Column(name='ENERGY', format='E', array=evt_en, unit='TeV')
    col4 = fits.Column(name='RA', format='E', array=evt_ra, unit='deg')
    col5 = fits.Column(name='DEC', format='E', array=evt_dec, unit='deg')
    col6 = fits.Column(name='OPT', format='8A', array=evt_opt)
    col_list = [col1, col2, col3, col4, col5, col6]
    if evt_type_list:
        col7 = fits.Column(name='EVT_TYPE', format='8A', array=evt_type)
        col_list.append(col7)
    if evt_class_list:
        col8 = fits.Column(name='EVT_CLASS', format='8A', array=evt_class)
        col_list.append(col8)
    hdu_evt = fits.BinTableHDU.from_columns(col_list)

    hdr = hdu_evt.header
    hdr["EXTNAME"] = 'EVENTS'
    hdr["HDUCLAS1"] = 'EVENTS'
    common_md(hdr, obs_id=obs_id, ob_id=ob_id)

    return hdu_evt


def create_gti_hdu(obs_id, ob_id=None):
    gti = Table(names=("START","STOP"))
    gti.add_row([60760, 60760.5])
    gti.add_row([60760.7, 60761.2])
    hdu_gti = fits.BinTableHDU(data=gti)

    hdr = hdu_gti.header
    hdr["EXTNAME"] = 'GTI'
    hdr["HDUCLAS1"] = 'GTI'
    common_md(hdr, obs_id, ob_id)

    return  hdu_gti