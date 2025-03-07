'''
Functions to read in data
'''


################################################################################
# IMPORT MODULES
#-------------------------------------------------------------------------------
from astropy.io import fits
from astropy.table import Table, QTable

import numpy as np
import numpy.ma as ma
################################################################################






################################################################################
#-------------------------------------------------------------------------------
def read_master_file(filename):
    '''
    Read in the master file containing all the galaxy meta-data


    PARAMETERS
    ==========

    filename : string
        File name of the master file


    RETURNS
    =======

    master_table : astropy table
        Astropy table of the master file
    '''

    master_table = QTable.read(filename, format='ascii.ecsv')

    return master_table
################################################################################






################################################################################
#-------------------------------------------------------------------------------
def construct_filename(galaxy_ID, data_directory):
    '''
    Build the file name for a galaxy's data cube.


    PARAMETERS
    ==========

    galaxy_ID : length-2 tuple
        (plate, fiberID) for individual MaNGA galaxy

    data_directory : string
        Location of data cubes on computer system


    RETURNS
    =======

    cube_filename : string
        File name of data cube for MaNGA galaxy identified by the given 
        plate-fiberID.
    '''

    plate, fiberID = galaxy_ID

    cube_filename = data_directory + plate + '/' + fiberID + '/manga-' + plate + '-' + fiberID + '-MAPS-HYB10-GAU-MILESHC.fits.gz'

    return cube_filename
################################################################################





################################################################################
#-------------------------------------------------------------------------------
def build_galaxy_dict(data_table):
    '''
    Create dictionary of galaxy IDs and their indices in the data table.


    PARAMETERS
    ==========

    data_table : length-N astropy table
        Table of galaxies.  Required columns are 'MaNGA_plate' and 
        'MaNGA_fiberID'


    RETURNS
    =======

    galaxy_dict : length-N dictionary
        Dictionary of (plate, fiberID) keys with a value of the row index 
        for indexing into data_table.
    '''


    galaxy_dict = {}

    for idx, (plate, fiberID) in enumerate(zip(data_table['MaNGA_plate'], data_table['MaNGA_fiberID'])):

        galaxy_dict[(plate, fiberID)] = idx

    return galaxy_dict
################################################################################





################################################################################
#-------------------------------------------------------------------------------
def write_masses(masses, IDs, master_filename):
    '''
    Add mass data to master table.


    PARAMETERS
    ==========

    masses : astropy table of length N
        Table of galaxy masses, ratios, and associated errors.

    IDs : length-N list of length-2 tuples
        List of (plate, IFU) galaxy IDs.  Length is the same as N, such that 
        masses[i] is the mass of galaxy IDs[i].

    master_filename : string
        File name of the master file
    '''


    ############################################################################
    # Read in master file
    #---------------------------------------------------------------------------
    master_table = read_master_file(master_filename)
    ############################################################################


    ############################################################################
    # Match up elliptical galaxies to table
    #---------------------------------------------------------------------------
    galaxy_dict = build_galaxy_dict(master_table)

    for i, galaxy in enumerate(IDs):

        j = galaxy_dict[galaxy]

        ########################################################################
        # Write data to table
        #-----------------------------------------------------------------------
        master_table['Mtot'][j] = masses['Mtot'][i]
        master_table['Mtot_error'][j] = masses['Mtot_err'][i]
        master_table['Mdark'][j] = masses['Mdark'][i]
        master_table['Mdark_error'][j] = masses['Mdark_err'][i]
        master_table['Mdark_Mstar_ratio'][j] = masses['Mdark_Mstar_ratio'][i]
        master_table['Mdark_Mstar_ratio_error'][j] = masses['Mdark_Mstar_ratio_err'][i]
        ########################################################################
    ############################################################################


    ############################################################################
    # Write master table to file
    #---------------------------------------------------------------------------
    master_table.write(master_filename[:-4] + '_ellipticals.txt', 
                       format='ascii.commented_header', overwrite=True)
    ############################################################################
################################################################################






################################################################################
#-------------------------------------------------------------------------------
def open_map(cube_filename, map_name):
    '''
    Import a masked map from the data cube.


    PARAMETERS
    ==========

    cube_filename : string
        File name of data cube for a MaNGA galaxy.

    map_name : string
        Field name of the map to import


    RETURNS
    =======

    masked_map : 2d masked numpy array
        Masked numpy array of the requested map from the data cube.
    '''


    ############################################################################
    # Import data cube
    #---------------------------------------------------------------------------
    cube = fits.open(cube_filename)
    ############################################################################


    ############################################################################
    # Extract (and correct for instrumental resolution effects) stellar velocity 
    # dispersion map
    #
    # See https://www.sdss.org/dr16/manga/manga-data/working-with-manga-data/ 
    # for correction details
    #---------------------------------------------------------------------------
    if map_name is 'STELLAR_SIGMA':

        # Data
        star_sigma = np.sqrt(cube[map_name].data**2 
                             - cube['STELLAR_SIGMACORR'].data[0]**2)

        # Mask extension
        star_sigma_mask_extension = cube['STELLAR_SIGMA'].header['QUALDATA']

        # Mask
        mStar_sigma = ma.array(star_sigma, mask=cube[star_sigma_mask_extension].data>0)

        masked_map = ma.masked_invalid(mStar_sigma)
    #---------------------------------------------------------------------------
    # Extract the inverse variance map of the velocity dispersion
    #---------------------------------------------------------------------------
    elif map_name is 'STELLAR_SIGMA_IVAR':

        # Data
        star_sigma_ivar = cube[map_name].data

        # Mask
        mStar_sigma_ivar = ma.array(star_sigma_ivar, mask=cube['STELLAR_SIGMA_MASK'].data>0)

        masked_map = ma.masked_invalid(mStar_sigma_ivar)
    #---------------------------------------------------------------------------
    # Extract average r-band image
    #---------------------------------------------------------------------------
    elif map_name is 'SPX_MFLUX':

        # Data
        r_band = cube[map_name].data

        # Mask
        masked_map = ma.masked_equal(r_band, 0)
    ############################################################################

    return masked_map