# %%
import json

# %%
file_path = f"../data/processed/labels.json"
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

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


result_with_score = {i: {j:0 for j in ethics_concepts.keys()} for i in privacy_concepts.keys()}
result_without_score = {i: {j:0 for j in ethics_concepts.keys()} for i in privacy_concepts.keys()}

# %%

for post in data:
    for p in privacy_concepts.keys():
        for e in ethics_concepts.keys():
            if p in post['labels-p'] and e in post['labels-e']:
                result_with_score[p][e] += post['score']
                result_without_score[p][e] += 1
    
    for comment in post['comments']:
        for p in privacy_concepts.keys():
            for e in ethics_concepts.keys():
                if (p in post['labels-p'] and e in comment['labels-e']) or (e in post['labels-e'] and p in comment['labels-p']) or (e in comment['labels-e'] and p in comment['labels-p']):
                    result_with_score[p][e] += comment['score']
                    result_without_score[p][e] += 1

# %%

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Convert the result dictionary into a DataFrame for easier plotting
df = pd.DataFrame(result_with_score)

# Plot the heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(df, annot=True, cmap="Blues", fmt="d", cbar_kws={'label': 'Count'})
plt.title("Relationship between Privacy and Ethics Concepts")
plt.xlabel("Privacy Concepts")
plt.ylabel("Ethics Concepts")
plt.show()

# %%

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Convert the result dictionary into a DataFrame for easier plotting
df = pd.DataFrame(result_with_score)

# Plot the heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(df, annot=True, cmap="Blues", fmt="d", cbar_kws={'label': 'Count'})
plt.title("Relationship between Privacy and Ethics Concepts considering score")
plt.xlabel("Privacy Concepts")
plt.ylabel("Ethics Concepts")
plt.show()


# %%

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Convert the result dictionary into a DataFrame for easier plotting
df = pd.DataFrame(result_without_score)

# Plot the heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(df, annot=True, cmap="Blues", fmt="d", cbar_kws={'label': 'Count'})
plt.title("Relationship between Privacy and Ethics Concepts without considering score")
plt.xlabel("Privacy Concepts")
plt.ylabel("Ethics Concepts")
plt.show()

# %%