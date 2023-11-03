import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from shapely import wkt
import folium
import streamlit as st


@st.cache_data
def cobertura():
    CoberturasSMP = pd.read_csv("C:/Users/yroar/Downloads/coberturasSMPUnzip/CoberturasCSV.csv")
    CoberturasSMP = CoberturasSMP.drop(['Unnamed: 0', 'OID'], axis='columns')
    
    CoberturasSMP['geometry'] = CoberturasSMP['geometry'].apply(wkt.loads)
    GeoDFcobSMP = gpd.GeoDataFrame(CoberturasSMP, crs=3857)
    return GeoDFcobSMP



def geraPOLbuffer(allDrawings, geracaoTecnologia):
    
    if geracaoTecnologia == '2G':
        distBufferEst = 5
    elif geracaoTecnologia == '3G':
        distBufferEst = 3
    elif geracaoTecnologia == '4G':
        distBufferEst = 2
    else:
        distBufferEst = 1
    
    DFpol = pd.DataFrame(allDrawings[0])
    
    if DFpol['geometry']['type'] == "Point":
        geometria = [(Point(DFpol['geometry']['coordinates']))]
    elif DFpol['geometry']['type'] == "LineString":
        geometria = [(LineString(DFpol['geometry']['coordinates']))]
    elif DFpol['geometry']['type'] == "Polygon":
        geometria = [(Polygon(DFpol['geometry']['coordinates'][0]))]
    
    xGeoDF = gpd.GeoDataFrame(geometria, columns=['geometry'], crs=3857)
    
    if DFpol['geometry']['type'] == "Point":
        xBuffer = xGeoDF.buffer(1 * 0.009)
        xBufferEstacoes = xGeoDF.buffer(distBufferEst * 0.009)
    elif DFpol['geometry']['type'] == "LineString":
        xBuffer = xGeoDF.buffer(1.5 * 0.009)
        xBufferEstacoes = xGeoDF.buffer(distBufferEst * 0.009)
    else:
        xBuffer = xGeoDF.buffer(0.01 * 0.009)
        xBufferEstacoes = xGeoDF.buffer(distBufferEst * 0.009)
    
    df_yBuffer = gpd.GeoDataFrame([1], geometry=xBuffer)
    df_yBufferEstacoes = gpd.GeoDataFrame([1], geometry=xBufferEstacoes)
    
    if allDrawings == []:
        POLsim_geo = gpd.GeoSeries()
        POLgeo_json = POLsim_geo.to_json()
        POLGeoBuffer = folium.GeoJson(data=POLgeo_json)
    
    else:
        POLsim_geo = gpd.GeoSeries(df_yBuffer["geometry"]).simplify(tolerance=0.001)
        POLgeo_json = POLsim_geo.to_json()
        POLGeoBuffer = folium.GeoJson(data=POLgeo_json, style_function=lambda x: {'fillColor': 'orange'})
    
    return POLGeoBuffer, xBuffer, xBufferEstacoes



def porcentCob(POLGeoBuffer, tecnologiaMovel):
    GeoDFcobSMP = cobertura()
    polDraw = gpd.GeoDataFrame([1], geometry=POLGeoBuffer, crs=3857)
    
    selecCobTecno = GeoDFcobSMP.loc[GeoDFcobSMP['Tecnologia'] == tecnologiaMovel]
    listaOp = list(selecCobTecno['Operadora'])
    
    DF_intersec = pd.DataFrame()
    
    for op in listaOp:
        coberturaPorOp = selecCobTecno.loc[selecCobTecno['Operadora'] == op]
        intersecDrawCob = gpd.clip(coberturaPorOp, POLGeoBuffer)
        dfAreaIntersec = pd.DataFrame(intersecDrawCob.area)
        dfAreaPoligoDraw = pd.DataFrame(polDraw.area)
        
        if dfAreaIntersec.empty is not True:
            PorcentagemAreaCobertaPolDraw = round((dfAreaIntersec.iloc[0, 0] / dfAreaPoligoDraw.iloc[0, 0]) * 100, 2)
        else:
            PorcentagemAreaCobertaPolDraw = []
        
        intersecDrawCob['area'] = PorcentagemAreaCobertaPolDraw
        DF_intersec = pd.concat([DF_intersec, intersecDrawCob])
    
    return DF_intersec


def selecionaIcone(nomeOp):
    dictOp = {'VIVO': "C:/Users/yroar/Downloads/iconesOp/iconeVIVO-.png",
              'TIM': "C:/Users/yroar/Downloads/iconesOp/iconeTIM-.png",
              'CLARO': "C:/Users/yroar/Downloads/iconesOp/iconeClaro-.png",
              'ALGAR': "C:/Users/yroar/Downloads/iconesOp/iconeAlgar-.png",
              'BRISANET': "C:/Users/yroar/Downloads/iconesOp/iconeBrisanet-.png",
              'SERCOMTEL': "C:/Users/yroar/Downloads/iconesOp/iconeSercomtel-.png",
              'LIGUE': "C:/Users/yroar/Downloads/iconesOp/iconeLIGUE-.png",
              'WINITY': "C:/Users/yroar/Downloads/iconesOp/iconeWinity-.png",
              'LIGGA': "C:/Users/yroar/Downloads/iconesOp/iconeLIGGA-.png"}
    if nomeOp in dictOp.keys():
        return dictOp[nomeOp]
    else:
        None
    