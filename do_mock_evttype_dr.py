from astropy.io import fits
from astropy.coordinates import SkyCoord
from pathlib import Path
from mock_dr_utils import *

def create_irf_table(name, obs_id, evt_type):
    ones_data = [[1.,2], [3.,4.]]
    col = fits.Column(name='DATA', format='2D', array=ones_data)
    table_hdu_ones = fits.BinTableHDU.from_columns([col])

    hdr = table_hdu_ones.header
    common_md(hdr, obs_id)

    if name == 'aeff':
        hdr["EXTNAME"] = 'EFFECTIVE AREA ' + str(evt_type)
        hdr["HDUCLAS1"] = 'RESPONSE'
        hdr["HDUCLAS2"] = 'EFF_AREA'
        hdr["HDUCLAS3"] = 'FULL-ENCLOSURE'
        hdr["HDUCLAS4"] = '2D'
    if name == 'edisp':
        hdr["EXTNAME"] = 'ENERGY DISPERSION ' + str(evt_type)
        hdr["HDUCLAS1"] = 'RESPONSE'
        hdr["HDUCLAS2"] = 'EDISP   '
        hdr["HDUCLAS3"] = 'FULL-ENCLOSURE'
        hdr["HDUCLAS4"] = '2D'
    if name == 'psf':
        hdr["EXTNAME"] = 'POINT SPREAD FUNCTION ' + str(evt_type)
        hdr["HDUCLAS1"] = 'RESPONSE'
        hdr["HDUCLAS2"] = 'RPSF    '
        hdr["HDUCLAS3"] = 'FULL-ENCLOSURE'
        hdr["HDUCLAS4"] = '2D'
    if name == 'bkg':
        hdr["EXTNAME"] = 'BACKGROUND ' + str(evt_type)
        hdr["HDUCLAS1"] = 'RESPONSE'
        hdr["HDUCLAS2"] = 'BKG     '
        hdr["HDUCLAS3"] = 'FULL-ENCLOSURE'
        hdr["HDUCLAS4"] = '2D'
    hdr["EVTTYPE"] = str(evt_type)

    return table_hdu_ones


def create_irf_file(filename, obs_id, evt_type_list):
    # Create a PrimaryHDU object
    hdu = fits.PrimaryHDU()
    common_md(hdu.header, obs_id)

    # Create an HDUList and write to a file
    hdul = fits.HDUList([hdu])

    for evt_type in evt_type_list:
        # Create the 4 IRFs
        for irf in ['aeff','edisp','psf','bkg']:
            hdu_irf = create_irf_table(name=irf, obs_id=obs_id, evt_type=evt_type)
            hdul.append(hdu_irf)

    # Saving the file
    save_hdul(hdul=hdul, filename=filename, overwrite=True)


def create_grouping_table(irffilename, obs_id, evt_type_list):
    xtension = ['BINTABLE', 'BINTABLE']
    name = ['EVENTS', 'GTI']
    loc = ['null', 'null']
    uri = ['URL', 'URL']
    sel_type = ['none', 'none']
    for evt_type in evt_type_list:
        for irf in ['EFFECTIVE AREA ', 'ENERGY DISPERSION ', 'POINT SPREAD FUNCTION ', 'BACKGROUND ']:
            xtension.append('BINTABLE')
            name.append(irf + evt_type)
            loc.append(irffilename)
            uri.append('URL')
            sel_type.append(evt_type)

    col1 = fits.Column(name='MEMBER_XTENSION', format='8A', array=xtension)
    col2 = fits.Column(name='MEMBER_NAME', format='30A', array=name)
    col3 = fits.Column(name='MEMBER_LOCATION', format='30A', array=loc)
    col4 = fits.Column(name='MEMBER_URI_TYPE', format='3A', array=uri)
    col5 = fits.Column(name='EVT_TYPE', format='3A', array=sel_type)
    cols = fits.ColDefs([col1, col2, col3, col4, col5])
    table_hdu = fits.BinTableHDU.from_columns(cols)

    hdr = table_hdu.header
    hdr["EXTNAME"] = 'GROUPING'
    common_md(hdr, obs_id)
    # print(table_hdu)
    # print(repr(hdr))

    return table_hdu


def create_main_file(filename="simple.fits", irffilename="./irfs_file.fits", obs_id="1", coord=None, evt_type_list=None):
    # Create a PrimaryHDU object
    hdu = fits.PrimaryHDU()
    common_md(hdu.header, obs_id)

    # Create an HDUList and write to a file
    hdul = fits.HDUList([hdu])

    # Create the Grouping table
    hdu_gp = create_grouping_table(irffilename=irffilename, obs_id=obs_id, evt_type_list=evt_type_list)
    hdul.append(hdu_gp)

    hdu_evt = create_event_hdu(obs_id=obs_id, coord=coord,
                               nentries=len(evt_type_list)*3,
                               evt_type_list=evt_type_list)
    hdul.append(hdu_evt)
    hdu_gti = create_gti_hdu(obs_id)
    hdul.append(hdu_gti)

    # Saving the file
    save_hdul(hdul=hdul, filename=filename, overwrite=True)

if __name__ == "__main__":

    GCcoord = SkyCoord("17h45m40.03599s", "-29d00m28.1699s", frame="icrs")
    evt_type_list = ["A","B","C"]

    dr_dir_simple = "./w-evttype-dr/"
    nfiles_simple = 3
    for _ in range(nfiles_simple):
        obs_id = random_string()
        filename = dr_dir_simple / Path(f"obs_{obs_id}.fits")
        irffilename = dr_dir_simple / Path(f"./obs_{obs_id}_irfs.fits")
        create_main_file(filename=filename, obs_id=obs_id, coord=GCcoord, evt_type_list=evt_type_list)
        create_irf_file(irffilename, obs_id, evt_type_list)
