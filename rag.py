from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from typing import List, Dict
from langchain_core.messages import HumanMessage
import dotenv
import json
import re

class FAANGJobAnalyzer:
    def __init__(self):
        dotenv.load_dotenv()
        api_key = dotenv.get_key(dotenv.find_dotenv(), "OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.3)
        self.vector_db = None

    def load_jobs(self, jobs: List[Dict]):
        """Embed FAANG jobs using OpenAI"""
        texts = [f"{job['title']}\n{job['text']}" for job in jobs]
        self.vector_db = FAISS.from_texts(texts, self.embeddings)

    def analyze(self, resume_text: str) -> Dict:
        """Generate feedback by comparing resume to closest JD."""
        closest_jd = self.vector_db.similarity_search(resume_text, k=1)[0].page_content
        
        # Improved prompt with JSON formatting enforcement
        prompt = f"""
        Analyze this resume against the job description below.
        Return ONLY a valid JSON object with these keys:
        - "missing_keywords" (list of strings)
        - "score" (integer 0-100)
        - "advice" (list of strings)

        Example Output:
        {{
            "missing_keywords": ["Kubernetes", "AWS"],
            "score": 75,
            "advice": [
                "Add a projects section with cloud examples",
                "Quantify your achievements with metrics"
            ]
        }}

        Resume:
        {resume_text[:2000]}

        Job Description:
        {closest_jd}
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        try:
            # Extract JSON from markdown code blocks if present
            json_str = response.content
            if '```json' in json_str:
                json_str = json_str.split('```json')[1].split('```')[0]
            elif '```' in json_str:
                json_str = json_str.split('```')[1].split('```')[0]
                
            return json.loads(json_str.strip())
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}\nRaw response: {response.content}")
            # Fallback to manual extraction
            return {
                "missing_keywords": re.findall(r'"missing_keywords": \[(.*?)\]', response.content),
                "score": int(re.search(r'"score": (\d+)', response.content).group(1)),
                "advice": re.findall(r'"advice": \[(.*?)\]', response.content)
            }