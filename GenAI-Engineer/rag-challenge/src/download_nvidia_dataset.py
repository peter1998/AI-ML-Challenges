import os
import json
import random
from tqdm import tqdm
from datasets import load_dataset

def main():
    # Create directories if they don't exist
    os.makedirs("../data/raw", exist_ok=True)
    os.makedirs("../data/processed", exist_ok=True)
    os.makedirs("../data/processed/documents", exist_ok=True)
    
    print("Downloading a subset of NVIDIA OpenCodeReasoning dataset...")
    # Load a small subset of the dataset
    dataset_dict = load_dataset("nvidia/OpenCodeReasoning", "split_0")
    dataset = dataset_dict["split_0"].select(range(100))  # Fixed: Access the split first
    
    print("Dataset info:")
    print(dataset)
    
    # Process the dataset to simulate company documentation
    print("Processing dataset to simulate company documents...")
    
    # Create document types that would appear in a company
    doc_types = ["technical_specification", "product_manual", 
                 "meeting_notes", "support_ticket", "internal_memo"]
    
    # Create departments
    departments = ["engineering", "product", "support", "marketing", "operations"]
    
    # Process samples into documents
    document_metadata = []
    questions = []
    expected_answers = []
    
    # Create documents from programming problems
    doc_id = 1
    samples = dataset
    
    # Group by source
    grouped_samples = {}
    for item in samples:
        source = item["source"]
        if source not in grouped_samples:
            grouped_samples[source] = []
        grouped_samples[source].append(item)
    
    for source, items in grouped_samples.items():
        # Create 1-2 documents per source
        num_docs = min(2, max(1, len(items) // 5))
        
        for doc_num in range(num_docs):
            # Select items for this document
            start_idx = doc_num * (len(items) // num_docs)
            end_idx = min(len(items), start_idx + 5)  # Limit to 5 items per document
            doc_items = items[start_idx:end_idx]
            
            # Determine document type and department
            doc_type = random.choice(doc_types)
            department = random.choice(departments)
            
            # Create document content
            content = f"# {source.title()} Programming Documentation {doc_num + 1}\n\n"
            content += f"Department: {department}\n"
            content += f"Document Type: {doc_type}\n\n"
            content += "## Content\n\n"
            
            # Add items to the document
            for idx, item in enumerate(doc_items):
                content += f"### Problem {idx + 1}\n"
                content += f"{item['input'][:1000]}...\n\n"  # Truncate long problems
                
                # Use solution as the answer
                solution = item['solution']
                content += f"**Solution:**\n```python\n{solution}\n```\n\n"
                
                # Create a question-answer pair for evaluation
                if idx % 2 == 0:  # Select every other item
                    questions.append({
                        "id": len(questions) + 1,
                        "question": f"How do I solve this programming problem: {item['input'][:100]}...",
                        "document_id": doc_id
                    })
                    expected_answers.append({
                        "id": len(expected_answers) + 1,
                        "question_id": len(questions),
                        "answer": solution
                    })
            
            # Save the document
            filename = f"doc_{doc_id:03d}_{source}_{doc_type}.md"
            
            with open(f"../data/processed/documents/{filename}", "w") as f:
                f.write(content)
            
            # Create metadata
            document_metadata.append({
                "id": doc_id,
                "filename": filename,
                "topic": source,
                "type": doc_type,
                "department": department,
                "creation_date": f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            })
            
            doc_id += 1
    
    # Save metadata, questions, and expected answers as JSON
    with open("../data/processed/document_metadata.json", "w") as f:
        json.dump(document_metadata, f, indent=2)
    
    with open("../data/processed/sample_questions.json", "w") as f:
        json.dump(questions, f, indent=2)
        
    with open("../data/processed/expected_answers.json", "w") as f:
        json.dump(expected_answers, f, indent=2)
    
    print(f"Created {doc_id - 1} documents")
    print(f"Created {len(questions)} sample questions with expected answers")
    print("Processing complete!")

if __name__ == "__main__":
    main()
