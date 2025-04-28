from astropy.io import fits
from astropy.coordinates import SkyCoord
from pathlib import Path
from mock_dr_utils import *

def create_irf_table(name, obs_id):
    ones_data = [[1.,2], [3.,4.]]
    col = fits.Column(name='DATA', format='2D', array=ones_data)
    table_hdu_ones = fits.BinTableHDU.from_columns([col])

    hdr = table_hdu_ones.header
    common_md(hdr, obs_id)

    if name == 'aeff':
        hdr["EXTNAME"] = 'EFFECTIVE AREA'
        hdr["HDUCLAS1"] = 'RESPONSE'
        hdr["HDUCLAS2"] = 'EFF_AREA'
        hdr["HDUCLAS3"] = 'FULL-ENCLOSURE'
        hdr["HDUCLAS4"] = '2D'
    if name == 'edisp':
        hdr["EXTNAME"] = 'ENERGY DISPERSION'
        hdr["HDUCLAS1"] = 'RESPONSE'
        hdr["HDUCLAS2"] = 'EDISP   '
        hdr["HDUCLAS3"] = 'FULL-ENCLOSURE'
        hdr["HDUCLAS4"] = '2D'
    if name == 'psf':
        hdr["EXTNAME"] = 'POINT SPREAD FUNCTION'
        hdr["HDUCLAS1"] = 'RESPONSE'
        hdr["HDUCLAS2"] = 'RPSF    '
        hdr["HDUCLAS3"] = 'FULL-ENCLOSURE'
        hdr["HDUCLAS4"] = '2D'
    if name == 'bkg':
        hdr["EXTNAME"] = 'BACKGROUND'
        hdr["HDUCLAS1"] = 'RESPONSE'
        hdr["HDUCLAS2"] = 'BKG     '
        hdr["HDUCLAS3"] = 'FULL-ENCLOSURE'
        hdr["HDUCLAS4"] = '2D'

    return table_hdu_ones


def create_irf_file(filename, obs_id):
    # Create a PrimaryHDU object
    hdu = fits.PrimaryHDU()
    common_md(hdu.header, obs_id)

    # Create an HDUList and write to a file
    hdul = fits.HDUList([hdu])

    # Create the 4 IRFs
    for irf in ['aeff','edisp','psf','bkg']:
        hdu_irf = create_irf_table(name=irf, obs_id=obs_id)
        hdul.append(hdu_irf)

    # Saving the file
    save_hdul(hdul=hdul, filename=filename, overwrite=True)


def create_grouping_table(irffilename, obs_id):
    xtension = ['BINTABLE', 'BINTABLE', 'BINTABLE', 'BINTABLE', 'BINTABLE']
    name = ['EVENTS', 'EFFECTIVE AREA', 'ENERGY DISPERSION', 'POINT SPREAD FUNCTION', 'BACKGROUND', 'GTI']
    loc = ['NULL', irffilename.name, irffilename.name, irffilename.name, irffilename.name, 'NULL']
    uri = ['URL', 'URL', 'URL', 'URL', 'URL', 'URL']

    col1 = fits.Column(name='MEMBER_XTENSION', format='8A', array=xtension)
    col2 = fits.Column(name='MEMBER_NAME', format='30A', array=name)
    col3 = fits.Column(name='MEMBER_LOCATION', format='30A', array=loc)
    col4 = fits.Column(name='MEMBER_URI_TYPE', format='3A', array=uri)
    cols = fits.ColDefs([col1, col2, col3, col4])
    table_hdu = fits.BinTableHDU.from_columns(cols)

    hdr = table_hdu.header
    hdr["EXTNAME"] = 'GROUPING'
    common_md(hdr, obs_id)
    # print(table_hdu)
    # print(repr(hdr))

    return table_hdu


def create_main_file(filename="simple.fits", irffilename="./irfs_file.fits", obs_id="1", coord=None):
    # Create a PrimaryHDU object
    hdu = fits.PrimaryHDU()
    common_md(hdu.header, obs_id)

    # Create an HDUList and write to a file
    hdul = fits.HDUList([hdu])

    # Create the Grouping table
    hdu_gp = create_grouping_table(irffilename=irffilename, obs_id=obs_id)
    hdul.append(hdu_gp)

    hdu_evt = create_event_hdu(obs_id=obs_id, coord=coord)
    hdul.append(hdu_evt)
    hdu_gti = create_gti_hdu(obs_id)
    hdul.append(hdu_gti)

    # Saving the file
    save_hdul(hdul=hdul, filename=filename, overwrite=True)

if __name__ == "__main__":

    GCcoord = SkyCoord("17h45m40.03599s", "-29d00m28.1699s", frame="icrs")

    dr_dir_simple = "./simple-dr/"
    nfiles_simple = 3
    for _ in range(nfiles_simple):
        obs_id = random_string()
        filename = dr_dir_simple / Path(f"obs_{obs_id}.fits")
        irffilename = dr_dir_simple / Path(f"./obs_{obs_id}_irfs.fits")
        create_main_file(filename, irffilename, obs_id=obs_id, coord=GCcoord)
        create_irf_file(irffilename, obs_id)
