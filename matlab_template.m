%����������� ������������� �������� (�������� � ���������������� ���� �� ����������)
variable = 'atmosphere_water_vapor_content';

%������ ������ �� ��������� �������
granules = {
    'http://opendap.solab.rshu.ru:8080/opendap/allData/SOLAB_AMSRE_L2_NN/2011/10/SOLAB_AMSRE_L2_NN_20111004_060306_20111004_065147_232_A_v1.nc',
    'http://opendap.solab.rshu.ru:8080/opendap/allData/SOLAB_AMSRE_L2_NN/2011/10/SOLAB_AMSRE_L2_NN_20111001_021430_20111001_030424_195_A_v1.nc'
};

%����������� ������ � ������� ���������� ������� � �������� ������� ������
min_lat = 1;
max_lat = 1948;
min_lon = 1;
max_lon = 196;

%��� �����
step = 1;

% �������� ��������� ��� �������� ����������� ������
selection = struct([]);

%���� �� ��������� ��������
for i = 1:length(granules)
    dataset = readNetCDF(char(granules{i}));
    selection{i} = dataset.(variable).data(min_lat:step:max_lat, min_lon:step:max_lon);
    
    % ����� ������
    disp(selection{i}) 
end