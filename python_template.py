# OPeNDAP client - http://pydap.org
from pydap.client import open_url

# исследуемый геофизический параметр
variable = 'atmosphere_water_vapor_content'

# массив ссылок на выбранные гранулы
granules = [
    'http://opendap.solab.rshu.ru:8080/opendap/allData/SOLAB_AMSRE_L2_NN/2011/10/SOLAB_AMSRE_L2_NN_20111004_060306_20111004_065147_232_A_v1.nc',
    'http://opendap.solab.rshu.ru:8080/opendap/allData/SOLAB_AMSRE_L2_NN/2011/10/SOLAB_AMSRE_L2_NN_20111001_021430_20111001_030424_195_A_v1.nc'
]

# подстановка широты и долготы выбранного региона в индексах массива данных
min_lat = 0
max_lat = 1948
min_lon = 0
max_lon = 195

# шаг сетки
step = 1

# цикл по выбранным гранулам
for granule in granules:
    dataset = open_url(granule)
    selection = dataset[variable][min_lat:step:max_lat][min_lon:step:max_lon]
    # добавьте процедуры обработки данных ниже
    print selection

       
    