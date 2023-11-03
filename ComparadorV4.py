import streamlit as st
import pandas as pd
import folium
from folium.plugins import Draw, MarkerCluster, MeasureControl, FeatureGroupSubGroup
from streamlit_folium import st_folium
import geopandas as gpd
import funComparadorV0 as fun
from shapely.geometry import Point, Polygon

st.set_page_config(page_title='Comparador', layout="centered")
st.title(':gray[Comparador SMP]')

status = [0]

######################################################################################################################

## dados geométricos municípios
path = "C:/Users/yroar/OneDrive/Documents/DADOS_MUNICIPIOS.csv"
path2 = "C:/Users/yroar/Downloads/BR_mun_sede_limites_dec.csv"
path3 = "C:/Users/yroar/Downloads/Estacoes_SMP_tec.csv"


###
## dados das estações

@st.cache_data
def estacoesSMP(path3):
    EstacoesSMP = pd.read_csv(path3, encoding='latin_1')
    
    geometriaEstacoesSMP = [Point(xy) for xy in zip(EstacoesSMP['Longitude'], EstacoesSMP['Latitude'])]
    
    geoDFestacoesSMP = gpd.GeoDataFrame(EstacoesSMP, geometry=geometriaEstacoesSMP, crs='EPSG:3857')
    
    return geoDFestacoesSMP


######################################################################################################################
geoDFestacoesSMP = estacoesSMP(path3)

location = [-15.5, -54.8]
zoom_start = 4
# 'bounds': {'_southWest': {'lat': -41.48235440132145, 'lng': -87.5201472465456}, '_northEast': {'lat': 15.656750744681045, 'lng': -25.996709746545598}}, 'zoom': 4

with st.container():
    st.write("Adicione ao mapa seguimento(s) de reta(s), ou um polígono, ou um marcador")
    grupo = folium.FeatureGroup('Estações')
    
    mapa = folium.Map(location=location, no_touch=True,
                      tiles='openstreetmap', control_scale=True,
                      crs='EPSG3857',
                      zoom_start=zoom_start,
                      key='mapaBase',
                      prefer_canvas=False,
                      max_bounds=False,
    
                      )
    
    (Draw(export=False, show_geometry_on_click=False,
          filename='data.geojson',
          position='topleft',
          draw_options={'marker': True,
                        'polyline': True,
                        'polygon': True,
                        'circlemarker': False,
                        'rectangle': False,
                        'circle': False},
          edit_options={'poly': {'allowIntersection': False}})).add_to(mapa)
    
    (folium.plugins.MousePosition(position='bottomright', separator=' | ')).add_to(mapa)
    
    marker_cluster = MarkerCluster(name="estacoes")
    grupo.add_child(marker_cluster)
    
    folium.plugins.Geocoder(add_marker=False, position='topright').add_to(mapa)
    mapa.add_child(MeasureControl(position='bottomleft', primary_length_unit='meters'))
    
    ##----------------------------------------------------------------------------------##
    
    status = list(st.session_state.values())
    
    if len(status) >= 1:
        for i in range(len(status)):
            if type(status[i]) == str or status[i] == None:
                pass
            else:
                statusMapa = status[i]
    
    if len(status) >= 1:
        
        if statusMapa['all_drawings'] != None:
            if len(statusMapa['all_drawings']) == 1:
    
                if len(status) == 2:
                    geracaoTecnologia = st.session_state.tecnologia
                else:
                    geracaoTecnologia = '4G'
                    
                print(geracaoTecnologia)
                
                POLGeoBuffer, xBuffer, bufEst = fun.geraPOLbuffer(statusMapa['all_drawings'], geracaoTecnologia)
                grupo.add_child(POLGeoBuffer)
                
                geoDFbufEst = gpd.GeoDataFrame(bufEst)
                mascaraEstacoesSelecionadas = geoDFestacoesSMP.within(geoDFbufEst.iloc[0, 0])
                
                EstSel = geoDFestacoesSMP.loc[mascaraEstacoesSelecionadas].copy()
                
                dfEstSel = pd.DataFrame(EstSel)
                OpeTecQtdEst = pd.DataFrame(dfEstSel.value_counts(subset=['NomeEntidade', 'Geracao']))
                OpeTecQtdEstNovo = OpeTecQtdEst.reset_index()
                
                listaOperadoras = list(OpeTecQtdEstNovo['NomeEntidade'].drop_duplicates())
                
                ##################################################################
                
                if len(EstSel) != []:
                    
                    EstSel = EstSel[EstSel['Geracao'] == geracaoTecnologia]
                    
                    for i in range(0, len(EstSel)):
                        nomeOP = EstSel.iloc[i]['NomeEntidade']
                        
                        logo = fun.selecionaIcone(nomeOP)
                        icone = folium.features.CustomIcon(logo, icon_size=(30, 30))
                        
                        markerOP = folium.Marker(
                            location=[EstSel.iloc[i]['Latitude'], EstSel.iloc[i]['Longitude']],
                            # tooltip=EstSel.iloc[i][['NomeEntidade', 'NumEstacao', 'Geracao']],
                            tooltip=EstSel.iloc[i][['Geracao']],
                            icon=icone
                        ).add_to(marker_cluster)
    
    mostraMapa = st_folium(mapa, feature_group_to_add=grupo, return_on_hover=False, width=700)
    
    if len(status) >= 1:
        if statusMapa['all_drawings'] != None:
            if len(statusMapa['all_drawings']) == 1:
                
                tecnologiaMovel = st.radio('***Selecione a Tecnologia***', ["2G", "3G", "4G", "5G"],
                                           key='tecnologia', horizontal=True, disabled=False, index=2)
                
                df_PorcentagemCobertura = fun.porcentCob(xBuffer, tecnologiaMovel)
                
                ############################# TABELA DE INDICADORES #####################################
                df_indicadores_dados = pd.read_excel(
                    f'C:\\Users\\Public\\Documents\\IndicadoresDadosSMP\\indicadoresRQUAL.xlsx')
                
                listaOp_comCobertura = list(df_PorcentagemCobertura['Operadora'])
                
                df_PorcentagemCobertura.set_index('Operadora', inplace=True)
                
                df_indNovo = pd.DataFrame()
                
                for op in listaOp_comCobertura:
                    df_Indicador_Op = df_indicadores_dados.loc[df_indicadores_dados['Operadora'] == op]
                    selecaoOP = OpeTecQtdEstNovo[OpeTecQtdEstNovo['NomeEntidade'] == op]
                    selecaoTec = selecaoOP[selecaoOP['Geracao'] == tecnologiaMovel]
                    df_Indicador_Op['Cobertura (%)'] = df_PorcentagemCobertura.loc[op, 'area']
                    
                    if selecaoTec.empty:
                        df_Indicador_Op['Qtd Estações'] = '-'
                    else:
                        df_Indicador_Op['Qtd Estações'] = selecaoTec['count'].values[0]
                    
                    df_indNovo = pd.concat([df_indNovo, df_Indicador_Op])
                
                st.dataframe(df_indNovo, hide_index=True)
            
            elif len(statusMapa['all_drawings']) > 1:
                st.write(':red[Para fazer nova consulta, apague o(s) objeto(s) existente(s)]')
                st.write(':red[e inclua um novo objeto no mapa.]')





