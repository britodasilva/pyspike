function SLE = get_SLE(data,samplingFrequency)
    SLE = [];
    npoints = length(data);
    time_vec = linspace(0,npoints/samplingFrequency,npoints);
    fmin_detect = 1;
    fmax_detect = 40;
    [b,a]=ellip(2,0.1,40,[fmin_detect fmax_detect]*2/samplingFrequency);
    d_data=filtfilt(b,a,data);
    noise_std_detect = median(abs(d_data))/0.6745;
    ths = 4*noise_std_detect;
    ths = abs(ths);
    ini= find(diff(abs(d_data)>ths)==1)+1;
    fim = find(diff(abs(d_data)>ths)==-1);
    event_idx = [];

    start_ix = time_vec(ini);
    end_ix = time_vec(fim);
    if length(start_ix)> length(end_ix)
        start_ix(end) = [];
    elseif length(end_ix) > length(start_ix)
        end_ix(1) = [];
    end
    if length(start_ix) > 0
        if end_ix(1)-start_ix(1) < 0
            end_ix(1) = [];
            start_ix(end) = [];
        end
        if length(start_ix) > 0
            to_exclude = [];
            to_exclude = find(start_ix(2:end)-end_ix(1:end-1) < 3); % find index of events separeted by less the minimal interval
            start_ix(to_exclude + 1) = []; % removing
            end_ix(to_exclude) = []; % removing
            if length(start_ix) > 0
                to_exclude = [];
                to_exclude = find(end_ix-start_ix < 20);
                start_ix(to_exclude) = [];
                end_ix(to_exclude) = [];
            end
        end
    end
    c = 0;

    for ii = 1:length(start_ix)
        c = c+1;
        SLE(c).start_time = start_ix(ii);
        SLE(c).end_time = end_ix(ii);
    end
