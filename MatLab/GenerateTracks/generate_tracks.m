% basic startup stuff
disp('calling script');
clc
close all
restoredefaultpath

% working direcotry path
addpath('Functions');

% user input
datapath='../Inputs/';   % UPDATE
outpath='../Outputs/test.csv';
[czipath, spotpath, trackpath]=getDataPaths(datapath);

% may be able to parse this information from the .ome.tiff file
channelColors={'G','R','B'};                                               
channelNames={'AF514','mCher','H3342'};
channelNamesRGB=sort_channels(channelColors,channelNames);

% image J saves screen pixels, we need to know this number to convert back to indexed pixels
% it varies from experiment to experiment (has to do with the focus of the microscope)
% would be extremely useful if there was a way to parse this from the .ome.tiff
PixelSize=0.6834                                                                                                             

% basic data
ImageStack = load_czi_data(czipath,channelNames);
TrackSpots = add_spots_to_tracks(trackpath,spotpath,channelColors);
T=annotate_tracks(ImageStack,TrackSpots,PixelSize,channelNamesRGB);

% save the normalized T structure to file
writetable(T, outpath)

% % remove background averages (each channel)
% % fine to comment these lines out during development
% ZStack = get_seg_info(ImageStack,channelNamesRGB);
% Tn=normalize_stack(T,ZStack,channelNamesRGB);

% basic plot
% very_basic_plot(T);


function T = normalize_stack(T,ZStack,channelNamesRGB)
    T.MeanBlueSignal_Norm=T.MeanBlueSignal;
    T.MeanGreenSignal_Norm=T.MeanGreenSignal;
    T.MeanRedSignal_Norm=T.MeanRedSignal;
    
    redName=channelNamesRGB{1};
    greenName=channelNamesRGB{2};
    blueName=channelNamesRGB{3};
    
    for i=1:height(ZStack)
        t_idx=(T.Frame==i);
        z_idx=(ZStack.Frame==i);
        T.MeanBlueSignal_Norm(t_idx)=T.MeanBlueSignal_Norm(t_idx)-ZStack.(blueName)(z_idx);
        T.MeanGreenSignal_Norm(t_idx)=T.MeanGreenSignal_Norm(t_idx)-ZStack.(greenName)(z_idx);
        T.MeanRedSignal_Norm(t_idx)=T.MeanRedSignal_Norm(t_idx)-ZStack.(redName)(z_idx);
    end
end

% generate path to files for platform
function [czipath, spotpath, trackpath] = getDataPaths(dirname)
    dc=dir(dirname);
    tiffinfo=dir([dirname,'/*.tiff']);
    csvinfo=dir([dirname,'/*.csv']);
    xmlinfo=dir([dirname,'/*.xml']);
    czipath=[tiffinfo.folder,'/',tiffinfo.name];
    spotpath=[csvinfo.folder,'/',csvinfo.name];
    trackpath=[xmlinfo.folder,'/',xmlinfo.name];
end


function channelNamesRGB=sort_channels(channelColors,channelNames)
    channelNamesRGB={'','',''};
    for i=1:length(channelColors)
        channelColor=channelColors{i};
        switch(channelColor)
            case 'R'
                channelNamesRGB{1}=channelNames{i};
            case 'G'
                channelNamesRGB{2}=channelNames{i};
            case 'B'
                channelNamesRGB{3}=channelNames{i};
        end
    end
end

function very_basic_plot(T)
    
    % prepare figure
    figure;
    hold on;
    
    % loop through frames
    minframe=min(T.Frame);
    maxframe=max(T.Frame);
    for frame=minframe:maxframe
        idx=(T.Frame==frame);
        X=T.ScreenX(idx);
        Y=T.ScreenY(idx);
        scatter(X,Y,'b.');
        pause(0.2);
    end
    
    hold off;
end









