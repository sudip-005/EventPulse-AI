from geoalchemy2 import functions as geo_func
from sqlalchemy import func

def geom_to_geojson(geom):
    """Convert WKB geometry to GeoJSON dict."""
    return func.ST_AsGeoJSON(geom)