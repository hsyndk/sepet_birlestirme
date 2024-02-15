from geocode_location_converter import GeocodeLocationConverter as glc
import random
import xlsxwriter
import math


converter = glc()

## tam ölçüleri bilinmemekle birlikte, Ankara Kızılay ve çevresini kapsayan bir alanın geocode'ları kullanıldı.
edge_geocodes = {
    "left_top": {
        'lat': 39.930610,
        'lon': 32.844595
    },
    "right_top": {
        'lat': 39.930610,
        'lon': 32.865696
    },
    "left_bottom": {
        'lat': 39.917291,
        'lon': 32.844595
    },
    "right_bottom": {
        'lat': 39.917291,
        'lon': 32.865696
    },
}

sepet_positions = []
sepet_counts_input = input("Rastgele Belirlenecek Lokasyon Sayısı Giriniz: ")

try:
    sepet_counts = int(sepet_counts_input)
except Exception:
    sepet_counts = 500
    print("0'dan büyük bir tam sayı değeri girmediğiniz için rastgele belirlenecek lokasyon sayısı 500 olarak atandı.")

#belirlenen sayı kadar lokasyon için, yukarıda atanmış alan içinde kalacak biçimde rastgele geocode'lar üretilir
for i in range(sepet_counts):
    lat_rand = random.random()
    lon_rand = random.random()
    sepet_positions.append(
        {
            "lat": edge_geocodes["left_bottom"]["lat"] + (edge_geocodes["right_top"]["lat"] - edge_geocodes["left_bottom"]["lat"])*lat_rand,
            "lon": edge_geocodes["left_bottom"]["lon"] + (edge_geocodes["right_top"]["lon"] - edge_geocodes["left_bottom"]["lon"])*lon_rand
        }
    )


''' carrier_positions =>
1   2   3
4   5   6  
7   8   9
'''

carrier_count = 9
carriers = {}

#taşıyıcıların sorumlu oldukları bölgelerin geocode'ları tespit edilir 
for carrier in range(carrier_count):
    top_line_lat = edge_geocodes["left_bottom"]["lat"] + (edge_geocodes["right_top"]["lat"] - edge_geocodes["left_bottom"]["lat"])*(math.floor(carrier/3)/3)
    bottom_line_lat = edge_geocodes["left_bottom"]["lat"] + (edge_geocodes["right_top"]["lat"] - edge_geocodes["left_bottom"]["lat"])*((math.floor(carrier/3)+1)/3)
    right_line_lon = edge_geocodes["left_bottom"]["lon"] + (edge_geocodes["right_top"]["lon"] - edge_geocodes["left_bottom"]["lon"])*((carrier%3)/3)
    left_line_lon = edge_geocodes["left_bottom"]["lon"] + (edge_geocodes["right_top"]["lon"] - edge_geocodes["left_bottom"]["lon"])*((carrier%3 + 1)/3)
    carriers[carrier+1] = {"sepets":[]}
    
    carriers[carrier+1]["geocodes"]= {
        "left_top": {
            "lat": top_line_lat,
            "lon": left_line_lon
        },
        "right_top": {
            "lat": top_line_lat,
            "lon": right_line_lon
        },
        "left_bottom": {
            "lat": bottom_line_lat,
            "lon": left_line_lon
        },
        "right_bottom": {
            "lat": bottom_line_lat,
            "lon": right_line_lon
        },
    }
    

##tüm alanın dikey ve yataydaki geocode genliği hesaplanır
vertical_geocode_diff_of_total_area = edge_geocodes["right_top"]["lat"]-edge_geocodes["right_bottom"]["lat"]
horizontal_geocode_diff_of_total_area = edge_geocodes["right_top"]["lon"]-edge_geocodes["left_top"]["lon"]

##rastgele oluşturulmuş geocode'lar taşıyıcıların bulunduğu bölgelere atanır.
for position in sepet_positions:
    lat = position["lat"]
    lon = position["lon"]
    vertical_order = (lat - edge_geocodes["left_bottom"]["lat"])/(vertical_geocode_diff_of_total_area/3)
    horizontal_order = (lon - edge_geocodes["left_bottom"]["lon"])/(horizontal_geocode_diff_of_total_area/3)
    carrier = 1 + math.floor(vertical_order)*3 + math.floor(horizontal_order)
    carriers[carrier]["sepets"].append(position)


## taşıyıcı bazında gidecekleri lokasyonlar tek tek tespit edilip oluşturulan excel dökümanının taşıyıcı için ayrılmış sayfasına yazılır
workbook = xlsxwriter.Workbook('carriers_addresses.xlsx')
for carrier in range(carrier_count):
    worksheet = workbook.add_worksheet("carrier_" + str(carrier + 1))
    
    ## dökümana taşıyıcının bulunduğu bölgenin sınır geocode'ları yazılır
    worksheet.set_column("A:A", 70)
    worksheet.set_column("B:B", 30)
    worksheet.set_column("C:C", 30)
    worksheet.write("A1", "POSITION")
    worksheet.write("B1", "LATITUDE")
    worksheet.write("C1", "LONGTITUDE")
    
    worksheet.write('A2', "Top Right")
    worksheet.write('B2', carriers[carrier+1]["geocodes"]["right_top"]["lat"])
    worksheet.write('C2', carriers[carrier+1]["geocodes"]["right_top"]["lon"])
    worksheet.write('A3', "Bottom Left")
    worksheet.write('B3', carriers[carrier+1]["geocodes"]["left_bottom"]["lat"])
    worksheet.write('C3', carriers[carrier+1]["geocodes"]["left_bottom"]["lon"])
    worksheet.write('A4', "Bottom Right")
    worksheet.write('B4', carriers[carrier+1]["geocodes"]["right_bottom"]["lat"])
    worksheet.write('C4', carriers[carrier+1]["geocodes"]["right_bottom"]["lon"])
    worksheet.write('A5', "Top Left")
    worksheet.write('B5', carriers[carrier+1]["geocodes"]["left_top"]["lat"])
    worksheet.write('C5', carriers[carrier+1]["geocodes"]["left_top"]["lon"])
    
    
    for position in range(len(carriers[carrier + 1]["sepets"])):
        bold = workbook.add_format({'bold': True})
        
        ## rastgele oluşturulmuş geocode'lara karşılık gelen adresler alınır.
        information = converter.get_location_from_geocode(carriers[carrier+1]["sepets"][position]["lat"], carriers[carrier+1]["sepets"][position]["lon"])
        
        ## dökümana taşıyıcının gideceği adres ve bu adresin geocode bilgileri yazılır.
        worksheet.write('A' + str(position + 6), information["display_name"], bold)
        worksheet.write('B' + str(position + 6), str(carriers[carrier+1]["sepets"][position]["lat"]))
        worksheet.write('C' + str(position + 6), str(carriers[carrier+1]["sepets"][position]["lon"]))
        
        ## konsolda ilgili adresi ve bu adresin taşıyıcının sınırları dahilinde olduğu geocode'ların kıyaslaması yoluyla gösterilir. 
        print("latitude: " + str(carriers[carrier+1]["geocodes"]["right_top"]["lat"]) + " => " + str(carriers[carrier+1]["sepets"][position]["lat"]) + " <= " + str(carriers[carrier+1]["geocodes"]["right_bottom"]["lat"]) + "\nlongitude: " + str(carriers[carrier+1]["geocodes"]["left_bottom"]["lon"]) + " => " + str(carriers[carrier+1]["sepets"][position]["lon"]) + " <= " + str(carriers[carrier+1]["geocodes"]["right_bottom"]["lon"]))
        print(information["display_name"])

workbook.close()
print("_"*100)
print("Taşıyıcıların gidecekleri lokasyonların listelendiği dökümanın hazırlanması tammalandı.")
print("-"*100)