function zstack=get_seg_info(ImageStack,channelNamesRGB)

    %{
    disp('blue_tracker_video');
    close all
    clearvars -except ImageStack

    addpath('zeiss_walter_suggested');                                         % pc2


    channelNamesRGB={'mCher','AF514','H3342'};                                 % red/green/blue

    if ~exist('ImageStack','var')
    load('ImageStack4');
    ImageStack=ImageStack4;
    clear ImageStack4
    end
    %}
    %{
    clearvars -except blue_channel red_channel green_channel;

    if ~exist('blue_channel','var')
        %load('E:\Zeiss\Data\WalterSuggestScenes\orig\blue_channel.mat');            % pc1 - SEAN: update path
        load('blue_channel.mat');                                              % pc2
    end

    if ~exist('green_channel','var')
        %load('E:\Zeiss\Data\WalterSuggestScenes\orig\green_channel.mat');           % pc1 - SEAN: update path
        load('green_channel.mat');                                             % pc2
    end

    if ~exist('red_channel','var')
        %load('E:\Zeiss\Data\WalterSuggestScenes\orig\red_channel.mat');             % pc1 - SEAN: update path
        load('red_channel.mat');                                               % pc2
    end
    %}

    zstack=-1;
    dbg1=-1;
    redName=channelNamesRGB{1};
    greenName=channelNamesRGB{2};
    blueName=channelNamesRGB{3};

    %blue_filt=0.8;
    blob_size=200;
    sleep_time=22;

    %red_filt=0.5;
    %green_filt=0.5;

    % temp to validate z-stack
    %nr=size(ImageStack.(blueName){1},1);
    %nc=size(ImageStack.(blueName){1},2);
    %zstack=zeros(nr,nc,height(ImageStack));                                  % new stuff
    
    dt=zeros(height(ImageStack),3);
    dt=array2table(dt,'VariableNames',channelNamesRGB);
    dbg3=-2;

    for i=1:height(ImageStack)

        %raw_blue=double(blue_channel.PixelArray{i});
        %raw_green=double(green_channel.PixelArray{i});
        %raw_red=double(red_channel.PixelArray{i});

        %raw_blue=mat2gray(blue_channel.PixelArray{i},[0 2^14-1]);
        %raw_green=mat2gray(green_channel.PixelArray{i},[0 2^14-1]);
        %raw_red=mat2gray(red_channel.PixelArray{i},[0 2^14-1]);
        raw_blue=ImageStack.(blueName){i};
        raw_green=ImageStack.(greenName){i};
        raw_red=ImageStack.(redName){i};


        % basic data info
        nr=size(raw_blue,1);
        nc=size(raw_blue,2);

        scaled_blue=minmax_scale(raw_blue,2.25);
        scaled_green=minmax_scale(raw_green,2.25);
        scaled_red=minmax_scale(raw_red,2.25);
        % add matlab histrogram to normalize the data
        % change from caxis property

        %{
            % histogram thresholds
            blue_thr=2319;
            green_thr=4726;
            red_thr=1983;
            %red_thr=1983*2;

            % filter out the images
            filt_blue=basic_hist_filt(raw_blue,blue_thr);
            filt_green=basic_hist_filt(raw_green,green_thr);
            filt_red=basic_hist_filt(raw_red,red_thr);

            filt_green(filt_green < green_filt)=0;
            filt_green(filt_green < green_filt)=0;

            %filt_green(filt_green < green_filt)=filt_green(filt_green < green_filt)./2;
            %filt_red(filt_red < red_filt)=filt_red(filt_red < red_filt)./2;
        %}
        scaled_green(scaled_green < 0.5)=0;
        scaled_red(scaled_red < 0.5)=0;
        %{
        filt_img=raw_blue./thr;
        filt_img(filt_img>1)=1;
        %}

        %{
        img=imshow(filt_img);

        I2=imadjust(filt_img);
        img2=imshow(I2);

        %}

        % NEED STREL LINE
        se = strel('disk',30);
        background = imopen(scaled_blue,se);

        I2=scaled_blue - background;


        I3=imadjust(I2);
        %BW=imbinarize(I2,blue_filt);                                                % change from 0.8 to 0.95
        BW=imbinarize(I3);
        %img3=imshow(BW);
        %I3(I3<0.6)=0;
        %img3=imshow(I3);
        BW2=bwareaopen(BW,blob_size);                                                % remove small objects (change from 30 to 100)
        cc=bwconncomp(BW2);
        stats=regionprops(cc);
        
        imshow(BW2);
        pause(.25);
        idx=~BW2;
        dt{i,blueName}=median(raw_blue(idx));
        dt{i,greenName}=median(raw_green(idx));
        dt{i,redName}=median(raw_red(idx));
        dbg4=-2;
        %{
        % all at the same time
        all_pids=[];
        z=zeros(nr,nc);
        for j=1:length(cc.PixelIdxList)
            all_pids=[all_pids;cc.PixelIdxList{j}];

            % multiple by j to encode with the blob-id
            z(cc.PixelIdxList{j})=1*j;                                         % swiss-cheese (reversed), same thing, but more complicated
        end
        zstack(:,:,i)=z;
        imshow(zstack(:,:,i));
        pause(.5);
        %}

        % vis stuff
        %{
        cdata=zeros(nr,nc,3);
        red_data=zeros(nr,nc);
        green_data=zeros(nr,nc);

        %red_data(all_pids)=raw_red(all_pids);
        %green_data(all_pids)=raw_green(all_pids);

        red_data(all_pids)=scaled_red(all_pids);
        green_data(all_pids)=scaled_green(all_pids);
        BWoutline=bwperim(BW2);

        cdata(:,:,1)=red_data;
        cdata(:,:,2)=green_data;
        cdata(:,:,3)=BWoutline;


        dbg=-1;
        img4=imshow(cdata);

        %img=imshow(BW2);
        dbg=-1;
        pause(sleep_time/100);
        %}
    end
    
    dt=addvars(dt,[1:height(ImageStack)]','Before',1,'NewVariableNames',{'Frame'});
    zstack=dt;
    clear dt;

    function scaled_img=minmax_scale(raw_img,gain)
        igmin=double(min(min(raw_img)));
        igmean=double(mean(mean(raw_img)));
        igmax=double(max(max(raw_img)));

        % identical to mat2gray
        %{
        scaled_img=double(raw_img)-igmin;                                      % offset
        scaled_img=scaled_img/(igmax-igmin);                                   % gain
        scaled_img(scaled_img>1)=1;                                            % saturation
        %}

        scaled_img=double(mat2gray(raw_img,[0,igmean*gain]));
        dbg2=-1;
    end
    %{
    function filt_img=basic_hist_filt(raw_img,thr)
        filt_img=raw_img./thr;
        filt_img(filt_img>1)=1;
    end
    %}
end