#Import modules
from sentence_transformers import SentenceTransformer
import qdrant_client
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import Batch
import numpy as np
import os

class EMBEDDINGS:
    """
    This class is used to generate and manipulate embeddings using the Qdrant client.
    """

    #construction
    def __init__(self):
        """
        Initializes the EMBEDDINGS class.

        Params:
            None
        """
        self.qdrant_client = qdrant_client.QdrantClient(":memory:")
        self.content = None
        self.created_collections = set()

    def _get_paragraphs(self, filename):
        """
        Reads a file and splits the content into paragraphs.

        Params:
            filename (str): The name of the file to read.

        Returns:
            paragraphs (list): A list of paragraphs from the file.
        """

        #Get current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_dir =script_dir.replace('models','files')
        file_path  = os.path.join(script_dir, filename)

        #Reading text
        with open(file_path, 'r', encoding='utf-8') as archivo:
            # Lee el contenido del archivo y lo almacena en una variable
            content = archivo.read()

        # Remove line breaks
        self.content = content.replace('\n', ' ')
        # Split the text into paragraphs based on double line breaks ('\n\n')
        paragraphs = self.content.split('.')
        return paragraphs
    

    def _model_embedding(self, content):
        """
        Generates embeddings for the given content using SentenceTransformer.

        Params:
            content (str): The content to generate embeddings for.

        Returns:
            embeddings (numpy.ndarray): The generated embeddings.
        """

        model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        embeddings = model.encode(content)
        return embeddings


        # Index the embeddings into Qdrant
    def _qdrant_collection(self):
        """
        Creates a new collection in Qdrant or overwrites an existing one.

        Params:
            None

        Returns:
            None
        """
        EMBEDDING_SIZE = 768  # 512 for small variant
        collection_name = "MyCollection"

        if collection_name in self.created_collections:
            #The collection already exists, we can choose to overwrite it or perform some other action
            self.qdrant_client.delete_collection(collection_name)

        self.qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
        )

        #Add the collection name to the list of created collections
        self.created_collections.add(collection_name)


    def _update_vectors(self, embeddings):
        """
        Updates the vectors in the Qdrant collection with the given embeddings.

        Params:
            embeddings (numpy.ndarray): The embeddings to update the vectors with.

        Returns:
            None
        """
        self.qdrant_client.upsert(
            collection_name="MyCollection",
            points=Batch(
                ids=list(range(len(embeddings))),
                vectors=embeddings,
            ),
        )

    def _search_embeddings(self, consult):
        """
        Searches for embeddings in the Qdrant collection that are similar to the given consult.

        Params:
            consult (str): The consult to search for similar embeddings.

        Returns:
            results (list): A list of search results.
        """
        embeddings = self._model_embedding(consult)
        results = self.qdrant_client.search(
            collection_name="MyCollection",
            query_vector = np.squeeze(embeddings),
            limit=3
            )
        
        return results
    
    
    def search_embeddings_content(self, filename):
        """
        Reads a file, generates embeddings for the content, creates a Qdrant collection, and updates the vectors with the embeddings.

        Params:
            filename (str): The name of the file to read.

        Returns:
            None
        """
        paragraphs = self._get_paragraphs(filename)
        embeddings = self._model_embedding(paragraphs)
        self._qdrant_collection()
        self._update_vectors(embeddings)
    
    def search_paragraphs(self, consult,filename):
        """
        Searches for paragraphs in a file that are similar to the given consult.

        Params:
            consult (str): The consult to search for similar paragraphs.
            filename (str): The name of the file to search in.

        Returns:
            answers (list): A list of paragraphs that are similar to the consult.
        """
        print('consult', consult)
        results = self._search_embeddings(consult)
        #Split the string by commas and get the part that contains the ID
        id_vectors = []
        for resultado in results:
            id_vector = resultado.id
            id_vectors.append(id_vector)

        paragraphs = self._get_paragraphs(filename)
        answers = []
        #Print the answer
        for id in id_vectors:
            print("Respuesta:", paragraphs[id])
            answers.append(paragraphs[id])

        return answers