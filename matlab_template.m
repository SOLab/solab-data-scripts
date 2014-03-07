%исследуемый геофизический параметр
%in question geophysical parameter
parameters = {
	'atmosphere_water_vapor_content',
};

%массив ссылок на выбранные гранулы
%an array of references to the selected granules

granules = [struct('url', 'http://opendap.solab.rshu.ru:8080/opendap/allData/SOLAB_AMSRE_L2_NN/2011/10/SOLAB_AMSRE_L2_NN_20111004_060306_20111004_065147_232_A_v1.nc',...
    'min_lat', 1, 'max_lat', 196, 'min_lon', 1, 'max_lon', 1948), ...
    struct('url', 'http://opendap.solab.rshu.ru:8080/opendap/allData/SOLAB_AMSRE_L2_NN/2011/10/SOLAB_AMSRE_L2_NN_20111001_021430_20111001_030424_195_A_v1.nc', ...
    'min_lat', 1, 'max_lat', 196, ...
    'min_lon', 1, ... 
    'max_lon', 1948)...
]

%шаг сетки
%grid step
step = 1;

% создание структуры для хранения извлекаемых данных
% creating a structure for storing data that is retrieved
selection = struct([]);

%цикл по выбранным гранулам
% iteration in selected granules
for i = 1:length(granules)
    granules(i).url
    dataset = readNetCDF(char(granules(i).url));

    for j = 1:length(parameters)
	    selection{j, i} = dataset.(parameters{j}).data(granules(i).min_lon:step:granules(i).max_lon, granules(i).min_lat:step:granules(i).max_lat);
	    % вывод данных
	    % data output
	    disp(selection{j, i})
	end  
end