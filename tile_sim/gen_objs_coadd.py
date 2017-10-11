#generate some input objects for a given tile
#use cosmos sampler in galsim_extra to get flux and size distribution
#save to fits file
import numpy as np
import galsim_extra
import fitsio
import galsim
import argparse
from esutil.coords import randsphere

def parse_args():
    import argparse
    description = 'Generate fits catalog of galaxy sizes, fluxes and positions for a given DES tile'

    parser = argparse.ArgumentParser(description=description, add_help=True,
                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('coadd_file', type=str, help='coadd file for the tile')
    parser.add_argument('output_file', type=str, help='output catalog file')
    parser.add_argument('--coadd_ext', type=int, default=2)
    parser.add_argument('-n','--number_density', type=float, default=None, help='number of objects per square arcmin')
    parser.add_argument('-N','--number', type=int, default=None, help='total number of objects')
    parser.add_argument('-s', '--scale_flux', type=int, default=1, help='scale fluxes by this factor')
    args=parser.parse_args()
    if args.number_density is None:
        if args.number is None:
            raise ValueError('give me either a number or number density of objects')
    else:
        if args.number is not None:
            raise ValueError('give me either a number or number density of objects (not both)')
    return args

def main():

    args=parse_args()
    #get cosmos sampler
    cs = galsim_extra.cosmos_sampler.CosmosSampler()
    
    #read in header of coadd file
    coadd_fits = fitsio.FITS(args.coadd_file)
    coadd_header = coadd_fits[args.coadd_ext].read_header()
    xsize, ysize = int(coadd_header['ZNAXIS1']), int(coadd_header['ZNAXIS2'])
    print xsize, ysize
    wcs,origin = galsim.wcs.readFromFitsHeader(args.coadd_file)
    corners = []
    im_corners = [galsim.PositionD(*c) for c in [(0,0),(0,ysize),(xsize,0),(xsize,ysize)]]
    world_corners = [wcs.toWorld(im_c) for im_c in im_corners]
    ra_list = [c.ra.wrap(world_corners[0].ra) for c in world_corners]
    dec_list = [c.dec for c in world_corners]
    ra_min, ra_max, dec_min, dec_max = np.min(ra_list).rad(), np.max(ra_list).rad(), np.min(dec_list).rad(), np.max(dec_list).rad()

    if args.number_density:
        #compute area
        area_rad2 = np.abs(np.sin(dec_max)-np.sin(dec_min)) * (ra_max-ra_min)
        area_deg2 = np.degrees(np.degrees(area_rad2))
        area_arcmin2 = area_deg2*3600
        args.number = area_arcmin2 * args.number_density

    #set up output array
    out_data = np.empty((args.number), dtype=[('flux',float),('size',float),('ra',float),('dec',float)])
    #generate flux and size
    size, flux = cs.sample(size=args.number).T
    #generate ra,dec
    ra, dec = randsphere(args.number, ra_range=[np.degrees(ra_min),np.degrees(ra_max)], dec_range=[np.degrees(dec_min), np.degrees(dec_max)])
    out_data['flux']=flux*args.scale_flux
    out_data['size']=size
    out_data['ra']=ra
    out_data['dec']=dec

    #save data to fits file
    print 'writing %d objects to %s'%(len(out_data), args.output_file)
    fitsio.write(args.output_file, out_data, clobber=True)

if __name__=="__main__":
    main()
