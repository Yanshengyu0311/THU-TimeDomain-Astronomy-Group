from pyraf import iraf
import os
import sys
from call_Tools import check_remove

class IRAF():
    def __init__(self,
                 Keys,
                 cwd,
                 fxpix,
                 Bias,
                 Dark,
                 Flat,
                 trim,
                 overscan,
                 ):
            self.cwd = cwd
            self.Keys = Keys
            self.fxpix = fxpix
            self.Bias = Bias
            self.Dark = Dark
            self.Flat = Flat
            self.trim = trim
            self.overscan = overscan
    def process(self,
                image_input, 
                image_output,
                zero_combine_input,
                dark_combine_input,
                flat_combine_input,
                zero_combine_output,
                dark_combine_output,
                flat_combine_output,
                zero_correct_input,
                zero_correct_output,
                dark_correct_input,
                dark_correct_output,
                target_filter,
                zero_combine_done,
                ):
        
        Keys = self.Keys
        fxpix = self.fxpix
        Bias = self.Bias
        Dark = self.Dark
        Flat = self.Flat
        trim = self.trim
        overscan = self.overscan

        os.chdir(self.cwd)

        print('Loading IRAF packages ...')
        iraf.imred()
        iraf.ccdred()
        print('unlearning previous settings...')
        # iraf.ccdred.unlearn()
        iraf.ccdred.ccdproc.unlearn()
        iraf.ccdred.combine.unlearn()
        iraf.ccdred.flatcombine.unlearn()
        iraf.ccdred.zerocombine.unlearn()
        iraf.ccdred.darkcombine.unlearn()

        iraf.ccdred.ccdproc.ccdtype = ""
        iraf.ccdred.ccdproc.zerocor = False
        iraf.ccdred.ccdproc.flatcor = False
        iraf.ccdred.ccdproc.fixpix  = False
        iraf.ccdred.ccdproc.oversca = False
        iraf.ccdred.ccdproc.trim    = False
        iraf.ccdred.ccdproc.darkcor = False


        if fxpix:
            iraf.ccdred.ccdproc.fixpix  = False
            iraf.ccdred.ccdproc.fixfile = Keys["fixpix"]
        if Bias:
            if not zero_combine_done:
                # combine flat images
                print('Combining bias images ...')
                print(zero_combine_output)
                check_remove(zero_combine_output)
                iraf.ccdred.zerocombine.ccdtype = ''
                # iraf.ccdred.zerocombine.process = 'no'
                iraf.ccdred.zerocombine.process = False
                iraf.ccdred.zerocombine.reject  = 'avsigclip'
                iraf.ccdred.zerocombine.combine = "average"
                iraf.ccdred.zerocombine.rdnoise = Keys['rdnoise']
                iraf.ccdred.zerocombine.gain    = Keys["gain"]
                iraf.ccdred.zerocombine.output  = zero_combine_output
                iraf.ccdred.zerocombine(input="@"+zero_combine_input)
                zero_combine_done=True
            # iraf.ccdred.zerocombine(input=",".join(bb_all))

            iraf.ccdred.ccdproc.zerocor = True
            iraf.ccdred.ccdproc.zero    = zero_combine_output
            iraf.ccdred.ccdproc(images="@"+zero_correct_input,
                                output="@"+zero_correct_output)
        if Dark:
            print('Combining dark images ...')
            check_remove("@"+dark_correct_input)
            check_remove(dark_combine_output)

            iraf.ccdred.darkcombine.ccdtype = ''
            # iraf.ccdred.flatcombine.process = 'no'
            iraf.ccdred.darkcombine.process = False
            iraf.ccdred.darkcombine.reject  = 'avsigclip'
            iraf.ccdred.darkcombine.combine = "average"
            iraf.ccdred.darkcombine.rdnoise = Keys['rdnoise']
            iraf.ccdred.darkcombine.gain    = Keys["gain"]
            iraf.ccdred.darkcombine.output  = dark_combine_output
            iraf.ccdred.darkcombine(input="@"+dark_combine_input)
            iraf.ccdred.ccdproc.darkcor     = True
            iraf.ccdred.ccdproc.dark        = dark_combine_output
            iraf.ccdred.ccdproc(images="@"+dark_correct_input,
                                output="@"+dark_correct_output)
        if Flat:
            print('Combining flat images ...')
            # check_remove("@"+flat_combine_output)
            check_remove(flat_combine_output)
            # TODO flat_cor_output name
            print(target_filter,flat_combine_input,flat_combine_output)
            iraf.ccdred.flatcombine.ccdtype = ''
            iraf.ccdred.flatcombine.scale   = 'mode'
            # iraf.ccdred.flatcombine.process = 'no'
            iraf.ccdred.flatcombine.process = False
            iraf.ccdred.flatcombine.reject  = 'avsigclip'
            iraf.ccdred.flatcombine.combine = "median"
            iraf.ccdred.flatcombine.rdnoise = Keys['rdnoise']
            iraf.ccdred.flatcombine.gain    = Keys["gain"]
            iraf.ccdred.flatcombine.output  = flat_combine_output
            iraf.ccdred.flatcombine(input="@"+flat_combine_input)
            iraf.ccdred.ccdproc.flatcor     = True
            iraf.ccdred.ccdproc.flat        = flat_combine_output  

        if trim:
            iraf.ccdred.ccdproc.trim    = True
            iraf.ccdred.ccdproc.trimsec = Keys["trimsec"]
        
        if overscan:
            iraf.ccdred.ccdproc.oversca = True
            iraf.ccdred.ccdproc.biassec = Keys["biassec"]
        check_remove(image_output)
        iraf.ccdred.ccdproc(images=image_input,output=image_output)
        print('--- DONE ---')
        # return zero_combine_done,flat_combine_done