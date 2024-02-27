# Import modules
import qdrant_client
import requests
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import Batch
import numpy as np

# Reading text
with open('/Users/tatianagarcia/Documents/proyecto_MLII/machine_learning_II/workshop_III/StephenKing_Cell.txt', 'r') as archivo:
    # Lee el contenido del archivo y lo almacena en una variable
    contenido = archivo.read()
    
# Eliminar saltos de línea
contenido = contenido.replace('\n', ' ')

# Split the text into paragraphs based on double line breaks ('\n\n')
parrafos = contenido.split('.')



# Seleccionar aleatoriamente 2048 oraciones
oraciones_reducidas = parrafos[:2048]

print('primer párrafo', len(parrafos))
# print('cantidad párrafos', len(parrafos))
print('primer párrafo', len(oraciones_reducidas))


def embedding_creation(oraciones):

    API_KEY = 'jina_ead3918f8bb748a587da01973afff04cJEi24j0RHWLJMlrby0uHDvwhDgSd'

    MODEL = "jina-embeddings-v2-base-es"  # or "jina-embeddings-v2-base-en"

    # Get embeddings from the API
    url = "https://api.jina.ai/v1/embeddings"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    data = {
        "input": oraciones,
        "model": MODEL,
    }

    response = requests.post(url, headers=headers, json=data)
    print(response)
    embeddings = [d["embedding"] for d in response.json()["data"]]

    return embeddings


# Realizar una búsqueda por similitud de vectores
EMBEDDING_SIZE = 768  # 512 for small variant
embeddings_texto = embedding_creation(oraciones_reducidas)

# Index the embeddings into Qdrant
qdrant_client = qdrant_client.QdrantClient(":memory:")
qdrant_client.create_collection(
    collection_name="MyCollection",
    vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.DOT),
)

qdrant_client.upsert(
    collection_name="MyCollection",
    points=Batch(
        ids=list(range(len(embeddings_texto))),
        vectors=embeddings_texto,
    ),
)


consulta = ['Dónde vive Clay']
embedding_consulta = embedding_creation(consulta)
print('embedding consulta:', embedding_consulta)

results = qdrant_client.search(
    collection_name="MyCollection",
    query_vector = np.squeeze(embedding_consulta),
     limit=3  # Obtener los 10 vectores más similares
    )

print(results)


# Dividir la cadena por comas y obtener la parte que contiene el ID
id_vectors = []
for resultado in results:
    id_vector = resultado.id
    id_vectors.append(id_vector)


# Imprimir la respuesta
for id in id_vectors:
    print("Respuesta:", oraciones_reducidas[id])
