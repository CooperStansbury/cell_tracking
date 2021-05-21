% TEST ImageStack =
% load_czi_data('G:\ImageProcessing\001_PreMitosisDetection\SampleData\BasicSplit.czi',{'AF514,'mCher','H3342'});

function ImageStack = load_czi_data(czipath, channelNames)
    addpath(genpath('/Applications/bfmatlab/'));
    addpath(genpath('G:\External_MATLAB\bfmatlab'));                       % install bioformats and update path
    % https://downloads.openmicroscopy.org/bio-formats/6.6.1/artifacts/bfmatlab.zip
    
    % AUTOMATED PROCESSING
    dbg=-1;   % handling for tiff/czi
    splt=strsplit(czipath,'.');
    xtz=splt{end};
    is_czi=isequal(xtz,'czi');        % is this a czi file
    
    data = bfopen(czipath);

    dt=data{1,1};
    cl=dt{1,2};
    splt=strsplit(cl,';');

    nm=splt{1+is_czi};                                                            % 2 --> 1 for tiff
    plane=double(string(regexprep(splt{2+is_czi},'.*/','')));                     % 3 --> 2 for tiff
    chan=double(string(regexprep(splt{3+is_czi},'.*/','')));                      % 4 --> 3 for tiff
    time=double(string(regexprep(splt{4+is_czi},'.*/','')));                      % 5 --> 4 for tiff

    fprintf("%s\n",nm);

    z=cell(time,chan);
    % assumes FOUR channels
    % extend to how to automatically extend the data
    %   green channel   (1)
    %   red channel     (2)
    %   blue channel    (3)
    %   oblique channel (4)

    T=table(dt(:,1),'VariableNames',{'PixelArray'});
    meta=dt(:,2);

    planes=regexprep(meta,'.*plane ','');
    planes=double(string((regexprep(planes,'/.*',''))));

    chans=regexprep(meta,'.*; C=','');
    chans=double(string((regexprep(chans,'/.*',''))));

    times=regexprep(meta,'.*; T=','');
    times=double(string((regexprep(times,'/.*',''))));
    dbg=-1;

    T.planes=planes;
    T.chans=chans;
    T.times=times;
    %{
    plane=double(string(regexprep(splt{3},'.*/','')));
    chan=double(string(regexprep(splt{4},'.*/','')));
    time=double(string(regexprep(splt{5},'.*/','')));
    %}
    for i=1:height(T)
        time=T.times(i);
        chan=T.chans(i);
        z{time,chan}=T.PixelArray{i};
    end

    ImageStack=cell2table(z);
    ImageStack.Properties.VariableNames=channelNames;
    dbg=-1;
    %{
    dbg=-1;
    pixelArrays=data{1,1};
    nplane=height(pixelArrays);
    nframe=nplane/4;

    green_idx=[1:4:nplane]';
    red_idx=[2:4:nplane]';
    blue_idx=[3:4:nplane]';
    oblq_idx=[4:4:nplane]';

    green_channel=pixelArrays(green_idx);
    red_channel=pixelArrays(red_idx);
    blue_channel=pixelArrays(blue_idx);
    oblq_channel=pixelArrays(oblq_idx);

    green_channel1=cell2table(green_channel,'VariableNames',{'PixelArray'});    % save
    red_channel1=cell2table(red_channel,'VariableNames',{'PixelArray'});        % save
    blue_channel1=cell2table(blue_channel,'VariableNames',{'PixelArray'});      % save
    oblq_channel1=cell2table(oblq_channel,'VariableNames',{'PixelArray'});      %(save)
    %}


    dbg=-1;
end