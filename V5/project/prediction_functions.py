# !/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import yaml
from psycopg2 import sql


def get_config():
    """
    Se carga el archivo config.yaml.
    """
    with open('config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    return config


def transform_data_type_to_float(data=None, list_names=None):
    """
    Dada una lista de variables de interés, se tranforman
    a tipo float.
    """
    data_copy = data.copy()
    for name in list_names:
        data_copy[name] = data_copy[name].astype(float)

    return data_copy


def transform_data_type_to_object(data=None, list_names=None):
    """
    Dada una lista de variables de interés, se tranforman
    a tipo object.
    """
    data_copy = data.copy()
    for name in list_names:
        data_copy[name] = data_copy[name].astype(str)

    return data_copy


def get_location_variables(data):
    """
    Se construyen las variables de localización x, y, z.
    """
    data_copy = data.copy()
    for name in ['latitude', 'longitude']:
        data_copy[name] = pd.to_numeric(data_copy[name],
                                        downcast='float',
                                        errors='coerce')
    data_copy['lat_rad'] = data_copy['latitude'] + 90
    data_copy['lat_rad'] = np.radians(data_copy['lat_rad'])
    data_copy['long_rad'] = data_copy['longitude'] + 180
    data_copy['long_rad'] = np.radians(data_copy['long_rad'])
    data_copy['x'] = np.sin(data_copy['lat_rad']) * np.cos(data_copy['long_rad'])
    data_copy['y'] = np.sin(data_copy['lat_rad']) * np.sin(data_copy['long_rad'])
    data_copy['z'] = np.cos(data_copy['lat_rad'])

    return data_copy


def basic_features_relationship(data):
    '''
    Crea variables útiles para el modelo utilizando
    las features básicas de inmueble
    '''
    # data['price_x_mt2'] = data['price'] / data['covered_area']
    data['bathrooms_rooms'] = data['bathrooms'] / data['rooms']
    data['parking_rooms'] = data['parking'] / data['rooms']
    data['covered_area_rooms'] = data['covered_area'] / data['rooms']
    data['covered_area_bathrooms'] = data['covered_area'] / data['bathrooms']
    data['space_utility'] = data['covered_area'] / (data['bathrooms'] + data['rooms'])
    data['rooms_bathrooms_difference'] = data['rooms'] - data['bathrooms']
    data['rooms_parking_difference'] = data['rooms'] - data['parking']

    return data


def create_variables_for_training(data=None):
    """
    Crea variables útiles para el entrenamiento. Se pueden crear, por ejemplo,
    variables que ayuden en el proceso de estratificación.
    """
    data_copy = data.copy()
    data_copy['grid_objectid'] = data_copy['grid_id'] + '_' + data_copy['objectid']

    return data_copy


def correct_identifier(identifier=None, list_not_used=None):
    """
    Sustituye el valor 'group_of_uncommon' en los valores de
    indetificadores geográficos con muy poca frecuencia.
    """
    if identifier in list_not_used:
        return 'group_of_uncommon'
    else:
        return identifier


def group_rare_identifiers(data=None,
                           identifier=None,
                           list_not_used=None,
                           threshold=30,
                           name_complement='modified',
                           save_list_names=False,
                           path=None):
    """
    Lleva a cabo la localización de valores de identificadores geográficos poco
    frecuentes, dado un umbral de frecuencia, y los sustituye por un
    valor general ('group_of_uncommon'). Guarda en un archivo .sav los valores
    que han caído en 'group_of_uncommon'
    """
    # grid ####
    data_copy = data.copy()
    if list_not_used is None:
        pd_count = data_copy[identifier].value_counts().to_frame().reset_index()
        pd_count.columns = [identifier, 'count']
        pd_count['count'] = pd.to_numeric(pd_count['count'],
                                          downcast='float',
                                          errors='coerce')
        list_not_used = pd_count[pd_count['count'] < threshold][identifier].tolist()

    data_copy[f'{identifier}_{name_complement}'] = data_copy.apply(lambda row: correct_identifier(identifier=row[identifier],
                                                                                                  list_not_used=list_not_used),
                                                                   axis=1)
    if save_list_names:
        path_identifier = f'{path}/{identifier}s_not_used.sav'
        pickle.dump(identifiers_not_used, open(path_identifier, 'wb'))

    return data_copy


def luxury_features_variables(data, luxury_features_list):
    '''
    Crea variables relacionadas con las amenidades de lujo.
    '''
    len_vars_luxury = len(luxury_features_list)
    data['prescence_luxury_features'] = data[luxury_features_list].apply(lambda x: any(x), axis=1)
    data['perc_luxury_features'] = data[luxury_features_list].apply(lambda x: sum(x) / len_vars_luxury, axis=1)

    return data


def get_dataframe(json=None):
    """
    Convierte una estructura json con la informarción básica payload
    en un DataFrame. El .T rota el DataFrame con el fin de obtener
    información tipo fila.
    """
    df_json = pd.DataFrame.from_dict(json, orient='index').T

    return df_json


def get_geo_identifiers(connection=None,
                        latitude=None,
                        longitude=None):
    """
    Hace una conección a la base de datos y, con ayuda de postgis, asigna a
    cierto punto de latitud y longitud los polígonos geográficos de interés.
    """
    data_txt = open('query_identifiers.txt', 'r')
    data_txt = data_txt.read()
    data_query = (sql.SQL(data_txt)
                     .format(latitude=sql.Literal(latitude),
                             longitude=sql.Literal(longitude)))
    data_identifiers = pd.read_sql(data_query, connection)
    data_identifiers.dtypes
    data_identifiers['neigh_id'] = pd.to_numeric(data_identifiers['neigh_id'],
                                                 downcast='float', errors='coerce')
    return data_identifiers


def fillna_categoric_data(data=None, list_names=None):
    """
    Dada una lista de variables categóricas, imputa en los
    valores perdidos el valor de 'No identificado'.
    """
    data_copy = data.copy()
    for name in list_names:
        data_copy[name].fillna('No identificado', inplace=True)

    return data_copy


def truncate(n, decimals=0):
    """
    Hace un redondeo a la centena más próxima.
    """
    multiplier = 10 ** decimals
    output = round(n * multiplier) / multiplier

    return output
