function ridx=find_optimum_red(signal)

[~,loc,~,~]=findpeaks(signal);

nloc=length(loc);
z=zeros(nloc,5);

for i=1:nloc
    cloc=loc(i);
    for j=1:5
        ploc=cloc+j;
        if(ploc < length(signal))
            z(i,j)=signal(cloc)-signal(ploc);
        end
    end
end
zmax=max(z,[],2);
lidx=ismember(zmax,max(zmax));

%if ~isempty(lidx)
%    ridx=loc(lidx);
%else
    ind=find(signal==max(signal));
    ridx=ind(end);
%end
%dbg=-1;
