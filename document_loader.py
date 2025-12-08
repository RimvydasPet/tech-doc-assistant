"""Technical documentation loader."""
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from logger import logger
from config import CHUNK_SIZE, CHUNK_OVERLAP


class TechnicalDocumentLoader:
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_documents(self) -> List[Document]:
        logger.info("Loading technical documentation")
        
        # Sample technical documentation content
        # In production, this would load from files, APIs, or web scraping
        documents_content = [
            {
                "content": """
# Pandas DataFrame Basics

Pandas is a powerful data manipulation library in Python. The DataFrame is the primary data structure.

## Creating DataFrames

You can create a DataFrame from various sources:

```python
import pandas as pd

# From dictionary
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

# From CSV
df = pd.read_csv('file.csv')

# From list of dictionaries
data = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
df = pd.DataFrame(data)
```

## Basic Operations

- `df.head()` - View first 5 rows
- `df.info()` - Get DataFrame information
- `df.describe()` - Statistical summary
- `df.shape` - Get dimensions (rows, columns)
- `df.columns` - Get column names

## Selecting Data

- `df['column']` - Select single column
- `df[['col1', 'col2']]` - Select multiple columns
- `df.loc[row_label]` - Select by label
- `df.iloc[row_index]` - Select by position
- `df[df['column'] > value]` - Conditional selection

## Data Cleaning

- `df.dropna()` - Remove missing values
- `df.fillna(value)` - Fill missing values
- `df.drop_duplicates()` - Remove duplicates
- `df.rename(columns={'old': 'new'})` - Rename columns
""",
                "metadata": {"source": "pandas_basics", "category": "pandas", "topic": "dataframe"}
            },
            {
                "content": """
# NumPy Array Operations

NumPy is the fundamental package for scientific computing in Python.

## Creating Arrays

```python
import numpy as np

# From list
arr = np.array([1, 2, 3, 4, 5])

# Zeros and ones
zeros = np.zeros((3, 4))
ones = np.ones((2, 3))

# Range
arr = np.arange(0, 10, 2)  # [0, 2, 4, 6, 8]

# Linspace
arr = np.linspace(0, 1, 5)  # 5 evenly spaced values

# Random
random_arr = np.random.rand(3, 3)
```

## Array Properties

- `arr.shape` - Dimensions
- `arr.dtype` - Data type
- `arr.size` - Total elements
- `arr.ndim` - Number of dimensions

## Array Operations

- `arr + 5` - Add scalar
- `arr * 2` - Multiply by scalar
- `arr1 + arr2` - Element-wise addition
- `arr.sum()` - Sum all elements
- `arr.mean()` - Mean value
- `arr.std()` - Standard deviation
- `arr.max()` - Maximum value
- `arr.min()` - Minimum value

## Reshaping

- `arr.reshape(rows, cols)` - Change shape
- `arr.flatten()` - Convert to 1D
- `arr.transpose()` - Transpose array

## Indexing and Slicing

- `arr[0]` - First element
- `arr[-1]` - Last element
- `arr[1:4]` - Slice
- `arr[arr > 5]` - Boolean indexing
""",
                "metadata": {"source": "numpy_basics", "category": "numpy", "topic": "arrays"}
            },
            {
                "content": """
# Scikit-learn Machine Learning Basics

Scikit-learn is a machine learning library for Python.

## Data Preprocessing

```python
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)

# Encode labels
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)
```

## Classification

```python
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# Logistic Regression
model = LogisticRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)

# Random Forest
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train, y_train)
```

## Regression

```python
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor

# Linear Regression
model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)

# Gradient Boosting
gb = GradientBoostingRegressor()
gb.fit(X_train, y_train)
```

## Model Evaluation

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.metrics import mean_squared_error, r2_score

# Classification metrics
accuracy = accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions)
recall = recall_score(y_test, predictions)

# Regression metrics
mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)
```

## Cross-Validation

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(model, X, y, cv=5)
print(f"Average score: {scores.mean()}")
```
""",
                "metadata": {"source": "sklearn_basics", "category": "scikit-learn", "topic": "machine_learning"}
            },
            {
                "content": """
# Matplotlib Visualization Guide

Matplotlib is a comprehensive library for creating visualizations in Python.

## Basic Plotting

```python
import matplotlib.pyplot as plt

# Line plot
plt.plot(x, y)
plt.xlabel('X Label')
plt.ylabel('Y Label')
plt.title('Title')
plt.show()

# Scatter plot
plt.scatter(x, y)
plt.show()

# Bar plot
plt.bar(categories, values)
plt.show()

# Histogram
plt.hist(data, bins=20)
plt.show()
```

## Subplots

```python
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

axes[0, 0].plot(x, y1)
axes[0, 1].scatter(x, y2)
axes[1, 0].bar(categories, values)
axes[1, 1].hist(data)

plt.tight_layout()
plt.show()
```

## Customization

```python
plt.plot(x, y, color='red', linestyle='--', linewidth=2, marker='o')
plt.grid(True)
plt.legend(['Series 1'])
plt.xlim(0, 10)
plt.ylim(0, 100)
```

## Saving Figures

```python
plt.savefig('plot.png', dpi=300, bbox_inches='tight')
```
""",
                "metadata": {"source": "matplotlib_basics", "category": "matplotlib", "topic": "visualization"}
            },
            {
                "content": """
# Python Requests Library Guide

The requests library is used for making HTTP requests in Python.

## Basic Requests

```python
import requests

# GET request
response = requests.get('https://api.example.com/data')
print(response.status_code)
print(response.json())

# POST request
data = {'key': 'value'}
response = requests.post('https://api.example.com/submit', json=data)

# PUT request
response = requests.put('https://api.example.com/update/1', json=data)

# DELETE request
response = requests.delete('https://api.example.com/delete/1')
```

## Headers and Authentication

```python
# Custom headers
headers = {'Authorization': 'Bearer token123'}
response = requests.get(url, headers=headers)

# Basic authentication
response = requests.get(url, auth=('username', 'password'))
```

## Query Parameters

```python
params = {'search': 'python', 'limit': 10}
response = requests.get(url, params=params)
```

## Error Handling

```python
try:
    response = requests.get(url, timeout=5)
    response.raise_for_status()  # Raise exception for bad status
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
```

## Session Objects

```python
session = requests.Session()
session.headers.update({'Authorization': 'Bearer token'})
response = session.get(url)
```
""",
                "metadata": {"source": "requests_basics", "category": "requests", "topic": "http"}
            },
            {
                "content": """
# Flask Web Framework Basics

Flask is a lightweight web framework for Python.

## Basic Application

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({'message': 'Success', 'data': [1, 2, 3]})

@app.route('/api/submit', methods=['POST'])
def submit_data():
    data = request.get_json()
    return jsonify({'received': data}), 201

if __name__ == '__main__':
    app.run(debug=True)
```

## URL Parameters

```python
@app.route('/user/<username>')
def show_user(username):
    return f'User: {username}'

@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f'Post ID: {post_id}'
```

## Request Data

```python
# Query parameters
search = request.args.get('search', '')

# Form data
username = request.form.get('username')

# JSON data
data = request.get_json()
```

## Templates

```python
from flask import render_template

@app.route('/page')
def page():
    return render_template('template.html', title='Page Title')
```

## Error Handling

```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404
```
""",
                "metadata": {"source": "flask_basics", "category": "flask", "topic": "web_framework"}
            }
        ]
        
        # Create Document objects
        documents = []
        for doc_data in documents_content:
            doc = Document(
                page_content=doc_data["content"],
                metadata=doc_data["metadata"]
            )
            documents.append(doc)
        
        logger.info(f"Loaded {len(documents)} documents")
        
        # Split documents into chunks
        split_docs = self.text_splitter.split_documents(documents)
        logger.info(f"Split into {len(split_docs)} chunks")
        
        return split_docs
