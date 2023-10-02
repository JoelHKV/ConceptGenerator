
from utils.my_firebase_io import init_firebase #()
from utils.my_firebase_io import read_firebase  #(this_collection, this_document)
from utils.my_firebase_io import write_firebase #(this_collection, this_document, this_dict)

from utils.my_creds import get_openai_key

from utils.little_helpers import return_sub_dict # (whole_dict, filter_field_name, filter_value)
from utils.little_helpers import dict_to_csv #(csv_file_path, data_dict)
from utils.little_helpers import dict_to_txt #(file_path, data_dict):

from src.chatgpt_data_processor import chatgpt_concept_iterator
from src.chatgpt_data_processor import iterate_backward_connections # (concept_dict)
from src.chatgpt_data_processor import compute_concept_popularity # (concept_dict)
from src.chatgpt_data_processor import sort_concept_by_popularity # (concept_dict, popularity_dict)
from src.chatgpt_data_processor import generate_concept_rating # (openai, concept_dict, dimension)
from src.chatgpt_data_processor import generate_concept_definition #(openai, concept, length)
from src.chatgpt_data_processor import add_rating_to_concept_data #(concept_dict, rating_dict)

import openai

openai.api_key = get_openai_key()
firestore_db = init_firebase()

import time


mode='add_rate'

if mode=='generate':
    concept_end_point='leadership'
    depth = 4
    
    raw_concept_data=read_firebase(firestore_db, 'conceptBrowser', 'concepts_raw')

    raw_concept_subset = return_sub_dict(raw_concept_data, 'branch', concept_end_point)
    start_time = time.time() 
    raw_concept_subset = chatgpt_concept_iterator(openai, concept_end_point, depth, concept_end_point, raw_concept_subset)
    
    end_time = time.time() 
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print(f"Elapsed time: {elapsed_time:.6f} seconds")

    raw_concept_updated_combined_data = {**raw_concept_data, **raw_concept_subset} # latter dict takes priority in case of same keys
     
    dict_to_txt('data/raw_data.txt',raw_concept_updated_combined_data)
    write_firebase(firestore_db, 'conceptBrowser', 'concepts_raw', raw_concept_updated_combined_data)

if mode=='refine':  
    raw_concept_data=read_firebase(firestore_db, 'conceptBrowser', 'concepts_raw')
    
    raw_concept_data = {key: value for key, value in raw_concept_data.items() if value['branch'].strip().lower() != 'artificial intelligence'}
    raw_concept_data = {key: value for key, value in raw_concept_data.items() if value['branch'].strip().lower() != 'innovation'}
    
    refined_concept_data = iterate_backward_connections(raw_concept_data) # other concepts related to this concept  
    concept_popularity = compute_concept_popularity(refined_concept_data)

    refined_concept_data = sort_concept_by_popularity(refined_concept_data, concept_popularity)

    dict_to_txt('data/sort_data.txt', refined_concept_data )
    
    write_firebase(firestore_db, 'conceptBrowser', 'concepts_refined', refined_concept_data)

if mode=='rate':
    rounds = 1
    refined_concept_data = read_firebase(firestore_db, 'conceptBrowser', 'concepts_refined') 
    keys_list_this = list(refined_concept_data.keys())
    present_abstract_ratings_data = read_firebase(firestore_db, 'conceptBrowser', 'abstract_ratings')
    keys_list_present = list(present_abstract_ratings_data.keys())
    
    if keys_list_present != keys_list_this:
        present_abstract_ratings_data = {key: {'abstract': []} for key in keys_list_this} # init abstract dict in case key lists do not correspond 
    
    dimension = ['concrete', 'abstract']
    rating_dict = generate_concept_rating(openai, keys_list_this, dimension, rounds)
      
    
    for key in keys_list_this:
        present_abstract_ratings_data[key]['abstract'].append(rating_dict[key]['abstract'])
     
    dict_to_txt('data/abst_rating_data.txt', rating_dict )
    write_firebase(firestore_db, 'conceptBrowser', 'abstract_ratings', present_abstract_ratings_data)
 
if mode=='add_rate':   
    refined_concept_data = read_firebase(firestore_db, 'conceptBrowser', 'concepts_refined')
    rating_dict = read_firebase(firestore_db, 'conceptBrowser', 'abstract_ratings')
    refined_concept_data = add_rating_to_concept_data(refined_concept_data, rating_dict)
    dict_to_txt('data/final_data.txt', refined_concept_data)
    
    write_firebase(firestore_db, 'conceptBrowser', 'concepts_refined', refined_concept_data)


if mode=='define':
    definition_length = 80
    refined_concept_data = read_firebase(firestore_db, 'conceptBrowser', 'concepts_refined')
    refined_concept_data = dict(list(refined_concept_data.items()))
    for dict_index, key in enumerate(refined_concept_data):
        key = key.replace('/', '-')
        print(key)
        this_concept_refinion = read_firebase(firestore_db, 'conceptNames', key)
        if this_concept_refinion==None:
            definition_dict = generate_concept_definition(openai, key, definition_length)
            write_firebase(firestore_db, 'conceptNames', key, definition_dict)    
            print(dict_index, key)
        
    

