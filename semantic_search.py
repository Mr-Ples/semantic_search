from typing import List

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

import constants


def main(query: List[str]):
    client = chromadb.Client(
        Settings(
            chroma_db_impl=constants.CHROMA_DB_IMPL,
            persist_directory=constants.CHROMA_PERSIST_DIR
        )
    )
    model = SentenceTransformer(constants.EMBEDDING_MODEL)
    collection = client.get_collection(name=constants.COLLECTION_NAME, embedding_function=lambda text: model.encode(text))
    results = collection.query(
        query_texts=query,
        where={"doc_type": "document"},
        n_results=min(collection.count(), 100)
    )
    datas = {}
    documents = {}
    print(results.keys())
    for index, idd in enumerate(results['ids'][0]):
        datas[idd] = {'text': results['documents'][0][index], 'metadata': results['metadatas'][0][index], 'distance': results['distances'][0][index]}

    # get all relevant docuemnts + link
    for idd, datasss in datas.items():
        page = idd.split("-")[-1]
        doc_id = idd[:-len('-' + page)]
        if documents.get(doc_id):
            continue
        doc_type = datasss['metadata']['doc_type']
        documents[doc_id] = {'header': datasss['metadata']['doc_name'].replace('.pdf', ''), 'link': f'https://docs.google.com/{doc_type}/d/' + doc_id}
    for idd, docuss in documents.items():
        print(docuss)

    # print(datas)
    # print(documents)
    # get all revelant pages
    for idd, datasss in datas.items():
        print(datasss)
        page = idd.split("-")[-1]
        doc_id = idd[:-len('-' + page)]
        print(doc_id)
        print()
        print("Name:", datasss['metadata']['doc_name'])
        print("Page:", page)
        print("Url:", datasss['metadata']['link'])
        print("Distance:", datasss['distance'])
        print(datasss['text'][:100])
    # print(documents)
    return datas, documents


if __name__ == "__main__":
    main(['delete account'])
