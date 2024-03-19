function results = read_rxs_log(filename, maxCSINumber)
%read_rxs_log Parse PicoScenes generated .csi file using mex function RXSParser.
%   It invokes the mex function RXSParser to decode the data entries.
%   RXSParser will be automatically compiled, if the mex function does not exist.
%
    if nargin < 2
        maxCSINumber = intmax;
    end

    if exist('RXSParser', 'file') ~= 3
        compileRXSParser
    end
    
    if exist('RXSParser', 'file') ~= 3
        error('RXSParer compilation fails');
    end
    
    ticStart = tic;
    fp = fopen(filename, 'rb');
    if (fp < 0)
        error('Cannot open file %s', filename);
    end

    resultBatchSize = 10000;
    results = cell(resultBatchSize, 1);
    count = 1;

    % find maximal csi dimensions
    max_csi_dimensions = determine_csi_dimensions(fp, maxCSINumber)
    
    while ~feof(fp) && count <= maxCSINumber
        segmentLength = fread(fp, 1, 'uint32') + 4;
        if isempty(segmentLength)
            break;
        end
        fseek(fp, -4, 'cof');
        bytes=fread(fp, segmentLength,'uint8=>uint8');
        csi_entry = RXSParser(bytes);
        for i = 1:numel(csi_entry)
            csi_entry(i).MPDU = {csi_entry(i).MPDU};
        end
        if isempty(csi_entry) % in very rare case, the data is corrupted.
            continue;
        end

        % check that this frame's csi matrix dimensions are maximal
        % to always enable bundled parsing
        % replace with the previous frame if not, or skip if is first frame
        if ~isequal(size(csi_entry.CSI.CSI), max_csi_dimensions)
            if count ~= 1
                csi_entry = results{count - 1};
            else
                continue
            end
        end
        
        if count == numel(results)
            results = [results; cell(resultBatchSize, 1)];
        end

        results{count} = csi_entry;
        count = count + 1;
    end
    results(count:end)= [];

    disp([num2str(length(results)) ' PicoScenes frames are decoded in ' num2str(toc(ticStart)) ' seconds.']);
    fclose(fp);
    end
