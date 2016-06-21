% PROGRAM Get_spikes.
% Gets spikes from all files in Files.txt.
% Saves spikes and spike times.
function Get_spikes_alt(samplingFrequency)
    handles = get_handles(samplingFrequency);
    files = textread('Files.txt','%s');

    for k= 1:length(files)
        tic
        file_to_cluster = files(k)
        index_all=[];
        spikes_all=[];
        for j=1:handles.par.segments        %that's for cutting the data into pieces
            % LOAD CONTINUOUS DATA
            eval(['load ' char(file_to_cluster) ';']);
            tsmin = (j-1)*floor(length(data)/handles.par.segments)+1;
            tsmax = j*floor(length(data)/handles.par.segments);
            x=data(tsmin:tsmax); clear data; 

            % SPIKE DETECTION WITH AMPLITUDE THRESHOLDING
            [spikes,~,index]  = amp_detect(x,handles);       %detection with amp. thresh.
            index=index+tsmin-1;

            index_all = [index_all index];
            spikes_all = [spikes_all; spikes];
        end
        index = index_all *1e3/handles.par.sr;                  %spike times in ms.
        spikes = spikes_all;
        eval(['save ' char(file_to_cluster) '_spikes.mat spikes index']);    %saves Sc files
        digits=round(handles.par.stdmin * 100);
        nfile=[char(file_to_cluster) '_sp_th.mat' num2str(digits)];
        eval(['save ' nfile ' spikes index']);    %save files for analysis
        toc
    end   
return