# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 17:05:54 2015

@author: anderson
"""

import numpy as np
from copy import copy
from npyhfo import DataObj,EventList,Timer
from read_header import read_header
import os
import matlab.engine
import scipy.io as sio
import shutil
import h5py
import sys
import scipy.signal as sig

def getFileList(folder):
    filelist = os.listdir(folder)
    label_amp = [f for f in filelist if f.startswith('amp') and f.endswith('.dat')]
    label_amp.sort()
    label_ADC = [f for f in filelist if f.startswith('board-ADC') and f.endswith('.dat')]
    label_ADC.sort()
    label_aux = [f for f in filelist if f.startswith('aux') and f.endswith('.dat')]
    label_aux.sort()
    label_vdd = [f for f in filelist if f.startswith('vdd') and f.endswith('.dat')]
    label_vdd.sort()
    label_info = [f for f in filelist if f.startswith('info') and f.endswith('.rhd')]
    label_info.sort()
    label_time = [f for f in filelist if f.startswith('time') and f.endswith('.dat')]
    label_time.sort()
    dic_labels = {'amp':label_amp, 'adc':label_ADC, 'aux':label_aux, 'vdd':label_vdd, 'info':label_info, 'time':label_time}
    return dic_labels

def openDATfile(filename,ftype,srate=25000):
    fh = open(filename,'r')
    fh.seek(0)
    if ftype == 'amp':
        data = np.fromfile(fh, dtype=np.int16)
        fh.close()
        data = np.double(data)
        data *= 0.195 # according the Intan, the output should be multiplied by 0.195 to be converted to micro-volts
    elif ftype == 'adc':
        data = np.fromfile(fh, dtype=np.uint16)
        fh.close()
        data = np.double(data)
        data *= 0.000050354 # according the Intan, the output should be multiplied by 0.195 to be converted to micro-volts
        data -= np.mean(data)
    
    elif ftype == 'aux':
        data = np.fromfile(fh, dtype=np.uint16)
        fh.close()
        data = np.double(data)
        data *= 0.0000748 # according the Intan, the output should be multiplied by 0.195 to be converted to micro-volts
        
    elif ftype == 'time':
        data = np.fromfile(fh, dtype=np.int32)
        fh.close()
        data = np.double(data)
        data /= srate # according the Intan, the output should be multiplied by 0.195 to be converted to micro-volts
    return data

def loadITANfolder(folder,save_folder = None,q=25):
    with Timer.Timer(folder):
        if type(save_folder) is 'NoneType':
           save_folder = folder  
        save_file = save_folder + folder[-14:-1] + '.nex'
        #get files in the folder
        files = getFileList(folder)
        # load info
        fid = open(folder+files['info'][0], 'rb')
        info = read_header(fid)
        sys.stdout.flush()
        #Sampling Rate
        sample_rate = info['sample_rate']
        time_vec = openDATfile(folder+files['time'][0],'time',sample_rate)
        time_vec = time_vec[0:-1:q]
        amp_unit = '$\mu V$'
        labels = []
        nch = len(files['amp']) + len(files['adc']) # +len(files['aux'])
        data = np.zeros([time_vec.shape[0],nch])
        eng = matlab.engine.start_matlab()
        eng.cd(folder,nargout=0)
        count = 0
        for f in files['amp']:
            sys.stdout.flush()
            with Timer.Timer(f):     
                name = f[:-4]
                labels.append(name)
                aux_data = openDATfile(folder+f,'amp',sample_rate)
                data[:,count] = sig.decimate(aux_data,q)
                count +=1
                if os.path.isfile(folder+name+'.mat'):
                    continue
                tfile = open(folder + 'Files.txt', 'w')
                tfile.write(name +'\n')
                tfile.close()
                sio.savemat(folder+name+'.mat', {'data':aux_data})
                eng.Get_spikes_alt(sample_rate,nargout=0)
                eng.close('all', nargout=0)
        eng.save_NEX(sample_rate,labels,int(time_vec[0]),save_file,nargout=0)
        for f in files['adc']:
            sys.stdout.flush()
            with Timer(f):  
                labels.append(f[:-4])
                aux_data = openDATfile(folder+f,'adc',sample_rate)
                data[:,count] = sig.decimate(aux_data,q)
                count +=1
        Data = DataObj(data,sample_rate/q,amp_unit,labels,time_vec,[])
    Data.save(folder+'downsampled.h5','data')
    eng.quit()    
    return Data