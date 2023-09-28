from src.chatgpt_prompt_functions import create_related_concepts # (openai, concept, nro) returns nro co
from src.chatgpt_prompt_functions import sort_concepts_along_dimension # (openai, concept_array, dimension)
from src.chatgpt_prompt_functions import create_definition # (openai, concept, nro_words)



def chatgpt_concept_iterator(openai, concept, depth, branch, concept_dict):
    if depth == 0:
        return
    if concept in concept_dict:
        new_concepts = concept_dict[concept]['concepts']
    else:
        new_concepts = create_related_concepts(openai, concept,8)
        concept_dict[concept] = {}
        concept_dict[concept]['branch'] = branch
        concept_dict[concept]['concepts'] = new_concepts
    for this_concept in new_concepts:
        chatgpt_concept_iterator(openai, this_concept, depth - 1, branch, concept_dict)

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


def generate_concept_rating(openai, concept_dict, dimension, rounds):
    import random
    rating_dict = {}
    for dict_index, key in enumerate(concept_dict):
        rating_dict[key]={}
        rating_dict[key]['abstract']=0
        for in_concept in concept_dict[key]['ordered_concepts']:
            in_concept = in_concept.replace('_', '').replace('*', '').replace("'", "")
            rating_dict[in_concept]={}
            rating_dict[in_concept]['abstract']=0
    
    
    for i in range(rounds):
        all_keys = list(rating_dict.keys())
        random.shuffle(all_keys)
        print(all_keys)
        lenlen=len(all_keys)
        step=9

        while lenlen>0:
            if lenlen % 10 == 0:
                step=10
            concept_array=all_keys[:step]       
            sorted_concepts = sort_concepts_along_dimension(openai, concept_array, dimension) 
            print(lenlen, sorted_concepts)
            for ind, this_concept in enumerate(sorted_concepts):
                value = (1+ind)/step/rounds             
                rating_dict[this_concept]['abstract'] += value
                
            all_keys[:step]=[]
            lenlen=len(all_keys)

    return rating_dict


def add_rating_to_concept_data(concept_dict, rating_dict):
    for dict_index, key in enumerate(concept_dict):
        abstract_rating = int(100*rating_dict[key]['abstract'])   
        concept_dict[key]['abstract']=abstract_rating

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



 