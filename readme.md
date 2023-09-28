# Concept Generator

## General Information
Concept Generator harnesses the power of ChatGPT 3.5 to generate data about concepts, which are fundamental building blocks in thinking. In this project, we utilize Python scripts to interact with ChatGPT in a recursive and unconventional manner. This project consists of four major steps:

- We begin with user-defined initial concepts and instruct ChatGPT to generate related concepts to a certain depth, creating a complex mesh of interconnected ideas.
- We identify the eight most closely related concepts for each original and created concept.
- We assess the degree of concreteness versus abstractness associated with each concept, utilizing a specialized comparison algorithm tailored for ChatGPT.
- We request ChatGPT to craft concise approximately 70-word summaries for each concept.

This approach enables us to create a rich web of interconnected conceptual data, offering insights into the relationships between various ideas and their abstractness levels. This data is futhermore utilized in [Concept Explorer.](https://github.com/JoelHKV/ConceptExplorer)

## Getting Started
To run this project locally, follow these five steps:

1. **Installation:**
Ensure you have Python 3.9.5 or newer installed on your system.

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
Set up API keys. Refer Section 'API Keys' for details.

5. **Run the Project:**
Execute the main script ```ConceptGenerator.py ``` one step at the time. First set ```mode='generate'``` and run the script, then ```mode='refine'``` and so on.

6. **Explore the Output:**
Check the project's output at Google Firestore or local files saved in the data-folder.



## Data Generation and Post-Processing
### Generate Interconnected Concepts with ChatGPT 
To run this step, set ```mode='generate'``` in ```ConceptGenerator.py ```. In addition, set a starting concept (e.g., ```concept_end_point='mind'```) and the level of depth in recursion (e.g., ```depth = 2```).

The iteration starts with the starting concept. 

At first at level 1, the script requests ChatGPT to generate eight concepts related to the starting concept. 
Then, at level 2, the script iterates through these eight newly created concepts and requests 
ChatGPT to generate eight concepts related to each. In theory, this would yield 64 concepts in total (8*8) 
but since there is some overlap, the actual number is smaller. Then at level 3, the script iterates through these new concepts (<=64) to create even more concepts and so on.

The script outputs a dictionary where each iterated concept is a key. One line looks like follows:

```judgment: {'branch': 'mind', 'concepts': ['decision', 'evaluation', 'assessment', 'discernment', 'verdict', 'opinion', 'critique', 'analysis']} ```

Within each key there is a key 'branch' with the user-defined starting concept (e.g., 'mind') as a value. The second key 'concepts' has an eight-long array as a value, each item representing one related concept created by ChatGPT.

The dictionary is stored in Firestore as   

- **`conceptBrowser`** (Collection)
  - **`concepts_raw`** (Collection)

It is also saved locally as data/raw_data.txt.

### Refine Concept Connections
This step uses the raw data created in the previous step. To run this step, set ```mode='refine'``` in ```ConceptGenerator.py ```. 
#### Get Backward Connections
The raw data generated in the previous step has the main weakness that concept connections are unilateral. 
That is, the inputed Concept A yielded eight related concepts, but Concept A can also appear as a related concept for other inputted concepts. 
The iterate_backward_connections -function sorts these connections out, yielding an additional key 'backward_concepts' with an array containing these connections as value. 

#### Sort By Popularity
The data so far contains an eight long array of forward connections and an x long array of backward connections, 
latter depending on the popularity of the concept. 
In most use cases however, we want to provide a fixed length array of connections, forward or backward, sorted by popularity.

The compute_concept_popularity -function counts whether or not the concept appears as a key and then how many times in total it appears as a related concept for other concepts. In the present function the former has a factor of 100 and the latter has a factor of 1, assuring that concepts that are keys always have priority. 

The sort_concept_by_popularity -function in turn creates a key 'ordered_concepts' with an array containing eight most popular concepts, in descending order, scored in the previous step, as value. 

Finally, 'concepts' and 'backward_concepts' are deleted from this dictonary, leaving only 'ordered_concepts' left as concept data.

This performant dictionary is the final interconnectedness data stored in Firestore as   

- **`conceptBrowser`** (Collection)
  - **`concepts_refined`** (Collection)

It is also saved locally as data/raw_refined.txt.

### Compute Concreteness vs. Abstractness of Each Concept


 







the first ste



Concepts 1-8 related to , but Concept A in turn 


that are related to the previos concept.   
The goal is to 


In addition the user has to enter the starting concept to be explored by setting for example ```concept_end_point='mind'```
Finally, the user has to set the level of recursion for example ```depth = 2```. 

The algorithm always returns eight concepts related to the inputted concept. If level is set to 


The first iteration round (depth = 1) returns 8 concepts related to the starting co



## Refining Process


## API Keys
### ChatGPT
Access to ChatGPT API requires an OpenAI account. Here, API key is saved as an environmental variable OPENAI_API_KEY and used by my_openai() function located in utils/my_openai_creds.py

### Google Cloud Platform & Firestore





We use Firestore, which is a cloud-based NoSQL database service, in every step of the way. Thus, from raw ChatGPT data to refined final data  

 

## Technologies Used
Concept Generator is written in Python and it uses Firestore (=cloud-based NoSQL database service) for data management.


## Folder Structure
The project directory is organized as follows:

* ConceptGenerator.py: The entry point for all steps in the way.
* src/: Contains functions for data processing.
* utils/: Holds utility functions for credentials etc.
* data/: Stores example data (not a functional part as actual data is handled by Firestore in every step of the way.).



## Database Schema
### All Interconnections
Data related to interconnections between concepts is stored in Firestore under the following structure:

- **`conceptBrowser`** (Collection)
  - **`concepts_refined`** (Collection)
    - **`[Concept Name]`** (Document)
      - **`abstract`** (Number): Abstractness rating from 0 (concrete) to 100 (abstract).
      - **`branch`** (String): The starting concept that led to this concept.
      - **`ordered_concepts`** (Array of Strings): An array of the 8 most related concepts to this concept, ordered by relatedness.

### Concept Details
Details about individual concepts are stored in Firestore using the following structure:

- **`conceptNames`** (Collection)
  - **`[Concept Name]`** (Document)
    - **`definition`** (String): A concise summary (about 70 words) about the concept.
    - **`date`** (Timestamp): The date and time when ChatGPT generated the definition.
    - **`definition_model_version`** (String): The version of ChatGPT used to generate the definition.

This structure helps organize and retrieve data efficiently, allowing for easy access to interconnections between concepts and detailed information about each concept.


## Testing
Since Concept Explorer uses Google Map Markers as buttons, and Selenium does not easily recognize them as such, conventional functional testing is difficult. Thus, we use Autohotkey to randomly click the screen area. We run this test with Chrome, Firefox, and Edge (but not Safari). The testing script is located in the 'testing_script' subfolder alongside the captured video with Chrome. The link to the video is also provided here.
    
## Licence
## Known Issues
- Google Map animations are not always smooth, particularly with some smartphones
## Roadmap
- Add Settings Menu where the user can turn animations on or off, change marker sizes etc.
- 
## Contact Information
