function manifest = reproduce_pnas2017_reference(outputDir)
% Primary unchanged author ODE execution. No figure comparison or plotting.
% Example: reproduce_pnas2017_reference('C:\new_external_run_directory')
root=fileparts(fileparts(mfilename('fullpath')));
if nargin~=1, error('PNAS:Output','A new external output directory is required.'); end
outputFile=java.io.File(outputDir); outputDir=char(outputFile.getCanonicalPath());
rootFile=java.io.File(root); rootCanonical=char(rootFile.getCanonicalPath());
if isfolder(outputDir) || isfile(outputDir) || strcmpi(outputDir,rootCanonical) || startsWith(lower(outputDir),lower([rootCanonical filesep]))
    error('PNAS:FrozenOutput','Output must be a new directory outside the repository.');
end
cfg=jsondecode(fileread(fullfile(root,'configs','benchmarks','pnas2017_reference','benchmark.json')));
if ~strcmp(cfg.model_id,'PNAS2017_full_reference') || cfg.time_grid.start_seconds~=1e-4 || cfg.time_grid.end_seconds~=1000 || cfg.time_grid.points~=200 || ...
        cfg.solver.RelTol~=1e-3 || cfg.solver.AbsTol~=1e-9 || ~strcmp(cfg.solver.name,'ode15s')
    error('PNAS:Config','Frozen author semantics changed.');
end
% jsondecode sanitizes path keys; verify the ordered source paths independently.
paths={cfg.source_sbml,cfg.s28_path,cfg.author_rhs,cfg.author_sample,cfg.initial_values,cfg.parameters,cfg.normalized_sbml};
hashRecord=struct('path',{},'sha256',{});
configText=fileread(fullfile(root,'configs','benchmarks','pnas2017_reference','benchmark.json'));
for i=1:numel(paths)
    actual=shaFile(fullfile(root,paths{i}));
    escaped=regexptranslate('escape',paths{i});
    token=regexp(configText,['"' escaped '"\s*:\s*"([a-f0-9]{64})"'],'tokens','once');
    if isempty(token) || ~strcmp(actual,token{1}), error('PNAS:SourceHash','Hash mismatch: %s',paths{i}); end
    hashRecord(end+1)=struct('path',paths{i},'sha256',actual); %#ok<AGROW>
end
authorDir=fileparts(fullfile(root,cfg.author_rhs));
savedPath=path; cleanup=onCleanup(@() path(savedPath)); %#ok<NASGU>
addpath(authorDir,'-begin');
if ~strcmpi(which('fMGG_synthesis'),fullfile(authorDir,'fMGG_synthesis.m'))
    error('PNAS:AuthorFunction','Author RHS shadowed.');
end
names=fMGG_synthesis('states');
initialData=importdata(fullfile(root,cfg.initial_values),',',1);
parameterData=importdata(fullfile(root,cfg.parameters),',',1);
% Exact executable authority from the author's sample: first numeric column.
initial_values=initialData.data(:,1); parameter_values=parameterData.data(:,1);
if numel(initial_values)~=241 || numel(names)~=241 || numel(parameter_values)~=969
    error('PNAS:InputCount','Author input/state counts mismatch.');
end
t=logspace(-4,3,200);
ode_opt=odeset('NonNegative',1:length(initial_values),'RelTol',1e-3,'AbsTol',1e-9);
[~,head]=system(sprintf('git -C "%s" rev-parse HEAD',root));
[~,dirty]=system(sprintf('git -C "%s" status --porcelain=v1',root));
mkdir(outputDir);
escapedOutput=strrep(outputDir,char(39),[char(39) char(39)]);
manifest=struct('execution_status','INCOMPLETE','model_id','PNAS2017_full_reference',...
    'git_HEAD',strtrim(head),'git_dirty_status',dirty,'MATLAB_version',version,'ODE_solver','ode15s',...
    'time_grid',cfg.time_grid,'solver_settings',cfg.solver,'source_hashes',hashRecord,...
    'timestamp_utc',char(datetime('now','TimeZone','UTC','Format',"yyyy-MM-dd'T'HH:mm:ssXXX")),...
    'exact_command',sprintf('reproduce_pnas2017_reference(''%s'')',escapedOutput),...
    'figure_generation','NOT_RUN','S28_comparison','NOT_RUN','experimental_validation','NOT_ESTABLISHED');
manifestPath=fullfile(outputDir,'run_manifest.json');saveManifest(manifestPath,manifest);
try
    model_h=@(tt,x)fMGG_synthesis(tt,x,parameter_values);
    [times,values]=ode15s(model_h,t,initial_values,ode_opt);
    if size(values,1)~=200 || size(values,2)~=241 || any(~isfinite(values),'all')
        error('PNAS:Output','Incomplete or nonfinite author trajectory.');
    end
    trajectory=fullfile(outputDir,'author_matlab_trajectory.csv');
    writecell([{'time_seconds'},reshape(names,1,[])],trajectory);
    writematrix([times,values],trajectory,'WriteMode','append');
    manifest.execution_status='COMPLETED';
    manifest.output_hashes=struct('path','author_matlab_trajectory.csv','sha256',shaFile(trajectory));
    manifest.recorded_minimum=min(values,[],'all');
    manifest.post_integration_clipping=false;
    saveManifest(manifestPath,manifest);
catch exception
    manifest.execution_status='FAILED';manifest.error_identifier=exception.identifier;manifest.error_message=exception.message;
    saveManifest(manifestPath,manifest);rethrow(exception);
end
end
function value=shaFile(file)
fid=fopen(file,'rb');if fid<0,error('PNAS:Read','Cannot read %s',file);end
c=onCleanup(@() fclose(fid)); %#ok<NASGU>
raw=fread(fid,Inf,'*uint8');md=java.security.MessageDigest.getInstance('SHA-256');md.update(typecast(raw,'int8'));
value=lower(reshape(dec2hex(typecast(md.digest(),'uint8'),2).',1,[]));
end
function saveManifest(file,manifest)
fid=fopen(file,'w','n','UTF-8');if fid<0,error('PNAS:Write','Cannot write manifest');end
c=onCleanup(@() fclose(fid)); %#ok<NASGU>
fprintf(fid,'%s\n',jsonencode(manifest,'PrettyPrint',true));
end
