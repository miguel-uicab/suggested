# !/usr/bin/env python
# coding: utf-8

import psycopg2
import pickle
import logging
from extras import download_model
from prediction_functions import *

logging_format = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(format=logging_format, datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)


def prediction(json=None,
               with_location_variables=True,
               with_basic_relationship_variables=True,
               with_fid_grid_variables=True,
               with_luxury_features=True):
    temporal_path = "/tmp"
    path = "outputs"
    # Se carga config.yaml. ###################################################
    logging.info('COMIENZO DE PREDICCIÓN.')
    config = get_config()
    config_pred = config['prediction']

    # Se construye DataFrame con variables en payload. ########################
    df_features = get_dataframe(json=json['features'])
    df_location = get_dataframe(json=json['location'])
    df_amenities = get_dataframe(json=json['amenities'])
    df_json = pd.merge(df_features, df_location, left_index=True, right_index=True)
    df_json = pd.merge(df_json, df_amenities, left_index=True, right_index=True)

    # Se transforman a float las variables numéricas presentes en payload. ####
    df_json = transform_data_type_to_float(data=df_json,
                                           list_names=config_pred['list_numeric_names_in_payload_to_float'])

    # Se transforman a booleano las variables de características de inmuebles
    # presentes en payload. #####
    for name in config_pred['list_feature_names_in_payload_to_bool']:
        df_json[name] = df_json[name].fillna(False)
        df_json[name] = df_json[name].astype(bool)

    # Construcción de variables x, y, z derivadas de latitud en longitude. ####
    if with_location_variables:
        df_json = get_location_variables(data=df_json)
        df_json = transform_data_type_to_float(data=df_json,
                                               list_names=config_pred['list_names_location_variables_to_float'])

    # Se construyen variables de relación. ####################################
    if with_basic_relationship_variables:
        df_json = basic_features_relationship(data=df_json)

    # Se aginan polígonos y se traen variables de fid y grid. #################
    if with_fid_grid_variables:
        # Se ubica el inmueble en los polígnos de interés. ####################
        data_conection = config_pred['postgres-db']
        user = data_conection['user']
        passwd = data_conection['password']
        host = data_conection['hostname']
        db_wb = data_conection['name']
        connection = psycopg2.connect(user=user,
                                      password=passwd,
                                      host=host,
                                      database=db_wb)
        data_identifiers = get_geo_identifiers(connection=connection,
                                               latitude=float(df_json.loc[0, "latitude"]),
                                               longitude=float(df_json.loc[0, "longitude"]))
        connection.close()

        # Se verifica se está en Ciudad de México #############################
        if data_identifiers.loc[0, 'state'] != 'Ciudad de México':
            logging.info('NO SE PUEDE DAR PREDICCIÓN PARA ESTA UBICACIÓN.')

            return None

        # Se imputa valor "No identificado" en missing de
        # variables categoricas presentes en polígonos. #######################
        data_identifiers = fillna_categoric_data(data=data_identifiers,
                                                 list_names=config_pred['list_names_in_polygons_to_object'])
        # Se hacen cambios intermedios de tipo de variable. ###################
        data_identifiers = transform_data_type_to_float(data=data_identifiers,
                                                        list_names=['objectid'])
        # Se transforman a string variables categóricas presentes
        # en polígonos. #######################################################
        data_identifiers = transform_data_type_to_object(data=data_identifiers,
                                                         list_names=config_pred['list_names_in_polygons_to_object'])

        # Se crean variables que ayudan en el proceso de entrenamiento. #######
        data_identifiers = create_variables_for_training(data=data_identifiers)

        # Se agrupan valores poco frecuentes de identificadores en un
        # grupo común. #####################
        for name in config_pred['list_names_in_polygons_to_group_rare_identifiers']:
            identifiers_file_name = f'{name}s_not_used.sav'
            assert download_model(path, identifiers_file_name), f"{identifiers_file_name} not load"
            list_not_used = pickle.load(open(f'{temporal_path}/{identifiers_file_name}', 'rb'))
            data_identifiers = group_rare_identifiers(data=data_identifiers,
                                                      identifier=name,
                                                      list_not_used=list_not_used,
                                                      name_complement='modified',
                                                      save_list_names=False)

        # Se traen variables derivadas de los fid y grid. #####################
        grid_data_file_name = 'grid_data_complete.sav'
        cadastral_data_file_name = 'cadastral_data_fid.sav'
        assert download_model(path, grid_data_file_name), f"{grid_data_file_name} not load"
        assert download_model(path, cadastral_data_file_name), f"{cadastral_data_file_name} not load"
        grid_data_complete = pickle.load(open(f'{temporal_path}/{grid_data_file_name}',
                                              'rb'))
        cadastral_data_fid = pickle.load(open(f'{temporal_path}/{cadastral_data_file_name}',
                                              'rb'))
        cadastral_data = cadastral_data_fid[config_pred['list_names_fid_variables']]
        grid_data = grid_data_complete[config_pred['list_names_grid_variables']]
        data_merge = pd.merge(data_identifiers,
                              cadastral_data,
                              how="left",
                              on=["fid"])
        data_merge = pd.merge(data_merge,
                              grid_data,
                              how="left",
                              on=["grid_id"])
        df_json = pd.merge(df_json,
                           data_merge,
                           left_index=True,
                           right_index=True)

    # Se crean variables de información de amenidades de lujo. ################
    if with_luxury_features:
        luxury_features_list = config_pred['luxury_feature_names']
        df_json = luxury_features_variables(df_json,
                                            luxury_features_list)

    # Asignar variable de cluster. ############################################
    colonias_df_file_name = 'colonias_df.sav'
    assert download_model(path, colonias_df_file_name), f"{colonias_df_file_name} not load"
    colonias_df = pickle.load(open(f'{temporal_path}/{colonias_df_file_name}', 'rb'))
    colonias_df.rename(columns={'colonia': 'neigh_id', 'class': 'class_past'},
                       inplace=True)
    df_json = pd.merge(df_json,
                       colonias_df[['neigh_id', 'class_past']],
                       how="left",
                       on=["neigh_id"])
    df_json = transform_data_type_to_object(data=df_json,
                                            list_names=['class_past'])

    # Aplicacion de codificadores en variables categóricas. ###################
    encoder_file_name = 'encoder_cdmx.sav'
    assert download_model(path, encoder_file_name), f"{encoder_file_name} not load"
    encoder_cdmx = pickle.load(open(f'{temporal_path}/{encoder_file_name}', 'rb'))
    categoric_column_names_for_target_encoder = config_pred['categoric_column_names_for_target_encoder']
    df_json[categoric_column_names_for_target_encoder] = encoder_cdmx.transform(df_json[categoric_column_names_for_target_encoder])

    # Predicción. #############################################################
    model_file_name = 'model_cdmx.sav'
    assert download_model(path, model_file_name), f"{model_file_name} not load"
    model = pickle.load(open(f'{temporal_path}/{model_file_name}',
                              'rb'))
    X_predict = df_json[config_pred['selected_features']]
    predict = model.predict(X_predict)[0]

    # Cálculo de máximo y mínimo. #############################################
    min = predict * (1 - config_pred['mape_for_min_max'] / 100)
    max = predict * (1 + config_pred['mape_for_min_max'] / 100)

    # Aplicación de redondeos. ################################################
    round_max = truncate(max, -2)
    round_mid = truncate(predict, -2)
    round_min = truncate(min, -2)
    true_round_predict = round(predict, 2)

    # Salida. #################################################################
    output = {"min": round_min,
              "mid": round_mid,
              "max": round_max,
              "original_prediction": true_round_predict,
              "version": "5.0"}

    logging.info('FIN DE PREDICCIÓN.')

    return output
