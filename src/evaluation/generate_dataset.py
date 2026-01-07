import os
import json
import random
from pathlib import Path
from typing import List, Dict
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

# Mock LLM generation function (In production, replace with actual LLM call)
def generate_qa_from_text(text: str) -> Dict[str, str]:
    """
    Simulates generating a Question-Answer pair from a text chunk.
    """
    # Simple heuristic for demo purposes
    words = text.split()
    if len(words) < 10:
        return None
        
    topic = " ".join(words[:5])
    return {
        "question": f"What does the text say about '{topic}'?",
        "ground_truth": text[:200] + "..."  # In reality, this should be a summarized answer
    }

class GoldenSetGenerator:
    def __init__(self, source_dir: str, output_file: str):
        self.source_dir = Path(source_dir)
        self.output_file = Path(output_file)
        
    def generate(self, num_samples: int = 10):
        print(f"Loading documents from {self.source_dir}...")
        if not self.source_dir.exists():
            print(f"Directory {self.source_dir} not found. Creating dummy data.")
            dataset = self._create_dummy_data()
        else:
            reader = SimpleDirectoryReader(input_dir=str(self.source_dir), recursive=True)
            documents = reader.load_data()
            
            parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
            nodes = parser.get_nodes_from_documents(documents)
            
            print(f"Generated {len(nodes)} chunks. Sampling {num_samples}...")
            selected_nodes = random.sample(nodes, min(num_samples, len(nodes)))
            
            dataset = []
            for node in selected_nodes:
                qa = generate_qa_from_text(node.text)
                if qa:
                    dataset.append({
                        "id": node.node_id,
                        "source": node.metadata.get("file_name", "unknown"),
                        "question": qa["question"],
                        "ground_truth": qa["ground_truth"]
                    })
        
        print(f"Saving {len(dataset)} items to {self.output_file}...")
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2)
            
    def _create_dummy_data(self):
        return [
            {
                "id": "1",
                "source": "dummy.txt",
                "question": "What is DeepTutor?",
                "ground_truth": "DeepTutor is a local-first AI tutoring assistant."
            },
            {
                "id": "2",
                "source": "dummy.txt",
                "question": "How does PrivacyGuard work?",
                "ground_truth": "It uses Microsoft Presidio to scrub PII from text."
            }
        ]

if __name__ == "__main__":
    # Default paths
    base_dir = Path(__file__).parent.parent.parent
    knowledge_dir = base_dir / "data" / "knowledge_bases" / "DE-all"
    output_path = base_dir / "data" / "golden_dataset.json"
    
    # Ensure data dir exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    generator = GoldenSetGenerator(str(knowledge_dir), str(output_path))
    generator.generate(num_samples=5)
