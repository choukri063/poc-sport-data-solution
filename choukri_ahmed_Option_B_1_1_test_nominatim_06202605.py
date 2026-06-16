# test_nominatim.py
import requests
import time

def geocode_address(address):
    """
    Convertit une adresse en coordonnées (latitude, longitude)
    Utilise Nominatim (OpenStreetMap) - gratuit
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "SportDataSolution-POC/1.0"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            return None, None
    except Exception as e:
        print(f"Erreur : {e}")
        return None, None

# Test avec le bureau
bureau_address = "1362 Avenue des Platanes, Lattes, France"
print(f"📍 Recherche du bureau : {bureau_address}")
lat, lon = geocode_address(bureau_address)
print(f"Bureau trouvé : lat={lat}, lon={lon}")
print()

# Test avec une adresse domicile type
test_address = "15 Rue de la République, Montpellier, France"
print(f"🏠 Test adresse domicile : {test_address}")
lat, lon = geocode_address(test_address)
print(f"Domicile trouvé : lat={lat}, lon={lon}")
print()

# Petite pause pour respecter la limite de requêtes Nominatim
time.sleep(1)