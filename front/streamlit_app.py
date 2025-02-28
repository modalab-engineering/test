import streamlit as st
import requests

# Agregar estilos CSS personalizados para las tarjetas
st.markdown("""
    <style>
    .card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        height: 500px;  /* Altura fija para todas las tarjetas */
        width: 100%;
        margin: 10px;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: top;
    }
    .card img {
        height: 350px;  /* Altura máxima para la imagen */
        object-fit: cover;
        width: 100%;
        border-radius: 5px;
    }
    .card-title {
        font-size: 1.1em;
        font-weight: bold;
        margin: 10px 0 0 0;
    }
    .card-designer {
        font-size: 0.9em;
        color: #555;
    }
    </style>
""", unsafe_allow_html=True)

# URL del endpoint GraphQL
graphql_url = "https://server.modalab.co/graphql"

def get_products_details(ids):
    query = """
    query ListProducts($filters: FilterProductsInput) {
      listProducts(filters: $filters) {
        products {
          name
          main_image
          designer_name
        }
      }
    }
    """
    variables = {
        "filters": {
            "ids": ids
        }
    }
    response = requests.post(graphql_url, json={"query": query, "variables": variables})
    result = response.json()
    products = result.get("data", {}).get("listProducts", {}).get("products", [])
    return products

st.title('Buscador con IA')
text = st.text_input('Ingresa una descripción')

if st.button('Buscar'):
    # Realizamos la búsqueda inicial para obtener una lista de IDs
    response = requests.post(
        'https://api.ai.modalab.co/search/description',
        json={'text': text, 'top_k': 10}
    )
    ids_data = response.json()
    
    if isinstance(ids_data, list) and len(ids_data) > 0:
        # Extraemos los IDs
        ids = [item.get('id') for item in ids_data]
        products = get_products_details(ids)
        
        if products:
            num_columns = 3
            cols = st.columns(num_columns)
            
            for index, product in enumerate(products):
                col = cols[index % num_columns]
                # Construir la tarjeta en HTML
                image_url = product.get('main_image') or "https://via.placeholder.com/300x150?text=No+Image"
                card_html = f"""
                <div class="card">
                    <img src="{image_url}" alt="{product.get('name')}" />
                    <div>
                        <div class="card-title">{product.get('name')}</div>
                        <div class="card-designer">Designer: {product.get('designer_name')}</div>
                    </div>
                </div>
                """
                with col:
                    st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.write("No se encontraron detalles para los productos.")
    else:
        st.write("No se encontraron resultados")
