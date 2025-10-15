# Self-Correction-Parsing

Code for EMNLP-2025's paper Self-Correction Makes LLMs Better Parsers.

## Requirements:

- nltk: >= 3.4.5

## Preparation

- In-domain dataset, e.g., PTB
- Cross-domain dataset, e.g., MCTB


## Usage

### LLM Parsing

Try the following commands.

```
python self-correction-parsing/LLM/prompt.py
```
   

### Self-Correction Method

1. Constructing Treebank from Dadaset, e.g., PTB.

   
   - [[Prepocessing steps.](https://github.com/zzy0509/Self-Correction-Parsing/tree/main/self-correction-parsing/preprocess)]
   

   

2. Prompting LLMs to Make Corrections.

   - [[Generating steps.](https://github.com/zzy0509/Self-Correction-Parsing/tree/main/self-correction-parsing/LLM)]

