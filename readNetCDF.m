function structure = readNetCDF(filename)
% Read data to struct from the specified NetCDFfile

ncid = netcdf.open(filename,'NC_NOWRITE');

% Determine contents of the file.
[~, nvars , ~, ~] = netcdf.inq(ncid);

% make structure an empty structure
structure = struct;

for i = 0:nvars-1
    % Get information about variables in the file.
    [varname, ~, ~, numatts] = netcdf.inqVar(ncid,i);
    structure.(varname) = varname;

    % Get variables ID, given its name.
    varid = netcdf.inqVarID(ncid,varname);

    % make structure.(varname) an empty structure to avoid warnings
    structure.(varname) = struct;
    structure.(varname).varid = varid;

    for j = 0:numatts-1
        % Get attribute name, given variable id.
        attname = netcdf.inqAttName(ncid,varid,j);
        if (strfind('_', char(attname(1))) ~= 0)
            attname_ = attname(2:end);
        else attname_ = attname;
        end
        % make structure.(varname).(attname_) an empty structure to avoid warnings
        structure.(varname).(attname_) = struct;
        structure.(varname).(attname_) = attname;

        % Get value of attribute.
        attval = netcdf.getAtt(ncid,varid,attname);
        % find spaces and change to "_"
        attval_ = num2str(attval);
        attval_(isspace(attval_)==1) = '_';
        attval_(strfind(':', attval_)) = '_';
        attval_(strfind('-', attval_)) = '_';
        attval_(strfind('=', attval_)) = '_';
        attval_(strfind(';', attval_)) = '_';
        attval_(strfind('/', attval_)) = '_';
        attval_(strfind('(', attval_)) = '_';
        attval_(strfind(')', attval_)) = '_';
        if (strfind('_', char(attval_(1))) ~= 0)
            attval_ = attval_(2:end);
        else attval_ = attval_;
        end
%         attval(strfind('_', char(attval))) = '';
%         make structure.(varname).attval an empty structure to avoid warnings
%         structure.(varname).(['attval_' char(attval_)]) = struct;
%         structure.(varname).(['attval_' char(attval_)]) = attval;
        structure.(varname).(attname_) = attval;
    end

    % Get the data from the variables, given its ID.
    data = netcdf.getVar(ncid,varid);
    structure.(varname).data = data;
end

end % FUNCTION
