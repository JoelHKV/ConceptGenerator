# Concept Generator

## General Information

Concept Generator utilizes ChatGPT 3.5 to generate multifaceted data 
about concepts, which are fundamental building blocks in thinking. 
The project yields three types of data:

- Relational (i.e., how concepts relate to one another)
- Comparative (i.e., how concepts rate along specific continua)
- Descriptive (i.e., what do different concepts mean?)

The outcome of the project is a Google Firestore database that provides
easy and efficient access to the generated data. In fact, 
[ConceptExplorer](https://github.com/JoelHKV/ConceptExplorer) is a web 
app that utilizes the data generated in this project in a user-friendly manner.

## Introduction

Concepts are the foundation of human thinking and understanding. 
They allow us to make sense of the world by organizing information 
into meaningful categories. While we grasp many concepts, 
our understanding of them is often intuitive rather than explicit. 
For example, explaining what 'the mind' truly is can be challenging.

The Concept Generator project takes a systematic approach to the 
world of concepts by harnessing the power of ChatGPT 3.5. 
With Concept Generator, you can:

- Initiate the creation of an interrelated concept network from a user-defined starting concept
- Evaluate concepts across any dimension, providing valuable insights into the spectrum of thought
- Generate clear and concise summaries for each concept, making complex ideas more accessible
 
The project produces data that can be useful for:

- Learning new concepts
- Enhancing the understanding of concepts already known
- Acquiring knowledge about the interconnections between concepts
- Categorizing and rating concepts across various dimensions

In essence, the data generated by this project can improve one's conceptual thinking skills, better equipping individuals to interact with the world around them.

The project is designed for learners, educators, researchers, and anyone curious about the intricacies of human thought.

Additionally, explore [ConceptExplorer](https://github.com/JoelHKV/ConceptExplorer), the application-side sister project that complements this endeavor.
 
## Getting Started
To run this project locally, follow these 5 steps:

1. **Installation:**
Ensure you have Python 3.9.5 or a more recent version installed on your system.

2. **Clone the Repository:**
```
git clone https://github.com/JoelHKV/ConceptGenerator.git
```
3. **Install Dependencies:**
Navigate to the project directory and install dependencies:
```
pip install -r requirements.txt
```
4. **Configuration:**
Set up API keys. Refer Section [API Keys](#api-keys) for details.

5. **Run the Project:**
Execute the main script ```ConceptGenerator.py ```. Refer Section [Data Generation and Post-Processing](#data-generation-and-post-processing) for details.

6. **Explore the Output:**
Check the project's output at Google Firestore or local files saved in the data-folder.

## Technologies Used
Concept Generator is written in Python and utilizes Firestore, a cloud-based NoSQL database service, for data management.
## Folder Structure
The project directory is organized as follows:

* ConceptGenerator.py: The entry point
* src/: Contains functions for data processing
* utils/: Holds utility functions for credentials etc
* data/: Stores local data files


## Data Generation and Post-Processing
All data generation and post-processing are done in ```ConceptGenerator.py ```.
The script is meant to be run one step at the time, and all the steps will 
be explained in the next subchapters.

### Generate Interconnected Concepts with ChatGPT 
To run this step, set ```mode='generate_connections'``` in ```ConceptGenerator.py ```. 
Also, specify a starting concept (e.g., ```starting_concept='mind'```) 
and the end recursion depth (e.g., ```end_depth = 3```). 
The start depth should always be set to 0 (i.e., ```start_depth = 0```).

The iteration begins with the starting concept (Level 0), which is 
first input into ChatGPT to generate 8 related concepts (Level 1). 
Each of these related concepts is then fed into ChatGPT to generate 
even more related concepts (Level 2). The iteration continues until 
the desired recursion depth is reached (e.g., ```end_depth = 3```).

In theory, the algorithm yields 8 times more concepts for each iteration. 
In practice, however, concepts start reappearing, and since the algorithm 
does not need to recompute them, the overall computational complexity 
increases less. The actual increase per depth level depends, for example, 
on the internal consistency of the starting concept.

The script outputs a dictionary that contains the starting concept and 
all iterated concepts. One key-value pair looks like this:

```"perception": {"branch": [["truth", 2]], "concepts": ["sensation", "awareness", "interpretation", "cognition", "attention", "stimulus", "consciousness", "recognition"]}```

The first item in 'branch' array is the starting concept that yielded
this concept. The second item is the recursion depth at which 
this concept appeared (e.g., 1 = direct child of the starting concept).
The 'concepts' is an 8-item array where each item is one related 
concept (direct child of the concept).

We ran the script for the following starting concepts: 
artificial intelligence, energy, hierarchy, identity, 
innovation, interdependence, justice, leadership, mind, problem solving, truth

Each run resulted in a dictionary that was saved locally as:
`data/raw_concept_data_[STARTING CONCEPT].txt`

where `STARTING CONCEPT` is the name of the starting concept.

### Refine Concept Connections
This step utilizes the raw data generated in the previous step. To run this step, 
set ```mode='combine_data_and_refine'``` in ```ConceptGenerator.py ```. 
#### Combine Raw Data

The previously generated dictionaries where located with `data/raw_concept_data_`
identifier in the folder structure and combined. 

We removed multiple entries since the same concept can appear from multiple starting 
concepts. However, we kept track of their appearance in the 'branch' array 
(e.g., `"branch": [["identity", 3], ["justice", 3]]` would mean that this concept
appears from both 'identity' and 'justice' at Level 3)

#### Get Backward Connections
The data so far has a main weakness in that concept connections are unilateral. 
That is, Concept A yields 8 related concepts, but Concept A can also appear as 
a related concept for other input concepts. 
The `iterate_backward_connections` function 
sorts out these connections, resulting in an additional key, 
`backward_concepts`, with an array containing these connections as values.

#### Sort Concepts By Popularity
The refined data so far contains an 8-item array of forward connections 
and a variable-length array of backward connections, the latter depending 
on the popularity of the concept. In most use cases, however, there is 
a desire to provide a fixed-length array of connections, either forward 
or backward, sorted by popularity.

The `compute_concept_popularity` function counts whether or not the 
concept appears as a key and how many times it appears as a related 
concept for other concepts. In the present function, the former has a 
factor of 100, and the latter has a factor of 1, ensuring that 
concepts that are keys always have priority.

The `sort_concept_by_popularity` function, in turn, creates a key, 
`ordered_concepts`, with an array containing the eight most popular 
concepts in descending order, scored in the previous step.

Finally, `concepts` and `backward_concepts` are deleted from this 
dictionary, leaving only `ordered_concepts` as concept data.

This dictionary is stored locally as `combined_refined_concept_data.txt`.

### Evaluate Concepts with ChatGPT

This step involves the evaluation of the concepts created earlier. 
Here we just give instructions for executing the script and understanding
the output data. Refer [ChatGPT for Evaluating Entities] for 
the overall philosophy, experimentation and statistical analyses.

To execute this step, set ```mode='create_evaluation_ratings'``` 
in ```ConceptGenerator.py ```. To define an evaluation dimension,
use the following format (e.g., ```dimension = ['concrete', 'abstract']```). 

The resulted evaluation ratings are appended into `dimension_rating_data.txt`.
This dictionary is organized as follows:
- Previously generated concepts are the main keys
- Upper end of the dimension is the subkey (e.g., `abstract`)
- Numerical array is the value

The required sample (e.g., ```required_sample = 8```) determines how many
evaluation ratings are appended into the array. 

It is important to note that the boolean variable 
`append_existing_rating_data` determines whether the final data 
file is appended or overwritten. For the initial run, this should 
be set to `False`, and then switched to `True`. The value should be `True`
also when another dimension (e.g., simple vs. complex) is being added. In this case,
the script simply adds another subkey to the dictonary and starts appending values to
the correspending array.

### Add Ratings to Interconnectedness Data

This step combines the rating data `dimension_rating_data.txt` 
and the interconnectedness data `combined_refined_concept_data.txt` into a single file.
To run this step, set ```mode='combine_final_file'``` in ```ConceptGenerator.py ```.

Additionally, you can use `ratings_to_be_included` to control which ratings are added 
(e.g.,```ratings_to_be_included=['abstract', 'complex']```). Please ensure that `dimension_rating_data.txt` contains rating data for any 
dimension specified here. The user can also set ratings_to_be_included to ['all'] or [].

The resulting dictionary is stored locally as `final_connection_data.txt`.

### Write to Firestore

The previously generated data is the final data for local inspection, 
but we also store it in Google Firestore for global use. 
To run this step, set ```mode='write_to_firestore'``` in ```ConceptGenerator.py ```.

To make the data Firestore compliant, we first need to flatten the nested 
structure in the 'branch' data (e.g., `[["identity", 3], ["justice", 3]]` 
becomes `["identity", 3 ,"justice", 3]`).

Since Firestore documents have size limitations, we also split the dictionary 
into multiple documents if necessary (i.e., `chunk_size = 200000`).

The data is stored in Firestore as follows:

 - **`conceptBrowser`** (Collection)
    - **`finalConceptData_0`** (Document)
    - **`finalConceptData_1`** (Document)
    - etc
        - **`abstract`** (Number): Rating from 0 (concrete) to 100 (abstract)
        - **`branch`** (Array): The starting concept, its level, ...
        - **`ordered_concepts`** (Array of Strings): An array of the 8 most related concepts to this concept, ordered by relatedness

### Summarize Concepts with ChatGPT

This step involves requesting ChatGPT to generate an 80-word summary for each concept. 
To run this step, set ```mode='define'``` in ```ConceptGenerator.py ```.

The script iterates through all the concepts that serve as keys 
in the interconnectedness data dictionary. For each concept, the script 
first checks Firestore to determine whether a summary already exists. 
If a summary is found, the concept is skipped.

The `generate_concept_definition` function sends a request to 
ChatGPT to create a summary. It returns a dictionary with keys `definition,` `model,`
and `date`. The value of the first key contains the actual summary, 
the second key contains the text "ChatGPT 3.5," and the third key contains 
the retrieval date.

The data is stored in Firestore as follows:

 - **`conceptNames`** (Collection)
    - **`[CONCEPT NAME]`** (Document)
        - **`definition`** (String): A concise summary (about 70 words) about the concept
        - **`date`** (Timestamp): The date and time when ChatGPT generated the definition
        - **`definition_model_version`** (String): The version of ChatGPT used to generate the definition

Where `CONCEPT NAME` is the name of each concept.

### Data Collection Management

A few words about overall data management are worth noting. First, 
it is important to realize that ChatGPT requests are quite time-consuming, 
error-prone, and they cost real money. Therefore, the focus here is on 
saving data frequently and ensuring that scripts can resume their actions 
wherever ChatGPT encounters an issue, for example.

Here's how we accomplish this in different scripts:

- For initial data collection, the iterator returns the data after 
`run_for_sec_before_save = 10` and then resumes the action
- In the evaluation script, 110 ratings are requested at a time and appended to the data file before requesting new ratings.
- The summary generation script interacts with Firestore directly and checks which summaries have already been written.

## ChatGPT for Evaluating Entities

One special aspect of this project is to utilize ChatGPT for evaluating
entities. ChatGPT can be used for evaluating nearly anything, 
from concepts to products, services, content, and more.

To evaluate entities meaningfully, two things have to be true. First, 
the entities have to form a group so that their comparison 
makes sense (e.g., concepts in this project). Second, there has to 
be a continuous dimension along which the entities can be rated. This dimension 
must have distinct lower and upper ends (e.g., concrete and abstract).

### Evolution of Approach

In this project, we experimented with various ways to obtain such evaluations.
One approach was simply to request ChatGPT to return a 
score ranging from 0 (concrete) to 1 (abstract). However, this approach 
yielded unreliable and counter-intuitive results.

The final approach is to request ChatGPT to sort the input entities (e.g., 
sort these concepts ['stone', 'sky', 'mind'] from concrete to abstract). The 
request returns a sorted array, and the location in this sorted array is one 
data point from which the final rating is derived.

The exact reason why this approach is better is somewhat unclear, 
but it probably has to do with the fact 
that Large Language Models (LLMs), unlike general-purpose computing, 
excel in processing verbal rather than numerical information. Additionally, 
sorting might outperform one-entity-at-a-time evaluations because more 
entities create more content for the evaluation.

This approach is also more efficient than the one-entity-at-a-time approach, 
as per ChatGPT's request. Indeed, since each request yields ratings for all 
the input concepts, we can run more ratings, reducing the impact of random 
erroneous results, which ChatGPT sometimes produces.

 
### Step by Step

Here, we apply the above principle for evaluating concepts along the concrete vs. 
abstract dimension. Other dimensions can be evaluated simply by changing 
the dimension variable (e.g., ```dimension = ['concrete', 'abstract']```).

The method begins by initializing a dictionary where all concepts 
serve as keys, with empty arrays as their corresponding values.

The repeated steps are as follows:

- Measure the length of the value array for each concept (0 for the first round)
- Select 110 keys with the shortest value arrays (randomize for equal values)
- In chunks of 11, request ChatGPT to sort the concepts
- Based on the location in the sorted array, assign a value between 0 and 1 to each concept
- Return all 110 values and append them to the original dictionary
- Save the value array in case one ChatGPT request crashes at some point
- Repeat the above steps until the defined minimum length of the value array has been reached

#### Function to Generate Actual Data

The `generate_concept_rating` function takes a concept array as an argument and 
divides it into batches that are 11 concepts long (handy for obtaining 
ratings from 0 to 1 with a 0.1 increment). The function returns a value 
dictionary, which is, in turn, appended to the final data stored in 
`dimension_rating_data.txt`.

#### Function to Generate Mock Data

The `generate_alphabetical_rating` function returns data in the same format as 
the actual `generate_concept_rating` function, but the data itself is nothing
but an alphabetical sorting of concepts (instead of their evaluative sorting). 
Since alphabetical sorting is flawless, this emulates perfect measurements and 
thereby serves as a figure of merit for the approach itself.

This special mock data can be generated by setting 
`dimension = ['', 'alphabetical']`. The outcome of this run is manually 
saved in `dimension_rating_data_alphabetical.txt`.

### Quality of Evaluations
 
Since there is no way to objectively determine the abstractness of a concept, 
we begin by simply showing some results. The second and the fourth columns in Table 1 
display the 10 most concrete and the 10 most abstract concepts in the data, respectively.


| Position | Most Abstract Concepts | Rating | Most Concrete Concepts | Rating |
|----------|-------------------|--------|-------------------|--------|
|    1     | feminism          | 1.0    | resistor          | 0.0    |
|    2     | sacred            | 1.0    | comets            | 0.0    |
|    3     | consciousness     | 0.96   | kite              | 0.0    |
|    4     | sacrosanct        | 0.96   | drilling          | 0.0    |
|    5     | spiritual          | 0.94   | submarine         | 0.0    |
|    6     | supreme being     | 0.93   | boy               | 0.0    |
|    7     | peace             | 0.93   | animals           | 0.0    |
|    8     | optimistic        | 0.93   | microorganisms    | 0.0    |
|    9     | revulsion         | 0.92   | burglary          | 0.0    |
|   10     | revolution         | 0.91   | kiteboarding      | 0.01   |

 It is intuitively clear that the items in the second column are more 
 abstract than the items in the fourth column. The extent to which 
 these ratings would agree with human evaluations is subject to further investigation.

#### Computation of Intraclass Correlation Coefficient

To evaluate the performance of ChatGPT, we compute the Intraclass 
Correlation Coefficient (ICC). This is a measure of test-retest 
reliability for multiple measurements.

We once again use ```ConceptGenerator.py ``` and 
set ```mode='intraclass_CC_for_evaluation_ratings'``` to run this analysis.

First, we use the `dict_to_numpy` function to arrange the rating 
data into a 2D numpy array (2171 by 8), where the former represents 
the between-concept and the latter represents the within-concept dimension.

Second, the array is passed into the `compute_icc` function, which returns 
ICC value. Finally, we repeated the above steps for the mock data that 
emulates perfect measurements.

These analyses yielded:

**ICC(ChatGPT) = 0.47** 

**ICC(theoretical) = 0.85** 

The results indicate a moderate level of agreement between measurements 
(ICC = 0.47), suggesting that ChatGPT can rate concepts somewhat reliably. 
However, the value also falls short of the theoretical ideal (ICC = 0.85). 
That said, given the subjective nature of the ratings, even moderate 
agreement is quite a remarkable outcome achieved by a computer.

## API Keys
### ChatGPT

Access to the ChatGPT API requires an OpenAI account. Here, the API key 
is saved as an environmental variable `OPENAI_API_KEY` and retrieved 
by the `my_openai()` function located in `utils/my_openai_creds.py`.

### Firestore

We use Firestore to store the final data. However, all intermediate results 
are saved locally, so the use of Firestore is optional.

To use Firestore, you need a Google account and initialization 
in the Google Cloud Platform. Here, the `init_firebase()` function 
reads a locally stored credentials certificate.

## Roadmap

### ChatGPT for Evaluating Entities

We aim to investigate the following ways to make ChatGPT even better for 
evaluating entities:

- There are computationally more accurate ways to convert the sorting 
results into values, factoring in the other concepts that appear in 
the sorting (increasing the theoretical ICC will also improve the practical ICC).
- Find prompting techniques that yield more robust results, including
the verification of ChatGPT's own outcome (e.g., 'Is this the order you really think is the most accurate?').
- Experiment with anchoring techniques, i.e., using well-tested ratings 
as anchors to provide context for new ratings.

### Robust Python Environment for Running ChatGPT
We aim to build an environment where complex prompting requests can be 
fully automated. To utilize the full potential of ChatGPT, experimentation 
is necessary, which in turn requires a robust, one-click environment even 
for the most complex and interactive requests.
## Contact Information

For inquiries or collaboration opportunities, please feel free to contact me via email. 
My name is listed on [the Profile page](https://github.com/JoelHKV), and I am using Gmail.
