% e.g. AnnotateTracks=annotate_tracks(ImageStack,TrackSpots,437.37/640);
%      eventually have to add x/y scaling
% channelNames should be in 'R','G','B' order

function AnnotatedTracks=annotate_tracks(ImageStack,TrackSpots,pixelSize,channelNames)
    %disp('annotate_tracks');

    %{'Oblique','AF514','mCher','H3342'};

    %load('WH02_Single.mat')
    %load('T.mat');

    %load('MR34_CenterFrame.mat');                                              % image stack
    %load('ImageStack.mat');
    %load('basic_track_info.mat');
    %load('spotTable1.mat');
    %load('spotTable.mat');
    %matStack=MR34_CenterFrame;                                                % data structure for matlab image stack (Zeiss)
    matStack=ImageStack;
    T=TrackSpots;
    %T=basic_track_info;                                                        % data structure for matlab tracks (ImageJ)

    %sf=68.34 / 100;                                                            % scale factor from zeiss (monitor pixels / image pixel)

    nv=height(T);
    T.BlueSignal=zeros(nv,1);
    T.GreenSignal=zeros(nv,1);
    T.RedSignal=zeros(nv,1);
    

    RedName=channelNames{1};
    GreenName=channelNames{2};
    BlueName=channelNames{3};

    for i=1:nv
        try
            FRAME=T.Frame(i);                                                  % 0 based indexing in ImageJ
            POSITION_X=round(T.ScreenX(i)/pixelSize)+1;                        % y,x inverted to further avoid confustion (may need to resolve this later)
            POSITION_Y=round(T.ScreenY(i)/pixelSize)+1;

            redInfo=matStack.(RedName){FRAME};                                 % these have to become variables also (at some point)
            greenInfo=matStack.(GreenName){FRAME};                             % green
            blueInfo=matStack.(BlueName){FRAME};                               % red

            T.RedSignal(i)=redInfo(POSITION_Y,POSITION_X);                     % save T
            T.GreenSignal(i)=greenInfo(POSITION_Y,POSITION_X);
            T.BlueSignal(i)=blueInfo(POSITION_Y,POSITION_X);
        catch ME
            fprintf("%d\n",i);
        end
        
    end
    
    AnnotatedTracks=T;
end