
from ast import Pass
from utils.my_firebase_io import init_firebase #()
from utils.my_firebase_io import read_firebase  #(this_collection, this_document)
from utils.my_firebase_io import write_firebase #(this_collection, this_document, this_dict)

from utils.my_creds import get_openai_key

from utils.little_helpers import dict_to_json #(file_path, data_dict)
from utils.little_helpers import json_to_dict #(file_path)
from utils.little_helpers import get_sample_underpresented # (dimension_rating_data, dimension_name, dimension, sample_size)
from utils.little_helpers import dict_to_numpy #(dict_data, key_data, max_nro_values)  

from utils.statistics import compute_icc #(numpy array) .shape[0] = items, .shape[1] = repeated measurements 


from src.chatgpt_data_processor import chatgpt_concept_iterator
from src.chatgpt_data_processor import iterate_backward_connections # (concept_dict)
from src.chatgpt_data_processor import compute_concept_popularity # (concept_dict)
from src.chatgpt_data_processor import sort_concept_by_popularity # (concept_dict, popularity_dict)
from src.chatgpt_data_processor import generate_concept_rating # (openai, concept_dict, dimension)
from src.chatgpt_data_processor import generate_concept_definition #(openai, concept, length)
from src.chatgpt_data_processor import add_rating_to_concept_data #(concept_dict, rating_dict)

from src.chatgpt_data_processor import generate_alphabetical_rating #(concept_keys):

import openai

openai.api_key = get_openai_key()
firestore_db = init_firebase()

import os
import time
import json
import random

folder = 'data'
raw_files = 'raw_concept_data_'
refined_file = 'combined_refined_concept_data.txt'
dimension_rating_file = 'dimension_rating_data.txt'
final_connection_data_file = 'final_connection_data.txt'

mode='write_to_firestore'

if mode=='generate_connections':
    start_depth = 0
    end_depth = 3
    run_for_sec_before_save = 10
    starting_concept='problem solving'
    file_path= folder +  '/' + raw_files + starting_concept.replace(' ', '_') + '.txt'
    raw_concept_dict = json_to_dict(file_path)           
    keep_going = True
    while keep_going:        
        return_time = time.time() + run_for_sec_before_save
        raw_concept_dict = chatgpt_concept_iterator(openai, starting_concept, start_depth, end_depth, starting_concept, raw_concept_dict, return_time)              
        dict_to_json(file_path, raw_concept_dict)        
        keep_going = time.time() > return_time
        print('saving now...')
        
if mode=='combine_data_and_refine':
    combined_concept_dict = {}
    all_files = os.listdir(folder)
    matching_files = [file for file in all_files if file.startswith(raw_files) and file.endswith('.txt')]    
    for filename in matching_files:
        this_raw_concept_dict = json_to_dict(folder +  '/' + filename)
        for dict_index, key in enumerate(this_raw_concept_dict):
            if key in combined_concept_dict:
                combined_concept_dict[key]['branch'].append(this_raw_concept_dict[key]['branch'][0])
            else:
                combined_concept_dict[key] = this_raw_concept_dict[key]         
    
    refined_concept_data = iterate_backward_connections(combined_concept_dict) # other concepts related to this concept  
    concept_popularity = compute_concept_popularity(refined_concept_data)

    refined_concept_data = sort_concept_by_popularity(refined_concept_data, concept_popularity)
    dict_to_json(folder +  '/' + refined_file, refined_concept_data)
    
if mode=='create_evaluation_ratings':
    required_sample = 8
    dimension = ['concrete', 'abstract']
    
    #dimension = ['simple', 'complex']
    #dimension = ['alphabetical', 'alphabetical']

    dimension_name = dimension[1]
    
    append_existing_rating_data = True
    
    refined_concept_data = json_to_dict(folder +  '/' + refined_file) 
    refined_concept_keys = list(refined_concept_data.keys()) # these concept we want to rate
    
    if append_existing_rating_data:
        dimension_rating_data = json_to_dict(folder +  '/' + dimension_rating_file)
    else:
        print('init')
        dimension_rating_data = {} 
        for key in refined_concept_keys:
            dimension_rating_data[key]={}
            dimension_rating_data[key][dimension_name]=[]
    
    for key in refined_concept_keys:
        dimension_rating_data.setdefault(key, {})   
        dimension_rating_data[key].setdefault(dimension_name, [])

    smallest_sample = 0
    while smallest_sample<required_sample:
        value = get_sample_underpresented(dimension_rating_data, dimension_name, dimension, 110)
        random_keys_list, smallest_sample = value
        if dimension_name!='alphabetical': # normal ChatGPT run
            rating_dict = generate_concept_rating(openai, random_keys_list, dimension)
        else: # contrasted to alphabetical sorting that emulates perfect measurements for statistical testing 
            rating_dict = generate_alphabetical_rating(random_keys_list)
        for key in rating_dict:
            dimension_rating_data[key][dimension_name].append(rating_dict[key]['value'])  
        dict_to_json(folder +  '/' + dimension_rating_file, dimension_rating_data)


if mode=='intraclass_CC_for_evaluation_ratings':

    dimension_rating_data = json_to_dict(folder +  '/' + dimension_rating_file)

    nro_measurements_per_concepts = 8
    this_dimension = 'abstract' # the concept to be evaluated
    evaluation_rating_data = dict_to_numpy(dimension_rating_data, this_dimension, nro_measurements_per_concepts)
    
    # emulate perfect measurements with alphabetically sorted concepts, find the theoretical maximum value
    alphabetical_rating_data = json_to_dict(folder +  '/dimension_rating_data_alphabetical.txt')
    alphabetical_evaluation_data = dict_to_numpy(alphabetical_rating_data, 'alphabetical', nro_measurements_per_concepts)

    icc_test = round(compute_icc(evaluation_rating_data), 2)
    icc_theoretical= round(compute_icc(alphabetical_evaluation_data), 2)
    print("Intraclass Correlation Coefficient (ICC):", icc_test, ". Theoretical maximum ICC for this measurement:",  icc_theoretical)  
    
if mode=='show_most_concrete_or_abstract_concepts':
    abstract=False
    nro_concepts_to_show = 10
    dimension_rating_data = json_to_dict(folder +  '/' + dimension_rating_file)
    rating_averages = []
    for key in dimension_rating_data:
        this_rating_array = dimension_rating_data[key]['abstract']
        rating_average = sum(this_rating_array) / len(this_rating_array)
        rating_averages.append((key, rating_average)) 
    print(len(rating_averages))         
    rating_averages.sort(key=lambda x: x[1], reverse=abstract)
    top_10 = rating_averages[:nro_concepts_to_show]
    for key, rating_average in top_10:
        print(f"{key}, Rating: {round(rating_average, 2)}")
        
if mode=='combine_final_file':
    ratings_to_be_included=['all']
    
    refined_concept_data = json_to_dict(folder +  '/' + refined_file)
    
    if len(ratings_to_be_included)==0:
        dict_to_json(folder +  '/' + final_connection_data_file, refined_concept_data)
    else:
 
        dimension_rating_data = json_to_dict(folder +  '/' + dimension_rating_file)
    
        if ratings_to_be_included[0]=='all':
            first_main_key = next(iter(dimension_rating_data.keys()))
            ratings_to_be_included = list(dimension_rating_data[first_main_key].keys())
        
        for this_rating in ratings_to_be_included:
            refined_concept_data_with_dimension_rating = add_rating_to_concept_data(refined_concept_data, dimension_rating_data, this_rating)
        dict_to_json(folder +  '/' + final_connection_data_file, refined_concept_data_with_dimension_rating) 

if mode=='write_to_firestore':
    refined_concept_data_with_dimension_rating = json_to_dict(folder +  '/' + final_connection_data_file)
    for key in refined_concept_data_with_dimension_rating:
        nested_list = refined_concept_data_with_dimension_rating[key]['branch']
        flat_list = [item for sublist in nested_list for item in sublist]
        refined_concept_data_with_dimension_rating[key]['branch']=flat_list
        
    chunk_to_save = {}
    chunk_nro = 0
    chunk_size = 200000
    for key in refined_concept_data_with_dimension_rating:
        chunk_to_save[key]=refined_concept_data_with_dimension_rating[key]      
        json_str = json.dumps(chunk_to_save, ensure_ascii=False)
        size_in_characters = len(json_str)
        if (size_in_characters>chunk_size):
            print(chunk_nro)
            write_firebase(firestore_db, 'conceptBrowser', 'finalConceptData_' + str(chunk_nro), chunk_to_save)
            chunk_to_save = {}
            chunk_nro=chunk_nro+1
    write_firebase(firestore_db, 'conceptBrowser', 'finalConceptData_' + str(chunk_nro), chunk_to_save)
 
if mode=='define':
    definition_length = 80

    refined_concept_data = json_to_dict(folder +  '/' + refined_file) 
    refined_concept_keys = list(refined_concept_data.keys()) # these concept we want to define

    for dict_index, key in enumerate(refined_concept_keys):
        key = key.replace('/', '-')
        this_concept_refinion = read_firebase(firestore_db, 'conceptNames', key)
        if this_concept_refinion==None:
            definition_dict = generate_concept_definition(openai, key, definition_length)
            write_firebase(firestore_db, 'conceptNames', key, definition_dict)    
            print(dict_index, key)
        
    

