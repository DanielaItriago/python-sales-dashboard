import pandas as pd

# =========================
# 1. Cargar archivos
# =========================

orders = pd.read_csv("olist_orders_dataset.csv")
items = pd.read_csv("olist_order_items_dataset.csv")
products = pd.read_csv("olist_products_dataset.csv")
customers = pd.read_csv("olist_customers_dataset.csv")
translation = pd.read_csv("product_category_name_translation.csv")

# =========================
# 2. Limpiar productos
# =========================

products["product_category_name"] = products["product_category_name"].fillna("unknown")

products = products.merge(
    translation,
    on="product_category_name",
    how="left"
)

products["product_category_name_english"] = (
    products["product_category_name_english"].fillna("Unknown")
)

# =========================
# 3. Crear tabla principal
# =========================

sales = items.merge(
    products[["product_id", "product_category_name_english"]],
    on="product_id",
    how="left"
)

sales = sales.merge(
    orders[["order_id", "customer_id", "order_purchase_timestamp", "order_status"]],
    on="order_id",
    how="left"
)

sales = sales.merge(
    customers[["customer_id", "customer_state"]],
    on="customer_id",
    how="left"
)

# =========================
# 4. Métricas y fechas
# =========================

sales["total_sale"] = sales["price"] + sales["freight_value"]

sales["order_purchase_timestamp"] = pd.to_datetime(
    sales["order_purchase_timestamp"]
)

sales_clean = sales[sales["order_status"] == "delivered"].copy()

sales_clean["year"] = sales_clean["order_purchase_timestamp"].dt.year
sales_clean["month"] = sales_clean["order_purchase_timestamp"].dt.month
sales_clean["month_name"] = sales_clean["order_purchase_timestamp"].dt.strftime("%B")
sales_clean["quarter"] = sales_clean["order_purchase_timestamp"].dt.quarter
sales_clean["year_month"] = sales_clean["order_purchase_timestamp"].dt.strftime("%Y-%m")

# =========================
# 5. Diccionario completo de categorías
# =========================

category_translation = {
    "agro_industry_and_commerce": "Agroindustria y Comercio",
    "air_conditioning": "Climatización",
    "art": "Arte",
    "arts_and_craftmanship": "Artesanías",
    "audio": "Audio",
    "auto": "Automotriz",
    "baby": "Bebés",
    "bed_bath_table": "Hogar y Decoración",
    "books_general_interest": "Libros",
    "books_imported": "Libros Importados",
    "books_technical": "Libros Técnicos",
    "cds_dvds_musicals": "CDs y DVDs",
    "christmas_supplies": "Navidad",
    "cine_photo": "Cine y Fotografía",
    "computers": "Computadoras",
    "computers_accessories": "Tecnología",
    "consoles_games": "Consolas y Videojuegos",
    "construction_tools_construction": "Herramientas de Construcción",
    "construction_tools_lights": "Iluminación",
    "construction_tools_safety": "Seguridad Industrial",
    "cool_stuff": "Tecnología",
    "costruction_tools_garden": "Herramientas de Jardín",
    "costruction_tools_tools": "Herramientas",
    "diapers_and_hygiene": "Higiene",
    "drinks": "Bebidas",
    "dvds_blu_ray": "DVDs y Blu-Ray",
    "electronics": "Electrónica",
    "fashio_female_clothing": "Moda Mujer",
    "fashion_bags_accessories": "Bolsos y Accesorios",
    "fashion_childrens_clothes": "Moda Infantil",
    "fashion_male_clothing": "Moda Hombre",
    "fashion_shoes": "Calzado",
    "fashion_sport": "Moda Deportiva",
    "fashion_underwear_beach": "Ropa Interior y Playa",
    "fixed_telephony": "Telefonía Fija",
    "flowers": "Flores",
    "food": "Alimentos",
    "food_drink": "Alimentos y Bebidas",
    "furniture_bedroom": "Muebles Dormitorio",
    "furniture_decor": "Decoración",
    "furniture_living_room": "Muebles Living",
    "furniture_mattress_and_upholstery": "Colchones y Tapicería",
    "garden_tools": "Jardinería",
    "health_beauty": "Salud y Belleza",
    "home_appliances": "Electrodomésticos",
    "home_appliances_2": "Electrodomésticos",
    "home_comfort_2": "Confort del Hogar",
    "home_confort": "Confort del Hogar",
    "home_construction": "Construcción y Hogar",
    "housewares": "Hogar",
    "industry_commerce_and_business": "Industria y Comercio",
    "kitchen_dining_laundry_garden_furniture": "Cocina, Lavandería y Jardín",
    "la_cuisine": "Cocina",
    "luggage_accessories": "Equipaje y Accesorios",
    "market_place": "Marketplace",
    "music": "Música",
    "musical_instruments": "Instrumentos Musicales",
    "office_furniture": "Muebles de Oficina",
    "party_supplies": "Fiesta",
    "perfumery": "Belleza",
    "pet_shop": "Mascotas",
    "security_and_services": "Seguridad y Servicios",
    "signaling_and_security": "Señalización y Seguridad",
    "small_appliances": "Pequeños Electrodomésticos",
    "small_appliances_home_oven_and_coffee": "Cocina y Café",
    "sports_leisure": "Deportes",
    "stationery": "Papelería",
    "tablets_printing_image": "Tablets e Impresión",
    "telephony": "Telefonía",
    "toys": "Juguetes",
    "watches_gifts": "Regalería",
    "Unknown": "Sin categoría"
}

# Limpiar espacios y traducir
sales_clean["product_category_name_english"] = (
    sales_clean["product_category_name_english"]
    .astype(str)
    .str.strip()
)

sales_clean["category_es"] = (
    sales_clean["product_category_name_english"]
    .map(category_translation)
)

sales_clean["category_es"] = sales_clean["category_es"].fillna(
    sales_clean["product_category_name_english"]
)

# =========================
# 6. Crear archivo para Looker Studio
# =========================

looker_data = sales_clean[
    [
        "order_id",
        "price",
        "freight_value",
        "total_sale",
        "product_category_name_english",
        "category_es",
        "customer_state",
        "year",
        "month",
        "month_name",
        "quarter",
        "year_month"
    ]
].copy()

# =========================
# 7. Exportar
# =========================

looker_data.to_csv(
    "olist_looker.csv",
    index=False,
    encoding="utf-8-sig"
)

# =========================
# 8. Validación
# =========================

print("Archivo olist_looker.csv creado correctamente")
print(looker_data.shape)

print("\nCategorías en español:")
print(
    looker_data["category_es"]
    .value_counts()
    .sort_index()
)

print("\nCategorías que todavía quedaron sin traducir:")
not_translated = looker_data[
    looker_data["category_es"] == looker_data["product_category_name_english"]
][["product_category_name_english", "category_es"]].drop_duplicates()

print(not_translated)