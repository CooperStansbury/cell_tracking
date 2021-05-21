% filters for full tracks with signals above threshold
function T=sanitize(T,gthr,rthr)
    min_frame=min(T.Frame);
    max_frame=max(T.Frame);
    nframe=length(min_frame:max_frame);

    % filter for only tracks through full time range
    [C,~,ic]=unique(T.Track);
    a_counts=accumarray(ic,1);
    idx=(a_counts==nframe);
    full_tracks=C(idx);
    T=T(ismember(T.Track,full_tracks),:);

    % filter for tracks above expression threshold
    [G, trackID]=findgroups(T.Track);
    max_green=splitapply(@max,T.GreenSignal,G);
    max_red=splitapply(@max,T.RedSignal,G);
    green_idx=(max_green > gthr);
    red_idx=(max_red > rthr);
    valid_tracks=trackID(green_idx&red_idx);
    T=T(ismember(T.Track,valid_tracks),:);
end