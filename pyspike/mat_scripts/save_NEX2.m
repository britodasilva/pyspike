function save_NEX2(samplingFrequency, channels,startTime)
    nexFile = nexCreateFileData(samplingFrequency);
    for ii = 1:length(channels)
        fprintf('Channel %s, ', channels{ii})
        if mod(ii,5) == 0
            fprintf('\n')
        end
        
        
        fprintf('\n Writing file')
        writeNexFile(nexFile,'Continuous.nex');
        fprintf('\n Done! \n')
    end
return