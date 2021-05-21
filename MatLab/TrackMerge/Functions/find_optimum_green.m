function gidx=find_optimum_green(signal)
inv=max(signal)-signal;
[~,loc,~,~]=findpeaks(inv);

nloc=length(loc);
z=zeros(nloc,5);

for i=1:nloc
    cloc=loc(i);
    for j=1:5
        ploc=cloc-j;
        if(ploc > 0)
            z(i,j)=signal(ploc)-signal(cloc);
        end
    end
end
zmax=max(z,[],2);
lidx=ismember(zmax,max(zmax));

%if ~isempty(lidx)
%    gidx=loc(lidx);
%else
    ind=find(signal==min(signal));
    gidx=ind(1);
%end

