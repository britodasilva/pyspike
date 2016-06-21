function handles = get_handles(samplingFrequency)
    handles.par.w_pre = 20;                     %number of pre-event data points stored (def. 20)
    handles.par.w_post = 44;                    %number of post-event data points stored (def. 44)
    % handles.par.detection = 'pos';            %type of threshold
    % handles.par.detection = 'neg';              %type of threshold
    handles.par.detection = 'both';           %type of threshold
    handles.par.stdmin = 5.00;                  %minimum threshold (def. 5)
    handles.par.stdmax = 50;                    %maximum threshold
    handles.par.interpolation = 'y';            %interpolation for alignment
    handles.par.int_factor = 2;                 %interpolation factor (def. 2)
    handles.par.detect_fmin = 300;              %high pass filter for detection (def. 300)
    handles.par.detect_fmax = 3000;             %low pass filter for detection (def. 3000)
    handles.par.sort_fmin = 300;                %high pass filter for sorting (def. 300)
    handles.par.sort_fmax = 3000;               %low pass filter for sorting (def. 3000)
    handles.par.segments = 1;                   %nr. of segments in which the data is cutted.
    handles.par.sr = samplingFrequency;                     %sampling frequency, in Hz (default 24000).
    min_ref_per = 1.5;                          %detector dead time (in ms)
    handles.par.ref = floor(min_ref_per ...
        *handles.par.sr/1000);                  %number of counts corresponding to the dead time
    return