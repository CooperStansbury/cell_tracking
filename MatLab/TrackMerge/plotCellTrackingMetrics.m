clear variables
close all

addpath('Functions');

%%
pixelSize=0.6840; %um
samplingTime=30*60; %sec
width=50; height=50;

sf=68.34 / 100;
gDropPer=30;%%
cellCyclePer=linspace(1,100,20);

cellextractOn=0;
peakFindingOn=1;
dataIndex=2;

%%
%load('ImageStack.mat');
%load('T.mat');
%load('./WH02=2;_tracks/T.mat');
%load('./WH04_tracks/T_B5.mat');
%load('./MR31_ShadingCorrection_Tracks_MeanIntensities/MR31_MeanSignals.mat');
%load('./MR31_MeanSignals_Norm/MR31_MeanSignals_Norm.mat');
%load('./MR31_MeanSignals_Norm/ImageStack.mat');

switch dataIndex
    case 1
        load('./PeakFinderRG/MR31_MeanSignals_Norm.mat');
        T.GreenSignal=T.MeanGreenSignal_Norm;
        T.RedSignal=T.MeanRedSignal_Norm;
        T.BlueSignal=T.MeanBlueSignal_Norm;
        tids=[2,5,19,29,40,42,43,47,53,71,73,83];
        T=T(ismember(T.Track,tids),:);
        plotInfo.title='MR31';
        
    case 2
        load('./MR31_Control_and_MYOD1/MR31_Control_4by4.mat')
        T.GreenSignal=T.MeanGreenSignal_Norm;
        T.RedSignal=T.MeanRedSignal_Norm;
        T.BlueSignal=T.MeanBlueSignal_Norm;
        T=sanitize(T,400,200);
        plotInfo.title='MR31 Control: Day 1';
        
    case 3
        load('./MR31_Control_and_MYOD1/MR31_MYOD1_4by4.mat')
        T.GreenSignal=T.MeanGreenSignal_Norm;
        T.RedSignal=T.MeanRedSignal_Norm;
        T.BlueSignal=T.MeanBlueSignal_Norm;
        T=sanitize(T,400,200);
        plotInfo.title='MR31 MYOD1: Day 1';
        
    case 4
        load('./MR31_Day2_Control_and_MYOD1/MR31_Day2_Control_4by4.mat')
        T.GreenSignal=T.MeanGreenSignal_Norm;
        T.RedSignal=T.MeanRedSignal_Norm;
        T.BlueSignal=T.MeanBlueSignal_Norm;
        T=sanitize(T,400,200);
        plotInfo.title='MR31 Control: Day 2';
        
    case 5
        load('./MR31_Day2_Control_and_MYOD1/MR31_Day2_MYOD1_4by4.mat')
        T.GreenSignal=T.MeanGreenSignal_Norm;
        T.RedSignal=T.MeanRedSignal_Norm;
        T.BlueSignal=T.MeanBlueSignal_Norm;
        T=sanitize(T,400,200);
        plotInfo.title='MR31 MYOD1: Day 2';
end

%%
min_frame=min(T.Frame);
max_frame=max(T.Frame);
nframe=length(min_frame:max_frame);

% filter for only tracks through full time range
[C,ia,ic]=unique(T.Track);
a_counts=accumarray(ic,1);
idx=(a_counts==nframe);
full_tracks=C(idx);
T=T(ismember(T.Track,full_tracks),:);

%%
trackId=T.Track;
uqTrackId=unique(trackId);
for i=1:length(uqTrackId)
    trackLengths(i)=sum(trackId==uqTrackId(i));
end

maxGS=1;%max(T.GreenSignal);
maxRS=1;%max(T.RedSignal);

assebleMat.XPos=zeros(max(trackLengths),length(trackLengths))+NaN;
assebleMat.YPos=zeros(max(trackLengths),length(trackLengths))+NaN;
assebleMat.GreenSignal=zeros(max(trackLengths),length(trackLengths))+NaN;
assebleMat.RedSignal=zeros(max(trackLengths),length(trackLengths))+NaN;

%%
for i=1:length(uqTrackId)
    i
    ind=find(trackId==uqTrackId(i));
    gCh=T.GreenSignal(ind)/maxGS;
    rCh=T.RedSignal(ind)/maxRS;
    xpos=T.ScreenX(ind);
    ypos=T.ScreenY(ind);
    frameNo=T.Frame(ind);
    
    gCh(gCh<0)=0;
    rCh(rCh<0)=0;
    
    gCh1=gCh;%/max(gCh)*100;
    rCh1=rCh;%/max(rCh)*100;
    
    if peakFindingOn
        %inv=max(gCh1)-gCh1;
        %[pks,loc,w,p]=findpeaks(inv);
        %pidx(i)=find_optimum(gCh1,loc);
        gidx(i)=find_optimum_green(gCh1);
        ridx(i)=find_optimum_red(rCh1);
    end
    
    assebleMat.XPos(frameNo,i)=xpos;
    assebleMat.YPos(frameNo,i)=ypos;
    assebleMat.GreenSignal(frameNo,i)=gCh;
    assebleMat.RedSignal(frameNo,i)=rCh;
    
    if rand>0.0
        hfig1=figure;
        set(hfig1,'Position',[100 200 500 300])
        yyaxis left
        plot(frameNo,gCh1,'g')
        ylabel('Green Channel')
        hold on
        if peakFindingOn
            scatter(gidx(i),gCh1(gidx(i)),'k');
        end
        yyaxis right
        plot(frameNo,rCh1,'r')
        hold on
        if peakFindingOn
            scatter(ridx(i),rCh1(ridx(i)),'k');
        end
        ylabel('Red Channel')
        title(['Track # ' num2str(uqTrackId(i))])
        xlabel('Frame #')
        %ylim([0 1])
        ax=gca;
        ax.LineWidth=2;
        ax.Box='on';
        ax.FontSize=12;
        %ax.XTickLabel=[];
        %ax.YTickLabel=[];
        drawnow
    end
    
    if cellextractOn
        %T.GreenSignal(i)=m02(POSITION_Y,POSITION_X);
        %T.RedSignal(i)=m03(POSITION_Y,POSITION_X);
        POSITION_X=round(assebleMat.XPos(:,i)/sf)+1;                                   % y,x inverted to further avoid confustion
        POSITION_Y=round(assebleMat.YPos(:,i)/sf)+1;
        hfig2=figure;
        set(hfig2,'Position',[600 300 800 900])
        index=1;
        for nframe=frameNo'
            m01=ImageStack.H3342{nframe};
            m02=ImageStack.AF514{nframe};                                             % green
            m03=ImageStack.mCher{nframe};                                             % red
            
            xmin=POSITION_X(nframe)-width/2;
            ymin=POSITION_Y(nframe)-height/2;
            
            cropH3342{i}{index}=imcrop(m01,[xmin ymin width height]);
            cropAF514{i}{index}=imcrop(m02,[xmin ymin width height]);
            cropmCher{i}{index}=imcrop(m03,[xmin ymin width height]);
            
            cropmCherTest=[];
            cropmCherTest(:,:,1)=cropmCher{i}{index};
            cropmCherTest(:,:,2)=cropAF514{i}{index};
            cropmCherTest(:,:,3)=0*cropH3342{i}{index};
            
            subplot(3,3,[1 2 3])
            imagesc(m01)
            hold on
            plot(POSITION_X(1:nframe),POSITION_Y(1:nframe),'r.')
            hold off
            %ylim([xmin-width xmin+width])
            %xlim([ymin-height ymin+height])
            title('H3342')
            %subplot(2,2,4)
            %imagesc(cropH3342{i}{index})
            subplot(3,3,4)
            imshow(cropH3342{i}{index},[])
            colorbar horiz
            title('H3342')
            
            subplot(3,3,5)
            imshow(cropmCher{i}{index},[])
            colorbar horiz
            title('mCherry')
            
            subplot(3,3,6)
            imshow(cropAF514{i}{index},[])
            colorbar horiz
            title('AF514')
            
            subplot(3,3,[7 8 9])
            yyaxis left
            plot(1:nframe,gCh1(1:nframe),'g')
            ylabel('Green Channel-mean')
            yyaxis right
            plot(1:nframe,rCh1(1:nframe),'r')
            ylabel('Red Channel-mean')
            xlabel('frame#')
            
            drawnow
            index=index+1;
        end
    end
    
end

%% unalligned: cell cycle by cells all plotted in one plot
meanGreenSignal=mean(assebleMat.GreenSignal,2,'omitNaN');
hfig=figure;
set(hfig,'Position',[100 100 1000 400])
subplot(1,2,1)
plot(assebleMat.GreenSignal,'k')
hold on
l1=plot(meanGreenSignal,'g','linewidth',2)
ylabel('Green Channel')
xlabel('Frame #')
legend(l1,'Mean')
title(plotInfo.title)
ax=gca;
ax.LineWidth=2;
ax.Box='on';
ax.FontSize=12;
%ax.XTickLabel=[];
%ax.YTickLabel=[];

meanRedSignal=mean(assebleMat.RedSignal,2,'omitNaN');
%figure
subplot(1,2,2)
plot(assebleMat.RedSignal,'k')
hold on
l1=plot(meanRedSignal,'r','linewidth',2)
ylabel('Red Channel')
xlabel('Frame #')
legend(l1,'Mean')
title(plotInfo.title)
ax=gca;
ax.LineWidth=2;
ax.Box='on';
ax.FontSize=12;
%ax.XTickLabel=[];
%ax.YTickLabel=[];

%% alligning using peakfinding
if peakFindingOn
    hfig1=figure(100);
    set(hfig1,'Position',[100 100 1000 400])
    %hfig2=figure(101);
    gcAll=[]; 
    rcAll=[];
    for i=1:size(assebleMat.XPos,2)
        i
        gC=assebleMat.GreenSignal(:,i);
        rC=assebleMat.RedSignal(:,i);
        %timeaxis=[-gidx(i)+1:1:0 1:length(gC)-gidx(i)];
        if ridx(i)>gidx(i)
            timeaxis1=[1:gidx(i)]/gidx(i)*gDropPer;
            tS=gidx(i)+1:ridx(i);
            timeaxis2=gDropPer+(tS-gidx(i))/(ridx(i)-gidx(i))*(100-gDropPer)
            timeaxis=[timeaxis1 timeaxis2];
            gC=gC(1:ridx(i));
            rC=rC(1:ridx(i));
            
            gcAll=[gcAll; interp1(timeaxis,gC,cellCyclePer)];
            rcAll=[rcAll; interp1(timeaxis,rC,cellCyclePer)];
            
            figure(hfig1)
            subplot(1,2,1)
            plot(timeaxis,gC,'k')
            hold on
            xlabel('% cell cycle')
            ylabel('Green Channel')
            title(plotInfo.title)
            ax=gca;
            ax.LineWidth=2;
            ax.Box='on';
            ax.FontSize=12;
            
            %figure(hfig2)
            subplot(1,2,2)
            plot(timeaxis,rC,'k')
            hold on
            xlabel('%cell cycle')
            ylabel('Red Channel')
            title(plotInfo.title)
            ax=gca;
            ax.LineWidth=2;
            ax.Box='on';
            ax.FontSize=12;
        end
    end
    meanRedSignal=mean(rcAll,1,'omitNaN');
    meanGreenSignal=mean(gcAll,1,'omitNaN');
    
    subplot(1,2,1)
    l1=plot(cellCyclePer,meanGreenSignal,'g','linewidth',2);
    legend(l1,'Mean')

    subplot(1,2,2)
    l1=plot(cellCyclePer,meanRedSignal,'r','linewidth',2);
    legend(l1,'Mean')
    drawnow
end

%% time warping
% ind=find(trackId==tracIdTemplate);
% gChTemp=T.GreenSignal(ind)/maxGS;
% rChTemp=T.RedSignal(ind)/maxRS;
% gChTemp(gChTemp<0)=0;
% rChTemp(rChTemp<0)=0;
% gChTemp=gChTemp/max(gChTemp)*100;
% rChTemp=rChTemp/max(rChTemp)*100;

if 0
    tracIdTemplate=14;
    gChTemp=assebleMat.GreenSignal(:,tracIdTemplate);
    rChTemp=assebleMat.RedSignal(:,tracIdTemplate);
    gChTemp=gChTemp/max(gChTemp)*100;
    rChTemp=rChTemp/max(rChTemp)*100;
    
    figure
    plot(gChTemp)
    hold on
    plot(rChTemp)
    
    hfig1=figure(102);
    hfig2=figure(103);
    
    for i=1:size(assebleMat.XPos,2)
        i
        gCh=assebleMat.GreenSignal(:,i);
        rCh=assebleMat.RedSignal(:,i);
        gCh1=gCh/max(gCh)*100;
        rCh1=rCh/max(rCh)*100;
        
        [DIST,IX,IY] = dtw(gChTemp,gCh1);
        
        figure
        subplot(2,1,1)
        plot(gChTemp)
        hold on
        plot(gCh1)
        subplot(2,1,2)
        plot(gChTemp(IX))
        hold on
        plot(gCh1(IY))
        drawnow
        
        figure(hfig1)
        plot(gCh1(IY),'k')
        hold on
        
        figure(hfig2)
        plot(rCh1(IY),'k')
        hold on
    end
end

%%
% POSITION_X=round(assebleMat.XPos/sf)+1;
% POSITION_Y=round(assebleMat.YPos/sf)+1;
% figure
% for nframe=1:max(trackLengths)
%     m01=ImageStack.H3342{nframe};                                             % green
%     imagesc(m01)
%     hold on
%     plot(POSITION_X(nframe,:),POSITION_Y(nframe,:),'r*')
%     pause(1)
%     hold off
%     drawnow
% end

return

%% speed
deltaX=diff(assebleMat.XPos);
deltaY=diff(assebleMat.YPos);
deltaXY=sqrt(deltaX.^2+deltaY.^2);
speed=deltaXY*pixelSize/samplingTime;
figure
subplot(2,1,1)
plot(speed)
xlabel('Frame #')
ylabel('Speed: mu/sec')
title(plotInfo.title)
ax=gca;
ax.LineWidth=2;
ax.Box='on';
ax.FontSize=12;
subplot(2,1,2)
hist(speed(:))
xlabel('Speed: mu/sec')
ylabel('Count')
title('Speed Histogram')
ax=gca;
ax.LineWidth=2;
ax.Box='on';
ax.FontSize=12;
drawnow

fac=0.1;
figure
for i=1:size(deltaX)
    plot(assebleMat.XPos(1:i,:),assebleMat.YPos(1:i,:))
    hold on
    quiver(assebleMat.XPos(i,:),assebleMat.YPos(i,:),deltaX(i,:),deltaY(i,:),1,'k')
    hold off
    xlim([(1-fac)*min(assebleMat.XPos(:)) (1+fac)*max(assebleMat.XPos(:))])
    ylim([(1-fac)*min(assebleMat.YPos(:)) (1+fac)*max(assebleMat.YPos(:))])
    ax=gca;
    ax.LineWidth=2;
    ax.Box='on';
    ax.FontSize=12;
    xlabel('x')
    ylabel('y')
    title(plotInfo.title)
    pause(0.5)
    drawnow
end
