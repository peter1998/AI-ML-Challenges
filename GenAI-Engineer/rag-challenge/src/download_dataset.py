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
    
    print("Downloading a subset of OpenThoughts2-1M dataset...")
    # Load only a small subset of the dataset (1000 samples to keep it manageable)
    dataset = load_dataset("open-thoughts/OpenThoughts2-1M", split="train[:1000]")
    
    print("Dataset info:")
    print(dataset)
    
    # Process the dataset to simulate company documentation
    print("Processing dataset to simulate company documents...")
    
    # Create document types that would appear in a company
    doc_types = ["technical_specification", "product_manual", 
                 "meeting_notes", "support_ticket", "internal_memo"]
    
    # Create departments
    departments = ["engineering", "product", "support", "marketing", "operations"]
    
    # Process samples into simulated documents
    document_metadata = []
    questions = []
    expected_answers = []
    
    # Group by mathematical topics to create related documents
    topics = {}
    
    for i, item in enumerate(tqdm(dataset)):
        # Create a simplified topic based on the content
        question = item["question"]
        if "function" in question.lower():
            topic = "functions"
        elif "circle" in question.lower():
            topic = "geometry"
        elif "prime" in question.lower():
            topic = "number_theory"
        elif "diagonal" in question.lower():
            topic = "linear_algebra"
        elif "maximum" in question.lower() or "minimum" in question.lower():
            topic = "optimization"
        else:
            topic = "general_mathematics"
        
        if topic not in topics:
            topics[topic] = []
        
        # Store the item with its index
        topics[topic].append((i, item))
    
    # Create documents from grouped topics
    doc_id = 1
    for topic, items in topics.items():
        # Determine how many documents to create for this topic
        num_docs = max(1, min(2, len(items) // 10))  # Create at most 2 docs per topic
        
        for doc_num in range(num_docs):
            # Select items for this document
            start_idx = doc_num * (len(items) // num_docs)
            end_idx = (doc_num + 1) * (len(items) // num_docs) if doc_num < num_docs - 1 else len(items)
            doc_items = items[start_idx:end_idx]
            
            if not doc_items:
                continue
                
            # Determine document type and department
            doc_type = random.choice(doc_types)
            department = random.choice(departments)
            
            # Create document content
            content = f"# {topic.replace('_', ' ').title()} Document {doc_num + 1}\n\n"
            content += f"Department: {department}\n"
            content += f"Document Type: {doc_type}\n\n"
            content += "## Content\n\n"
            
            # Add items to the document
            for idx, (item_idx, item) in enumerate(doc_items[:15]):  # Limit to 15 items per document
                content += f"### Question {idx + 1}\n"
                content += f"{item['question']}\n\n"
                
                # Extract answer from conversation if available
                answer = ""
                if "conversations" in item and item["conversations"] and len(item["conversations"]) > 1:
                    for conv in item["conversations"]:
                        if conv.get("from") != "user":
                            answer = conv.get("value", "")
                            break
                
                content += f"**Answer:**\n{answer}\n\n"
                
                # Create a question-answer pair for evaluation
                if idx % 5 == 0:  # Select every fifth item for QA evaluation
                    questions.append({
                        "id": len(questions) + 1,
                        "question": f"What is the answer to: {item['question']}",
                        "document_id": doc_id
                    })
                    expected_answers.append({
                        "id": len(expected_answers) + 1,
                        "question_id": len(questions),
                        "answer": answer
                    })
            
            # Save the document
            file_extension = "md"  # We'll use markdown for all
            filename = f"doc_{doc_id:03d}_{topic}_{doc_type}.{file_extension}"
            
            with open(f"../data/processed/documents/{filename}", "w") as f:
                f.write(content)
            
            # Create metadata
            document_metadata.append({
                "id": doc_id,
                "filename": filename,
                "topic": topic,
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
