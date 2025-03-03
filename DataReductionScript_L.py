#
#start casa again
#make a dirty image
import glob
import os
import shutil as sh 

project = '16B-376'
config = 'A'
band = 'L'
image_prefix = 'J0612-06'  # name of target
ms_prefix = image_prefix+'_'+band+'_'+config+'_v1' # MS file "root" (i.e., before ".ms" part) name
msfile = ms_prefix + '.ms'
#myrefant = 'ea27'

myspws = '*'  # image all spws
version = 'd' 
beamsize = 1.3 # estimate of the synthesized beamsize in arcseconds
myimsize = 500 # image size in pixels
mystokes = 'I'
mythresh = '0.1mJy' # set to a few times the expected (theoretical) rms noise
myniter = 0 # if niter = 0, output is a dirty image!
myuvrange = '' # set this to "filter" out emission on certain spatial scales
myfield = '0' # field to image.  See the output of the LISTOBS task for field ID info.
myweighting = 'briggs' # weight function to be applied during imaging
myrobust = 0 # (pure uniform) -2 < robust < 2 (pure natural)
#mymultiscale = [0,5,15] # good starting point for multiscale if imaging extended source
#mymask = 'J1651+34.AX.test_intact.mask' # do not use a clean mask
#interactive = True


# END USER INPUT!!!!
#=====================================================================

cellsize = beamsize/5.0 # to get 5 pixels across each beam
cellsize_str = str(cellsize)
mycell = cellsize_str+'arcsec' # format for use as input to CLEAN task
ArcminPerCell = cellsize/60.0
imdims = ArcminPerCell*myimsize
print "The image size is {0} arcminutes.".format(imdims)

default(tclean)
vis = msfile
field = myfield

spw = myspws
specmode = 'mfs' 
nterms = 2
gridder = 'wproject' 
wprojplanes = 128
facets = 1
niter = myniter
threshold = mythresh
imsize = myimsize
cell = mycell
stokes = mystokes
weighting = myweighting
robust = myrobust
deconvolver="mtmfs"
scales=[0, 5, 15]
nterms=2
interactive = False
uvtaper = ''
          
myimage = image_prefix + '_' + config + band + '_nterms' + str(nterms) + '_multiscale_' + myweighting + '_r' + str(myrobust) + '_v' + version
imagename = myimage
print imagename
tclean()
#-----------------------------------------------------------------------------------------
#------------------------------$$$$$$$$$$$$$$$$$$$$$$$$$$$$-------------------------------

myspws = '*'  # image all spws
version = '2' 
beamsize = beamsize
mystokes = 'I'
mythresh = '0.05mJy' # set to a few times the expected (theoretical) rms noise
myniter = 10 # if niter = 0, output is a dirty image!
myuvrange = '' # set this to "filter" out emission on certain spatial scales
myfield = '0' # field to image.  See the output of the LISTOBS task for field ID info.
myweighting = 'briggs' # weight function to be applied during imaging
myrobust = 0 # (pure uniform) -2 < robust < 2 (pure natural)
#mymultiscale = [0,5,15] # good starting point for multiscale if imaging extended source
#mymask = 'circle[[ '+max_pos[0]+', '+max_pos[1]+'],  '+str(beammin)+'arcsec]' # do not use a clean mask
#interactive = True
mask = 'J0612-06_L_A_tclean.reg'

# END USER INPUT!!!!
#=====================================================================

cellsize = beamsize/5.0 # to get 5 pixels across each beam
cellsize_str = str(cellsize)
mycell = cellsize_str+'arcsec' # format for use as input to CLEAN task
ArcminPerCell = cellsize/60.0
imdims = ArcminPerCell*myimsize
print "The image size is {0} arcminutes.".format(imdims)

default(tclean)
vis = msfile
field = myfield

spw = myspws
specmode = 'mfs' 
nterms = 2
gridder = 'wproject' 
wprojplanes = 128
facets = 1
niter = myniter
threshold = mythresh
imsize = myimsize
cell = mycell
stokes = mystokes
weighting = myweighting
robust = myrobust
deconvolver="mtmfs"
scales=[0, 5, 15]
nterms=2
interactive = False
uvtaper = ''
          
 
myimage = image_prefix + '_' + config + band + '_nterms' + str(nterms) + '_multiscale_' + myweighting + '_r' + str(myrobust) + '_v' + version
imagename = myimage
print imagename
tclean()
combine_flag = False



#try forcing point source model and check 
#delete the intial model first 
default(delmod)
vis = msfile
scr = True
delmod()

#search for the center point:
dirtyim = 'J0612-06_AL_nterms2_multiscale_briggs_r0_vd.image.tt0'
default(imstat)
default(imhead)
dirtstat = imstat(imagename = dirtyim)
max_pos = dirtstat['maxposf'].split(',')
SNR= dirtstat['max']/dirtstat['rms']

print dirtstat['max']/dirtstat['rms'], '::::::::: SNR\n'

#add a point source model 
cl.addcomponent(flux = 1.0, fluxunit = 'Jy', shape='point', dir= 'J2000 '+max_pos[0]+'  '+max_pos[1])
cl.rename(image_prefix+'_L_A.pointsrc1Jy.cl')
cl.close()
#determine beam size 
beammaj  = imhead(imagename = dirtyim, mode = 'get', hdkey = 'bmaj')['value']
beammin  = imhead(imagename = dirtyim, mode = 'get', hdkey = 'bmin')['value']
#regsize  = sqrt(beammaj*beammin)
default(ft)
vis = msfile
complist = image_prefix+'_L_A.pointsrc1Jy.cl'
usescratch = True
ft()

'''
default(delmod)
vis = msfile
scr = True
delmod()

default(ft)
vis = msfile
model = ['J0404-24_AX_nterms2_multiscale_briggs_r0_v2.image.tt0', 'J0404-24_AX_nterms2_multiscale_briggs_r0_v2.image.tt1']
usescratch = True
nterms = 2
ft()
'''



# selfcal 
default(gaincal)
vis = msfile
caltable = ms_prefix+'.P1.gcal'
solint = '30s'
#if(combine_flag):

minsnr = 3
refant = 'ea09'
calmode = 'p'
gaincal()


default(applycal)
vis = msfile
gaintable = ms_prefix+'.P1.gcal'
interp = 'nearest'
nspws = 16
#if(combine_flag):
spwmap = [0]*nspws
applycal()

#-----------------------------------------------------------------------------------------
#------------------------------$$$$$$$$$$$$$$$$$$$$$$$$$$$$-------------------------------
#create region files and see if additional cleaning is required
#################################################################################################33
'''
- on source---- ---- ---- ---- ---- ----
(J0000+78_AX_nterms2_multiscale_briggs_r0_v2.image.tt0)
        Stokes       Velocity          Frame        Doppler      Frequency 
             I   -15.0386km/s           LSRK          RADIO  9999000046.63 
BrightnessUnit       BeamArea           Npts            Sum    FluxDensity 
       Jy/beam        25.4837           1406   1.818226e-01   7.134863e-03 
          Mean            Rms        Std dev        Minimum        Maximum 
  1.293191e-04   6.803070e-04   6.681405e-04  -5.883705e-05   7.121467e-03 
  region count 
             1 
---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
(J0000+78_AX_nterms2_multiscale_briggs_r0_v2.image.tt0)
        Stokes       Velocity          Frame        Doppler      Frequency 
             I   -15.0386km/s           LSRK          RADIO  9999000046.63 
BrightnessUnit       BeamArea           Npts            Sum    FluxDensity 
       Jy/beam        25.4837        1708746   2.371111e-02   9.304426e-04 
          Mean            Rms        Std dev        Minimum        Maximum 
  1.387632e-08   1.845242e-05   1.845242e-05  -9.764948e-05   9.778338e-05 
  region count
             1 
---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----



'''
#--------------------------------------------------------------------------------------------
#-----==========================-=-=-=
#############################################################################################################
#create region files and see if additional cleaning is required
#if not proceed with selfcal : if strong source, run additional phasecal rounds to get rid of strong ripples
#in the image. 
##############################################################################################3

myspws = '*'  # image all spws
version = '3' 
beamsize = beamsize
mystokes = 'I'
mythresh = '0.05mJy' # set to a few times the expected (theoretical) rms noise
myniter = 1000 # if niter = 0, output is a dirty image!
myuvrange = '' # set this to "filter" out emission on certain spatial scales
myfield = '0' # field to image.  See the output of the LISTOBS task for field ID info.
myweighting = 'briggs' # weight function to be applied during imaging
myrobust = 0 # (pure uniform) -2 < robust < 2 (pure natural)
#mymultiscale = [0,5,15] # good starting point for multiscale if imaging extended source
#mymask = 'circle[[ '+max_pos[0]+', '+max_pos[1]+'],  '+str(beammin)+'arcsec]' # do not use a clean mask
#interactive = True
mask = 'J0612-06_L_A_tclean.reg'

# END USER INPUT!!!!
#=====================================================================

cellsize = beamsize/5.0 # to get 5 pixels across each beam
cellsize_str = str(cellsize)
mycell = cellsize_str+'arcsec' # format for use as input to CLEAN task
ArcminPerCell = cellsize/60.0
imdims = ArcminPerCell*myimsize
print "The image size is {0} arcminutes.".format(imdims)

default(tclean)
vis = msfile
field = myfield

spw = myspws
specmode = 'mfs' 
nterms = 2
gridder = 'wproject' 
wprojplanes = 128
facets = 1
niter = myniter
threshold = mythresh
imsize = myimsize
cell = mycell
stokes = mystokes
weighting = myweighting
robust = myrobust
deconvolver="mtmfs"
scales=[0, 5, 15]
nterms=2
interactive = False
uvtaper = ''
          
 
myimage = image_prefix + '_' + config + band + '_nterms' + str(nterms) + '_multiscale_' + myweighting + '_r' + str(myrobust) + '_v' + version
imagename = myimage
print imagename
tclean()



default(delmod)
vis = msfile
scr = True
delmod()

default(ft)
vis = msfile
nterms = 2
model = [myimage+'.model.tt0', myimage+'.model.tt1']
usescratch = True
ft()



# selfcal 
default(gaincal)
vis = msfile
caltable = 'J0404-24_X_A_v1.P2.gcal'
solint = '60s'
#if(combine_flag):
combine = 'spw'
minsnr = 2.5
refant = 'ea24'
calmode = 'p'
gaintable = 'J0404-24_X_A_v1.P1.gcal'
spwmap = [16]*nspws
gaincal()

caltable_prefix = 'J0404-24_X_A_v1'

default(applycal)
vis = msfile
gaintable = [caltable_prefix+'.P1.gcal', caltable_prefix+'.P2.gcal']
interp = 'nearest'
#if(combine_flag):
spwmap = [[16]*nspws, [16]*nspws]
applycal()


myspws = '*'  # image all spws
version = '4' 
beamsize = 0.2
mystokes = 'I'
mythresh = '0.05mJy' # set to a few times the expected (theoretical) rms noise
myniter = 2000 # if niter = 0, output is a dirty image!
myuvrange = '' # set this to "filter" out emission on certain spatial scales
myfield = '0' # field to image.  See the output of the LISTOBS task for field ID info.
myweighting = 'briggs' # weight function to be applied during imaging
myrobust = 0 # (pure uniform) -2 < robust < 2 (pure natural)
#mymultiscale = [0,5,15] # good starting point for multiscale if imaging extended source
#mymask = 'circle[[ '+max_pos[0]+', '+max_pos[1]+'],  '+str(beammin)+'arcsec]' # do not use a clean mask
#interactive = True
mask = 'J0404-24_X_A_tclean.reg'

# END USER INPUT!!!!
#=====================================================================

cellsize = beamsize/5.0 # to get 5 pixels across each beam
cellsize_str = str(cellsize)
mycell = cellsize_str+'arcsec' # format for use as input to CLEAN task
ArcminPerCell = cellsize/60.0
imdims = ArcminPerCell*myimsize
print "The image size is {0} arcminutes.".format(imdims)

default(tclean)
vis = msfile
field = myfield

spw = myspws
specmode = 'mfs' 
nterms = 2
gridder = 'wproject' 
wprojplanes = 128
facets = 1
niter = myniter
threshold = mythresh
imsize = myimsize
cell = mycell
stokes = mystokes
weighting = myweighting
robust = myrobust
deconvolver="mtmfs"
scales=[0, 5, 15]
nterms=2
interactive = False
uvtaper = ''
          
 
myimage = image_prefix + '_' + config + band + '_nterms' + str(nterms) + '_multiscale_' + myweighting + '_r' + str(myrobust) + '_v' + version
imagename = myimage
print imagename
tclean()


##################################################################################################################

default(delmod)
vis = msfile
scr = True
delmod()

default(ft)
vis = msfile
nterms = 2
model = [myimage+'.model.tt0', myimage+'.model.tt1']
usescratch = True
ft()



# selfcal 
default(gaincal)
vis = msfile
caltable = 'J0404-24_X_A_v1.AP3.gcal'
solint = '60s'
#if(combine_flag):
combine = 'spw'
minsnr = 3
refant = 'ea24'
calmode = 'ap'
gaintable = [caltable_prefix+'.P1.gcal', caltable_prefix+'.P2.gcal']
spwmap = [[16]*nspws, [16]*nspws]
gaincal()

caltable_prefix = 'J0404-24_X_A_v1'

default(applycal)
vis = msfile
gaintable = [caltable_prefix+'.P1.gcal', caltable_prefix+'.P2.gcal', caltable_prefix+'.AP3.gcal']
interp = 'nearest'
#if(combine_flag):
spwmap = [[16]*nspws, [16]*nspws, [16]*nspws]
applycal()



myspws = '*'  # image all spws
version = '5' 
beamsize = 0.2 # estimate of the synthesized beamsize in arcseconds
myimsize = 2000 # image size in pixels
mystokes = 'I'
mythresh = '0.02mJy' # set to a few times the expected (theoretical) rms noise
myniter = 4000 # if niter = 0, output is a dirty image!
myuvrange = '' # set this to "filter" out emission on certain spatial scales
myfield = '0' # field to image.  See the output of the LISTOBS task for field ID info.
myweighting = 'briggs' # weight function to be applied during imaging
myrobust = 0 # (pure uniform) -2 < robust < 2 (pure natural)
mymultiscale = [0,5,15] # good starting point for multiscale if imaging extended source
#mymask = 'circle[[ '+max_pos[0]+', '+max_pos[1]+'],  '+str(beammin)+'arcsec]' # do not use a clean mask
mask = 'J0404-24_X_A_tclean.reg'
#interactive = True


# END USER INPUT!!!!
#=====================================================================

cellsize = beamsize/5.0 # to get 5 pixels across each beam
cellsize_str = str(cellsize)
mycell = cellsize_str+'arcsec' # format for use as input to CLEAN task
ArcminPerCell = cellsize/60.0
imdims = ArcminPerCell*myimsize
print "The image size is {0} arcminutes.".format(imdims)

default(tclean)
vis = msfile
field = myfield

spw = myspws
specmode = 'mfs' 
nterms = 2
gridder = 'wproject' 
wprojplanes = 128
facets = 1
niter = myniter
threshold = mythresh
imsize = myimsize
cell = mycell
stokes = mystokes
weighting = myweighting
robust = myrobust
deconvolver="mtmfs"
scales=[0, 5, 15]
nterms=2
interactive = False
uvtaper = ''
          
 
myimage = image_prefix + '_' + config + band + '_nterms' + str(nterms) + '_multiscale_' + myweighting + '_r' + str(myrobust) + '_v' + version
imagename = myimage
print imagename
tclean()


##################################################################################################################





exportfits(imagename = myimage+'.image.tt0', fitsimage = image_prefix+'F.fits')

myimage = image_prefix + '_' + config + band + '_nterms' + str(nterms)  + myweighting + '_r' + str(myrobust) + '_v' + version+'_LF'
vis = msfile
imagename = myimage
mask = mymask
spw = '0~7'


clean()

exportfits(imagename = myimage+'.image.tt0', fitsimage = image_prefix+'L.fits')
myimage = image_prefix + '_' + config + band + '_nterms' + str(nterms)  + myweighting + '_r' + str(myrobust) + '_v' + version+'_HF'
vis = msfile
mask = mymask
imagename = myimage

spw = '8~15'
clean()
exportfits(imagename = myimage+'.image.tt0', fitsimage = image_prefix+'U.fits')


################################################################################
################################################################################
#$$$$$$$$$$$$$$$$$$$---------Smooth and Regridding--------------$$$$$$$$$$$$$#
#-----------------------------------------------------------------------------
################################################################################


fits_lsb = image_prefix+'L.fits'
fits_usb = image_prefix+'U.fits'
im_lsb = image_prefix + '_' + config + band + '_nterms' + str(nterms)  + myweighting + '_r' + str(myrobust) + '_v' + version+'_LF.image.tt0'
im_usb = image_prefix + '_' + config + band + '_nterms' + str(nterms)  + myweighting + '_r' + str(myrobust) + '_v' + version+'_HF.image.tt0'

default(imhead)
imhead_lsb = imhead(imagename = im_lsb, mode = 'summary')
lsb_bmaj = imhead_lsb['restoringbeam']['major']['value']
lsb_bmin = imhead_lsb['restoringbeam']['minor']['value']
lsb_pa   = imhead_lsb['restoringbeam']['positionangle']['value']

#actual smoothing of upper baseband


default(imsmooth)
imagename = im_usb
kernal = 'gauss'
beam = imhead_lsb['restoringbeam'] #shoxuld be a dictionary
smfile = image_prefix+'sU.image.tt0'
outfile = smfile
targetres = True
imsmooth()

default(imregrid)
imagename = smfile
template = im_lsb
rgfile = image_prefix+'.rgsmU.image.tt0'
output = rgfile
overwrite = True
imregrid()



exportfits(imagename = im_lsb, fitsimage = image_prefix+'.'+config+band+'.rgsmL.fits')
exportfits(imagename = rgfile, fitsimage = image_prefix+'.'+config+band+'.rgsmU.fits')
	



