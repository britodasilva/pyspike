# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 17:05:54 2015

@author: anderson
"""

import numpy as np
from copy import copy
from pyhfo import DataObj,EventList, SpikeObj

def open_file_DAT(folder,ports,nchans,srate,bsize=None,starttime = 0):
    if bsize == None:
        bsize = srate
    nch = sum(nchans)
    data = np.zeros([bsize,nch])
    count = 0
    labels = []
    
    for p in range(len(ports)):
        root =  'amp-'+ports[p]+'-'
        for ch in range(nchans[p]):
            x = str(ch)
            while len(x)<3:
                x = '0' + x
            fname = root + x + '.dat'
            labels.append(fname)
            fh = open(folder+fname,'r')
            fh.seek(np.round(starttime*srate)*2)
            data[:,count] = np.fromfile(fh, dtype=np.short, count=bsize)
            count +=1
            fh.close()
    data *= 0.195 # according the Intan, the output should be multiplied by 0.195 to be converted to micro-volts
    amp_unit = '$\mu V$'
    # Time vector   
    n_points  = data.shape[0]
    end_time  = n_points/srate
    time_vec  = np.linspace(0,end_time,n_points,endpoint=False)
    
    Data = DataObj(data,srate,amp_unit,labels,time_vec,[])
    return Data
    
    
def pca2(data):

    npoint,ch = data.shape
    Mn = np.mean(data,0)
    for i in range(ch):
        data[:,i] = data[:,i] - Mn[i]
    
    C = np.cov(data.T)
    a1 = np.zeros(ch)
    a2 = np.zeros(ch)
    #art1 = np.zeros(npoint)
    
    #art2 = np.zeros(npoint)
    pcadata = np.zeros([npoint,ch])
    for i in range(ch):
        j = [x for x in range(ch) if x is not i]
        noti = data[:,j]
        Cnoti = C[np.ix_(j,j)]
        w,d = np.linalg.eig(Cnoti)
        k = np.argsort(w)
        d = d[k]
        v = np.identity(ch-1)*w
        v = v[k]
        v= v[:,-2:]
        pc = np.dot(noti,v)
        pc = np.append(pc,data[:,i][...,None],1)
        Cpc = np.cov(pc.T)

        a1[i] = Cpc[0,2]/Cpc[0,0]
        a2[i] = Cpc[1,2]/Cpc[1,1]
        #art1 += a1[i]*pc[:,0]
        #art2 += a2[i]*pc[:,1] 
        pcadata[:,i] = data[:,i] - a1[i]*pc[:,0] - a2[i]*pc[:,1] 
    #art1 /= ch
    #art2 /= ch
    #pca12 = np.append(art1[...,None],art2[...,None],1)
    
    return pcadata

def FindBigStuff(data,xsd =2.5):
    
    s = np.std(data,0) * xsd
    #print s
    spikelist = np.array([0,0,0])[None,...]
    m,n = data.shape
   
    for i in range(n):
        
        x = data[:,i]
        taux = np.diff(np.where(abs(x)>s[i],1,0))
        times = np.nonzero(taux==1)[0]
        times2 = np.nonzero(taux==-1)[0]
        if len(times) !=0:
            if len(times)-1 == len(times2):
                times2 = np.append(times2,m)
            elif len(times) == len(times2)-1:
                times = np.append(0,times)
            chs = np.ones(times.shape)*i
            aux = np.append(chs[...,None],times[...,None],1)   
            aux = np.append(aux,times2[...,None],1)  
            spikelist = np.append(spikelist,aux,0)
    return np.delete(spikelist, (0), axis=0),s

def ReplaceBigStuff(data,biglist,replacearray,postpts = 10,prepts = 10):
    NoSpikesData = copy(data)
    for ch,atime,btime in biglist:
        if atime - prepts > 0:
            a = prepts
        else:
            a = atime-1
        if btime + postpts < data.shape[0]:
            b = postpts
        else:
            b = data.shape[0] - btime
        NoSpikesData[int(atime-a):int(btime+b),int(ch)] = replacearray[int(atime-a):int(btime+b),int(ch)]
    return NoSpikesData
    
    
def clearData(Data,ptspercut,postpts = 10,prepts = 10):
    data = Data.data
    m,n = data.shape
    if n>m:
        data = data.T
        m,n = data.shape
    last = m/ptspercut
    cleared = copy(data)
    for ci in range(last):
        if (ci+1)*ptspercut > m:
            stop = m
        else:
            stop = (ci+1)*ptspercut
        start = ci * ptspercut
        tdata = data[np.arange(start, stop),:,]
        
        
        pcadata = pca2(tdata)
        noiseEst = tdata - pcadata
        biglist,s = FindBigStuff(pcadata)
        replacearray = np.zeros(tdata.shape)
        NoSpikesData = ReplaceBigStuff(tdata,biglist,replacearray,postpts,prepts)
        
        pcadata = pca2(NoSpikesData)
        noiseEst = NoSpikesData - pcadata
        replacearray = noiseEst
        NoSpikesData = ReplaceBigStuff(tdata,biglist,replacearray,postpts,prepts)
        pcadata = pca2(NoSpikesData)
        cleared[np.arange(start, stop),:,] = tdata - pcadata
    Cleared = DataObj(cleared,Data.sample_rate,Data.amp_unit,Data.ch_labels,Data.time_vec,[])
    
    return Cleared
    
def GetSpike(Data,xsd=1,postpts = 10,prepts = 10):
    biglist,ths = FindBigStuff(Data.data,xsd =xsd)
    Spikes = EventList(Data.ch_labels,(Data.time_vec[0],Data.time_vec[-1]))     
    for ch,a,b in biglist:
        if a - prepts > 0:
            pass
        else:
            continue
        if b + postpts < Data.data.shape[0]:
            pass
        else:
            continue
        
        aux = Data.data[int(a-prepts):int(b+postpts),int(ch)]
        
        #aux_idx = atime-a + np.argmax(abs(aux)) 
        aux_idx = a-prepts + np.nonzero(abs(aux) > ths[int(ch)])[0][0]
          
        waveform = Data.data[int(aux_idx-prepts):int(aux_idx+postpts),int(ch)]
        if waveform.shape[0] != postpts+prepts:
            continue
        tstamp = aux_idx/Data.sample_rate
        clus = ch
        feat = 0
        spk = SpikeObj(waveform,tstamp,clus,feat)
        Spikes.__addEvent__(spk)
    return Spikes,ths