# %%
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from bs4 import BeautifulSoup
import requests
import os

# %%

ethics_concepts = {
    "Respect for human rights": "Concerns for human rights are discussed",
    "Data protection and right to privacy": "Data protection and privacy concerns in AI development are referenced",
    "Harm prevention and beneficence": "Harm prevention and safety when using AI is mentioned",
    "Non discrimination and freedom of privileges": "Discrimination and bias concerns are discussed",
    "Fairness and justice": "Fairness and justice of AI is discussed",
    "Transparency and explainability of AI systems": "Transparency and explainability of the AI system is referenced",
    "Accountability and responsibility": "The accountability and responsibility of the AI system is discussed",
    "Democracy and the rules of law": "Democratic oversight and legal frameworks for AI is discussed",
    "Environmental and social sustainability": "The environmental and social impacts from AI and how systems can be more sustainable is discussed"
}

privacy_concepts = {
    # Concepts from Solove’s Taxonomy
    "Surveillance": "The user is facing a data surveillance issue.",
    "Aggregation": "Personal user information is collected from other sources.",
    "Identification": "A data anonymity topic is discussed.",
    "Secondary Use": "The user is concerned about the purposes of personal data access.",
    "Exclusion": "The user wants to correct their personal information.",
    "Breach of Confidentiality": "A breach of data confidentiality is discussed.",
    "Disclosure": "Personal data disclosure is discussed.",

    # Concepts from Wang and Kobsa’s Taxonomy
    "Notice/Awareness": "Opting out from personal data collection is discussed.",
    "Data Minimization": "More access than needed is required.",
    "Purpose Specification": "The reason for data access is not provided.",
    "Collection Limitation": "Too much personal data is collected.",
    "Use Limitation": "The data is being used for unexpected purposes.",
    "Onward Transfer": "Data sharing with third parties is discussed.",
    "Choice/Consent": "User choice for personal data collection is discussed. User did not allow access to their personal data."
}

with open('../data/raw/reddit_posts_Ethics_AI.json') as file:
    ethics_data = json.load(file)
with open('../data/raw/reddit_posts_privacy_AI.json') as file:
    privacy_data = json.load(file)    

data = ethics_data + privacy_data


# %%
model_name = "facebook/bart-large-mnli"  # microsoft/deberta-large-mnli or roberta-large-mnli or facebook/bart-large-mnli
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def is_entailment(premise, hypothesis):
    # Encode the inputs
    inputs = tokenizer(premise, hypothesis, return_tensors="pt", truncation=True)
    
    # Get model outputs
    outputs = model(**inputs)
    logits = outputs.logits
    
    # Apply softmax to get probabilities
    probs = F.softmax(logits, dim=-1)
    
    # Map class labels to human-readable format
    label_map = ["Entailment", "Neutral", "Contradiction"]
    pred_label = label_map[torch.argmax(probs).item()]
    pred_probs = probs.detach().numpy()[0]
    return pred_label == "Entailment"

# %%
def find_labels(premise):
    privacy_lables = []
    ethics_lables = []
    for privacy_lable, privacy_hypothesis in privacy_concepts.items():
        if is_entailment(premise, privacy_hypothesis):
            privacy_lables.append(privacy_lable)

    for ethics_lable, ethics_hypothesis in ethics_concepts.items():
        if is_entailment(premise, ethics_hypothesis):
            ethics_lables.append(ethics_lable)
    return privacy_lables, ethics_lables

# %%
def get_url_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',]
    main_text = ' '.join([element.get_text() for tag in tags for element in soup.find_all(tag)])
    return main_text

# %%
#data = ethics_data[0:1] + privacy_data[1:2]
#privacy_data[1]

# %
os.makedirs("../data/processed", exist_ok=True)
file_path = f"../data/processed/labels.json"
processed_data = []
try:
    with open(file_path, "r", encoding="utf-8") as f:
        processed_data = json.load(f)
except:
    pass

i = len(processed_data)
for i in range(i, len(data)):
    post = data[i]
    res = {'title':post['title'], 'score': post['score'], 'labels-p': [], 'labels-e': [], 'comments':[]}
    text = post['title'] + '\n' + post['selftext']
    if post['selftext'] == '':
        text =  text + get_url_text(post['url'])
    labels_post = find_labels(text)
    res['labels-p'] = labels_post[0]
    res['labels-e'] = labels_post[1]
    print(i, res['labels-p'], res['labels-e'])
    post_score = post['score']
    for comment in post['comments'][:5]:
        comment_label = find_labels(comment["body"])
        res_comment = {
            "labels-p": comment_label[0],
            "labels-e": comment_label[1],
            "score": comment["score"],
        }
        res["comments"].append(res_comment)
    processed_data.append(res)        
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)
        print(i, res['labels-p'], res['labels-e'])

# %%

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(processed_data, f, ensure_ascii=False, indent=4)

print(f"Data saved to {file_path}")

# %%


