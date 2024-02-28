#Import modules
from sentence_transformers import SentenceTransformer
import qdrant_client
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import Batch
import numpy as np
import os

class EMBEDDINGS:
        #Constructor
    def __init__(self):
        self.qdrant_client = qdrant_client.QdrantClient(":memory:")
        self.content = None
        self.created_collections = set()

    def _get_paragraphs(self, filename):

        # Obtener el directorio del script actual
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_dir =script_dir.replace('models','files')
        file_path  = os.path.join(script_dir, filename)

        # Reading text
        with open(file_path, 'r') as archivo:
            # Lee el contenido del archivo y lo almacena en una variable
            content = archivo.read()

        # Eliminar saltos de línea
        self.content = content.replace('\n', ' ')
        # Split the text into paragraphs based on double line breaks ('\n\n')
        paragraphs = self.content.split('.')
        return paragraphs

    def _model_embedding(self, content):  
        model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        embeddings = model.encode(content)
        return embeddings


        # Index the embeddings into Qdrant
    def _qdrant_collection(self):
        EMBEDDING_SIZE = 768  # 512 for small variant
        collection_name = "MyCollection"

        if collection_name in self.created_collections:
            # La colección ya existe, podemos optar por sobrescribirla o realizar alguna otra acción
            self.qdrant_client.delete_collection(collection_name)

        self.qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
        )

        # Agregar el nombre de la colección a la lista de colecciones creadas
        self.created_collections.add(collection_name)


    def _update_vectors(self, embeddings):
        self.qdrant_client.upsert(
            collection_name="MyCollection",
            points=Batch(
                ids=list(range(len(embeddings))),
                vectors=embeddings,
            ),
        )

    def _search_embeddings(self, consult):
        embeddings = self._model_embedding(consult)
        results = self.qdrant_client.search(
            collection_name="MyCollection",
            query_vector = np.squeeze(embeddings),
            limit=3  # Obtener los 10 vectores más similares
            )
        
        return results
    
    
    def search_embeddings_content(self, filename):
        paragraphs = self._get_paragraphs(filename)
        embeddings = self._model_embedding(paragraphs)
        self._qdrant_collection()
        self._update_vectors(embeddings)
    
    def search_paragraphs(self, consult,filename):
        print('consult', consult)
        results = self._search_embeddings(consult)
        # Dividir la cadena por comas y obtener la parte que contiene el ID
        id_vectors = []
        for resultado in results:
            id_vector = resultado.id
            id_vectors.append(id_vector)

        paragraphs = self._get_paragraphs(filename)
        answers = []
        # Imprimir la respuesta
        for id in id_vectors:
            print("Respuesta:", paragraphs[id])
            answers.append(paragraphs[id])

        return answers


        #https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2
            

# consulta = ['Dónde se produjo una explosión']
# # consulta = ['Cuál es la melodia que le gustaba a Johny']
# file_path='Stephen King - Cell (1).txt'
# model = EMBEDDINGS()
# model.search_embeddings_content(file_path)
# model.search_paragraphs(consulta, file_path)
#         # print('embedding consulta:', embedding_consulta)
