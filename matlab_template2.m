%исследуемые геофизические параметры
%geophysical parameters to explore

parameters = { 
    'atmosphere_water_vapor_content',
    'wind_speed_lf',
    'sea_surface_temperature',
    'atmosphere_cloud_liquid_water_content',
    'atmospheric_absorption_at_11GHz',
};

%массив ссылок на выбранные гранулы
%an array of references to the selected granules
granules = {
    'http://opendap.solab.rshu.ru:8080/opendap/allData/SOLAB_AMSRE_L2_NN/2011/10/SOLAB_AMSRE_L2_NN_20111004_060306_20111004_065147_232_A_v1.nc',
};

%подстановка широты и долготы выбранного региона в индексах массива данных
%substitution of latitude and longitude of the selected region in indices of the data array
min_lat = 1;
max_lat = 195;
min_lon = 1;
max_lon = 1947;

%шаг сетки
%grid step
step = 1;

% создание структуры для хранения извлекаемых данных
% creating a structure for storing data that is retrieved
selection = struct([]);

%цикл по выбранным гранулам
% iteration in selected granules
for i = 1:length(granules)
    dataset = readNetCDF(char(granules{i}));

    for j = 1:length(parameters)
        selection{j, i} = dataset.(parameters{j}).data(min_lon:step:max_lon, min_lat:step:max_lat);
        % вывод данных
        % data output
        disp(selection{j, i})
    end
end