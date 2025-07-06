import logging
from apscheduler.schedulers.background import BackgroundScheduler
from config.config import settings
from infrastructure.database import SessionLocal
from infrastructure.dependencies.vector_db import get_client, get_existing_ids
from transformers import CLIPProcessor, CLIPModel
import torch
import requests
from io import BytesIO
from PIL import Image
import numpy as np
from sqlalchemy import text

logger = logging.getLogger(__name__)

logger.info("Cargando modelo CLIP y processor...")
try:
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    clip_model.eval()
    logger.info("Modelo CLIP y processor cargados correctamente.")
except Exception as e:
    logger.error("Error al cargar CLIP model o processor: %s", e)
    raise e

def generate_image_embedding(image_url: str):
    logger.info("Generando embedding para la imagen: %s", image_url)
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        inputs = clip_processor(images=img, return_tensors="pt")
        with torch.no_grad():
            features = clip_model.get_image_features(**inputs)
        normalized_features = features / features.norm(p=2, dim=-1, keepdim=True)
        return normalized_features
    except Exception as e:
        logger.error("Error generando embedding para %s: %s", image_url, e)
        raise e

def process_products():
    logger.info("Iniciando proceso de indexación de productos...")
    db = SessionLocal()
    client = get_client()
    collection_name = settings.VERTEX_INDEX_ENDPOINT
    try:
        query = text("SELECT * FROM products")
        result = db.execute(query)
        
        existing_ids = get_existing_ids(client, collection_name)
        logger.info("IDs existentes en Vertex: %d", len(existing_ids))

        product_count = 0
        indexed_count = 0
        for row in result:
            product_count += 1
            product_data = dict(row._mapping)
            product_id = product_data.get("id")
            main_image_url = product_data.get("main_image")
            if not main_image_url:
                logger.warning("Producto %s sin imagen principal", product_id)
                continue
            if product_id in existing_ids:
                logger.info("Producto %s ya indexado.", product_id)
                continue
            try:
                embedding = generate_image_embedding(main_image_url)
                embedding_list = np.array(embedding.detach().numpy()).flatten().tolist()
                point = {
                    "id": product_id,
                    "vector": embedding_list,
                    "payload": product_data,
                }
                client.upsert(collection_name=collection_name, points=[point])
                indexed_count += 1
                logger.info("Producto %s indexado en Vertex.", product_id)
            except Exception as e:
                logger.error("Error indexando producto %s: %s", product_id, e)

        logger.info("Total de productos procesados: %d. Nuevos productos indexados: %d", product_count, indexed_count)
    except Exception as e:
        logger.error("Error en el proceso de indexación: %s", e)
    finally:
        db.close()
        logger.info("Finalizado proceso de indexación.")

def start_indexing_job():
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_products, 'interval', hours=24)
    scheduler.start()
    logger.info("Scheduler de indexación iniciado.")
    return scheduler  # Se retorna el scheduler para poder detenerlo en el shutdown
