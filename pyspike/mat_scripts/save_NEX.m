function save_NEX(samplingFrequency, channels,startTime,name)
    
    
    %
    if length(channels) < 65
        nexFile1 = nexCreateFileData(samplingFrequency);
        for ii = 1:length(channels)
            fprintf('Channel %s, ', channels{ii})
            if mod(ii,5) == 0
                fprintf('\n')
            end
            eval(['load ' channels{ii} '.mat;']);
            nexFile1 = nexAddContinuous( nexFile1, startTime, samplingFrequency, data, channels{ii} );
            eval(['load ' channels{ii} '_spikes.mat;']);
            nexFile1 = nexAddNeuron(nexFile1,index(:)/100,[channels{ii} '_spk']);
            nexFile1 = nexAddWaveform(nexFile1,samplingFrequency,index(:)/100,1e3*spikes',[channels{ii} '_waveform']);
    %         eval(['load ' channels{ii} '_spikes.mat;']);
    %         if ~isempty(index)
    %             nexFile2 = nexAddWaveform(nexFile2,samplingFrequency,index(:)/100,1e3*spikes',channels{ii});
    %             fprintf('\n Writing spike file')
    %             writeNexFile(nexFile2,'Spikes.nex');
    %         end
            %fprintf('\n Done! \n')
        end
        fprintf('\n Writing continous file')
        writeNexFile(nexFile1,name);
    else
        name1 = [name(1:end-4) '_1.nex']
        nexFile1 = nexCreateFileData(samplingFrequency);
        for ii = 1:64
            fprintf('Channel %s, ', channels{ii})
%             if mod(ii,5) == 0
%                 fprintf('\n')
%             end
            try
                eval(['load ' channels{ii} '.mat;']);
                nexFile1 = nexAddContinuous( nexFile1, startTime, samplingFrequency, data, channels{ii} );
                eval(['load ' channels{ii} '_spikes.mat;']);
                nexFile1 = nexAddNeuron(nexFile1,index(:)/100,[channels{ii} '_spk']);
                nexFile1 = nexAddWaveform(nexFile1,samplingFrequency,index(:)/100,1e3*spikes',[channels{ii} '_waveform']);
                
            end
            clear data
        end
        fprintf('\n Writing continous file')
        writeNexFile(nexFile1,name1);
        clear nexFile1
        name2 = [name(1:end-4) '_2.nex']
        nexFile2 = nexCreateFileData(samplingFrequency);
        for ii = 65:length(channels)
            fprintf('Channel %s, ', channels{ii})
%             if mod(ii,5) == 0
%                 fprintf('\n')
%             end
            try
                eval(['load ' channels{ii} '.mat;']);
                nexFile2 = nexAddContinuous( nexFile2, startTime, samplingFrequency, data, channels{ii});
                eval(['load ' channels{ii} '_spikes.mat;']);
                nexFile2 = nexAddNeuron(nexFile2,index(:)/100,[channels{ii} '_spk']);
                nexFile2 = nexAddWaveform(nexFile2,samplingFrequency,index(:)/100,1e3*spikes',[channels{ii} '_waveform']);
            end
            clear data
        end
        fprintf('\n Writing continous file')
        writeNexFile(nexFile2,name2);
    end
return