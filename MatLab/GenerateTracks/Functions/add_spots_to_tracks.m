% e.g.
% trackpath='G:\ImageProcessing\CurveFitting\BasicMerging\Test1.xml';
% spotpath='G:\ImageProcessing\CurveFitting\BasicMerging\Test1.csv';
% trackspots=add_spots_to_tracks(trackpath,spotpath);
function TrackSpots=add_spots_to_tracks(trackpath,spotpath,channelColors)
    addpath('C:\Users\umich\Downloads\fiji-win64\Fiji.app\scripts');
    addpath('/Applications/Fiji.app/scripts/');
    % install ImageJ Fiji and update path
    % https://imagej.net/Fiji.html#Downloads
    
    %[tracks, metadata] = importTrackMateTracks('Test1.xml');
    [tracks, metadata] = importTrackMateTracks(trackpath);

    %spots=readtable('Test1.csv');
    spots=readtable(spotpath);

    nt=length(tracks)

    %T=table('VariableNames',{'Track','Frame','ScreenX','ScreenY'});
    z=zeros(1,4);
    for i=1:nt
        track=tracks{i,1};
        tk=track(:,1:3);
        tk(:,1)=tk(:,1)+1;
        col=i*ones(size(tk,1),1);
        dbg=-1;
        apnd=[col tk];
        z=[z;apnd];
    end
    z=z(2:end,:);
    op=array2table(z,'VariableNames',{'Track','Frame','ScreenX','ScreenY'});

    % TRACK_ID and FRAMES from spots to annotate

    spots=spots(~ismissing(spots.TRACK_ID),:);
    spots.TRACK_ID=spots.TRACK_ID+1;                                           % all 0 based to 1 based
    spots.FRAME=spots.FRAME+1;                                                 % all 0 based to 1 based
    [C, ia, ic]=unique(spots.TRACK_ID);
    spots.TRACK_ID=ic;                                                            % extra extra fancy



    % height(spots)==height(op)
    diameter=zeros(height(op),1);
    MeanGreen=zeros(height(op),1);                                         % added field
    MeanRed=zeros(height(op),1);                                           % added field
    MeanBlue=zeros(height(op),1);                                          % added field
    op.Diameter=diameter;
    op.MeanBlueSignal=MeanBlue;                                                  % added field
    op.MeanGreenSignal=MeanGreen;                                                % added field
    op.MeanRedSignal=MeanRed;                                                    % added field

    red_id='';
    green_id='';
    blue_id='';
    
    for i=1:length(channelColors)
        cid=channelColors{i};
        switch(cid)
            case 'R'
                red_id=sprintf("MEAN_INTENSITY%02d",i);
            case 'G'
                green_id=sprintf("MEAN_INTENSITY%02d",i);
            case 'B'
                blue_id=sprintf("MEAN_INTENSITY%02d",i);
        end
    end
    % guarantted there is a fancier/nicer way to do this using table joins
    for i=1:height(spots)
        TRACK_ID=spots.TRACK_ID(i);
        FRAME=spots.FRAME(i);
        DIAMETER=spots.ESTIMATED_DIAMETER(i);
        %MEAN_INTENSITY01=spots.MEAN_INTENSITY01(i);   % added field
        %MEAN_INTENSITY02=spots.MEAN_INTENSITY02(i);   % added field
        %MEAN_INTENSITY03=spots.MEAN_INTENSITY03(i);   % added field
        RED_INTENSITY=spots.(red_id)(i);
        GREEN_INTENSITY=spots.(green_id)(i);
        BLUE_INTENSITY=spots.(blue_id)(i);

        idx_T=ismember(op.Track,TRACK_ID);
        idx_F=ismember(op.Frame,FRAME);
        idx=logical(idx_T & idx_F);
        if(nnz(idx)==1)
            op.Diameter(idx)=DIAMETER;
            %op.MeanBlueSignal(idx)=MEAN_INTENSITY01;  % added field
            %op.MeanGreenSignal(idx)=MEAN_INTENSITY02;    % added field
            %op.MeanRedSignal(idx)=MEAN_INTENSITY03;   % added field
            op.MeanRedSignal(idx)=RED_INTENSITY;
            op.MeanGreenSignal(idx)=GREEN_INTENSITY;
            op.MeanBlueSignal(idx)=BLUE_INTENSITY;
        else
            dbg=-1
        end
    end
    
    TrackSpots=op;
end







