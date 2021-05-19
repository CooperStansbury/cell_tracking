% basic startup stuff
disp('calling script');
clc
close all
restoredefaultpath

% working direcotry path
addpath('Functions');
addpath("/Applications/");

% user input
datapath='Datasets/cooper_test/';   % UPDATE
[czipath, spotpath, trackpath]=getDataPaths(datapath);

% may be able to parse this information from the .ome.tiff file
channelColors={'G','R','B'};                                               
channelNames={'AF514','mCher','H3342'};
channelNamesRGB=sort_channels(channelColors,channelNames);

% image J saves screen pixels, we need to know this number to convert back to indexed pixels
% it varies from experiment to experiment (has to do with the focus of the microscope)
% would be extremely useful if there was a way to parse this from the .ome.tiff
PixelSize=0.6834;                                                                                                             

% basic data
ImageStack = load_czi_data(czipath,channelNames);
TrackSpots = add_spots_to_tracks(trackpath,spotpath,channelColors);
T=annotate_tracks(ImageStack,TrackSpots,PixelSize,channelNamesRGB);

% basic plot
very_basic_plot(T);


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









