function dimensions = determine_csi_dimensions(fp, maxCSINumber)
    count = 1;
    numTones = 0;
    numRx = 0;
    numSts = 0;

    while ~feof(fp) && count <= maxCSINumber
        segmentLength = fread(fp, 1, 'uint32') + 4;
        if isempty(segmentLength)
            break;
        end
        fseek(fp, -4, 'cof');
        bytes=fread(fp, segmentLength,'uint8=>uint8');
        csi_entry = RXSParser(bytes);
        if isempty(csi_entry) 
            continue;
        end

        if csi_entry.CSI.NumTones > numTones
            numTones = csi_entry.CSI.NumTones;
        end
        
        if csi_entry.RxSBasic.NumSTS > numSts
            numSts = csi_entry.RxSBasic.NumSTS;
        end

        if csi_entry.CSI.NumRx > numRx
            numRx = csi_entry.CSI.NumRx;
        end
        
        count = count + 1;
    end

    dimensions = [numTones, numSts, numRx];
    fseek(fp, 0, 'bof');
end