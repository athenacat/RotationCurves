
from astropy.table import QTable

from extract_Vmax_v1 import match_Vmax


###############################################################################
# User inputs
#------------------------------------------------------------------------------
DATA_PIPELINE = 'Pipe3D'
#DATA_PIPELINE = 'DRP'

MASTER_FILE_NAME = 'Pipe3D-master_file_vflag_BB_minimize_chi10_smooth2p27.txt'
###############################################################################


###############################################################################
# Read in the 'master_table.'
#------------------------------------------------------------------------------
master_table = QTable.read( MASTER_FILE_NAME, format='ascii.ecsv')
###############################################################################


###############################################################################
# Match to the 'master_table' according to 'index'
#------------------------------------------------------------------------------
master_table = match_Vmax( master_table, DATA_PIPELINE)
###############################################################################


###############################################################################
# Write the 'master_table.'
#------------------------------------------------------------------------------
master_table.write( MASTER_FILE_NAME, format='ascii.ecsv', overwrite=True)
###############################################################################
