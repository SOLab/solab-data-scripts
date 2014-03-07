# v0.3, 05.03.2014, SOLab
# OPeNDAP client - http://pydap.org
from pydap.client import open_url

# исследуемый геофизический параметр
parameters = [
    'atmosphere_water_vapor_content', 'wind_speed_lf', 'sea_surface_temperature', 'atmosphere_cloud_liquid_water_content', 'atmospheric_absorption_at_11GHz'
]

# массив ссылок на выбранные гранулы, а также широта и долгота выбранного региона в индексах массива данных
granules = [
    {'url': 'http://opendap.solab.rshu.ru:8080/opendap/allData/SOLAB_AMSRE_L2_NN/2011/10/SOLAB_AMSRE_L2_NN_20111004_051344_20111004_060336_232_D_v1.nc', 'min_lat': 0, 'max_lat': 195, 'min_lon': 0, 'max_lon': 1995}, 
    {'url': 'http://opendap.solab.rshu.ru:8080/opendap/allData/SOLAB_AMSRE_L2_NN/2011/10/SOLAB_AMSRE_L2_NN_20111004_042418_20111004_051414_216_A_v1.nc', 'min_lat': 0, 'max_lat': 195, 'min_lon': 0, 'max_lon': 1997}
]

# шаг сетки
step = 1

# цикл по выбранным гранулам
for granule in granules:
    dataset = open_url(granule['url'])
    # цикл по геофизическим параметрам
    for parameter in parameters:
        selection = dataset[parameter][granule['min_lat']:step:granule['max_lat']][granule['min_lon']:step:granule['max_lon']]
        # добавьте процедуры обработки данных ниже
        print selection

       
    