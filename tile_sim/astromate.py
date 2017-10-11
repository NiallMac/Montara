#simple script to run swarp and sextractor on simulated images
import astromatic_wrapper as aw
import glob
import os
import fitsio
import esutil
import pylab

#set up output directory
outdir="astromatic_output"
if not os.path.isdir(outdir):
    os.makedirs(outdir)

#under the hood some temperary files are created...do this in scratch as home is easily filled
temp_path="/global/cscratch1/sd/maccrann/DES/image_sims/temp_path"

#First run swarp
#gather simulated single exposures
filenames=glob.glob('/global/cscratch1/sd/maccrann/DES/image_sims/output/sim*fits')
#output coadd filename
coadd_file = os.path.join(outdir, "coadd.fits") 
#read in the original coadd header to get center, pixel scale, image size !!pixel scale doesn't seem to be there??
coadd_head = fitsio.read_header("/global/cscratch1/sd/maccrann/DES/meds/y3v02/DES0544-2249/sources-r/OPS/multiepoch/Y3A1/r2689/DES0544-2249/p01/coadd/DES0544-2249_r2689p01_r.fits.fz",1)
#options for swarp (will use internal defaults for those not set here)
swarp_config = {"IMAGEOUT_NAME" : coadd_file, 
                "CENTER_TYPE" : "MANUAL", 
                "CENTER" : "%f,%f"%(coadd_head["RA_CENT"],coadd_head["DEC_CENT"]),
                "PIXELSCALE_TYPE" : "MANUAL",
                "PIXEL_SCALE" : "0.263,0.263",
                "IMAGE_SIZE" : "%d,%d"%(coadd_head["ZNAXIS1"],coadd_head["ZNAXIS2"])}
#run swarp
swarp = aw.api.Astromatic(code='SWarp')
#swarp.run(filenames, config = swarp_config, temp_path=temp_path)

#Then SExtractor
sex = aw.api.Astromatic(code='SExtractor')
#the default sextractor files are in the astro_config directory...
sex_config_dir="sex_config"
sex_config_file=os.path.join(sex_config_dir, "default.sex")
cat_file=os.path.join(outdir, "coadd_cat.fits")
sex_config = {"CATALOG_NAME": cat_file,
              "CATALOG_TYPE": 'FITS_1.0',
              "STARNNW_NAME": os.path.join(sex_config_dir,"default.nnw"),
              "FILTER_NAME": os.path.join(sex_config_dir,"default.conv"),
}
sex_params = ["NUMBER", "FLUX_AUTO", "FLUXERR_AUTO", "ALPHA_J2000", "DELTA_J2000","X_IMAGE","Y_IMAGE", "FLUX_RADIUS"]
#sex.run(coadd_file, config_file=sex_config_file, config=sex_config, params=sex_params, temp_path=temp_path)
              
#read in the output file and compare to truth
sex_data=fitsio.read(cat_file)
input_data=fitsio.read("DES0544-2249_input_objs.fits")
#match ra,dec
h=esutil.htm.HTM()
m_in,m_out,d12 = h.match(input_data['ra'],input_data['dec'],sex_data['ALPHA_J2000'],sex_data['DELTA_J2000'],radius=1./3600)
#make some comparison plots
fig=pylab.figure()
ax=fig.add_subplot(121)
ax.loglog(input_data['flux'][m_in], sex_data['FLUX_AUTO'][m_out],'.')
ax.set_xlabel('log(input flux)')
ax.set_ylabel('log(FLUX_AUTO)')
ax=fig.add_subplot(122)
ax.loglog(input_data['size'][m_in], sex_data['FLUX_RADIUS'][m_out]*0.263,'.')
ax.set_xlabel('log(input size)')
ax.set_ylabel('log(FLUX_RADIUS)')
fig.tight_layout()
fig.savefig(os.path.join(outdir, "flux_size_comp.png"))
