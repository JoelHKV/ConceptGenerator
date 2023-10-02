from src.chatgpt_prompt_functions import create_related_concepts # (openai, concept, nro) returns nro co
from src.chatgpt_prompt_functions import sort_concepts_along_dimension # (openai, concept_array, dimension)
from src.chatgpt_prompt_functions import create_definition # (openai, concept, nro_words)

import time

def chatgpt_concept_iterator(openai, concept, current_depth, max_depth, branch, concept_dict, return_time):
    if current_depth > max_depth:
        return  
    current_time = time.time() 
    if current_time > return_time:
        return 
    if concept in concept_dict:
        new_concepts = concept_dict[concept]['concepts']
    else:
        print(concept)
        new_concepts = create_related_concepts(openai, concept, 9)  # Request 9 concepts
        if concept in new_concepts:  # ChatGPT sometimes returns the initial concept
            new_concepts.remove(concept)  # If so, remove it
        else:
            new_concepts.pop()  # Otherwise, remove the last item to keep the array 8 items long
        concept_dict[concept] = {}
        concept_dict[concept]['branch'] = [(branch, current_depth)]
        concept_dict[concept]['concepts'] = new_concepts

    for this_concept in new_concepts:
        chatgpt_concept_iterator(openai, this_concept, current_depth + 1, max_depth, branch, concept_dict, return_time)

    return concept_dict 

def iterate_backward_connections(concept_dict):
    keys_list = list(concept_dict.keys())
    for dict_index, key in enumerate(concept_dict):
        concept_dict[key]['backward_concepts'] = []    
    for dict_index, key in enumerate(concept_dict):
        for in_concept in concept_dict[key]['concepts']:       
            if in_concept in keys_list: # and key not in concept_dict[in_concept]['concepts']
                concept_dict[in_concept]['backward_concepts'].append(key)
    for dict_index, key in enumerate(concept_dict):
        concepts = concept_dict[key]['concepts']
        backward_concepts = concept_dict[key]['backward_concepts']               
        concept_dict[key]['backward_concepts'] = [item for item in backward_concepts if item not in concepts]
    return concept_dict 


def compute_concept_popularity(concept_dict):
    popularity_dict = {}
    for dict_index, key in enumerate(concept_dict):
        for in_concept in (concept_dict[key]['concepts'] + concept_dict[key]['backward_concepts']):         
            if in_concept in popularity_dict:
                popularity_dict[in_concept]['value']=popularity_dict[in_concept]['value']+1
            else:
                popularity_dict[in_concept] ={}
                popularity_dict[in_concept]['value'] = 1
                
    keys_list = list(concept_dict.keys())
    for dict_index, key in enumerate(popularity_dict):
        if key in keys_list:
            popularity_dict[key]['iskey']=1
            popularity_dict[key]['value']=popularity_dict[key]['value']+100
        else:
            popularity_dict[key]['iskey']=0

    return popularity_dict
        #for in_concept in concept_dict[key]['backward_concepts']:   


def sort_concept_by_popularity(concept_dict, popularity_dict):
    keys_list = list(concept_dict.keys())
    for dict_index, key in enumerate(concept_dict):
        popularity_list = []
        for in_concept in (concept_dict[key]['concepts'] + concept_dict[key]['backward_concepts']):
            popularity_list.append(popularity_dict[in_concept]['value'])
        sorted_indexes_descending = [index for index, value in sorted(enumerate(popularity_list), key=lambda x: x[1], reverse=True)]
        sorted_concepts = []
        concepts_flags = []
        nro_concepts = len(concept_dict[key]['concepts'])
        for index, value in enumerate(sorted_indexes_descending[:nro_concepts]):
            iskey = '1' if (value < nro_concepts and concept_dict[key]['concepts'][value] in keys_list) or (value >= nro_concepts and concept_dict[key]['backward_concepts'][value - nro_concepts] in keys_list) else '0'
    
            if value < nro_concepts:
                sorted_concepts.append(concept_dict[key]['concepts'][value])
                concepts_flags.append(iskey + 'F')
            else:
                sorted_concepts.append(concept_dict[key]['backward_concepts'][value - nro_concepts])
                concepts_flags.append(iskey + 'B')



       
        concept_dict[key]['ordered_concepts'] = sorted_concepts
        #concept_dict[key]['flags'] = concepts_flags 
      
    concept_dict = {key: {inner_key: inner_value for inner_key, inner_value in value.items() if inner_key != 'concepts'} for key, value in concept_dict.items()}
    concept_dict = {key: {inner_key: inner_value for inner_key, inner_value in value.items() if inner_key != 'backward_concepts'} for key, value in concept_dict.items()}

    return concept_dict   



def generate_concept_rating(openai, concept_keys, dimension):
    rating_dict = {}  
    for i in range(0, len(concept_keys), 11):
        batch_keys = concept_keys[i:i+11]
        modified_batch_keys = [key.replace("'", "") for key in batch_keys]
        
        sorted_concepts = sort_concepts_along_dimension(openai, modified_batch_keys, dimension)
        for ind, (original_key, modified_key) in enumerate(zip(batch_keys, sorted_concepts)):
            rating_dict[original_key] = {}
            rating_dict[original_key]['value'] = ind/10
    return rating_dict


def generate_concept_rating2(openai, concept_keys, dimension):
    rating_dict = {}
    
    for i in range(0, len(concept_keys), 11):
        batch_keys = concept_keys[i:i+11]
        
        # Modify batch keys for sorting (remove special characters)
        modified_batch_keys = [key.replace("'", "") for key in batch_keys]
        
        # Sort the modified concepts
        sorted_concepts = sort_concepts_along_dimension(openai, modified_batch_keys, dimension)
        
        for ind, (original_key, modified_key) in enumerate(zip(batch_keys, sorted_concepts)):
            rating_dict[original_key] = {}
            rating_dict[original_key]['value'] = ind/10
    
    return rating_dict
 








def add_rating_to_concept_data(concept_dict, rating_dict, what_rating):
    for dict_index, key in enumerate(concept_dict):
        this_rating_array = rating_dict[key][what_rating]
        rating_average = sum(this_rating_array) / len(this_rating_array)
        abstract_rating = int(100*rating_average)   
        concept_dict[key][what_rating]=abstract_rating

    return concept_dict



def generate_concept_definition(openai, concept, length):
    import datetime         
    concept_definition = create_definition(openai, concept, length)
    date = datetime.datetime.now()
    this_dict= {
        'definition': concept_definition,
        'model': 'ChatGPT 3.5',
        'date': date,
        }
    return this_dict



 