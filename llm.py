import os
from dotenv import load_dotenv # type: ignore
import google.generativeai as genai # type: ignore

# 1. Load Gemini API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

# 2. Set up Gemini model
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

def analyze_log_chunks(chunks: list) -> list:
    """
    Sends each chunk of log to the Gemini API and receives AI-generated analysis.

    Parameters:
        chunks (list): List of log chunks (each chunk is a string)

    Returns:
        List of dicts with summary, issue, suggestion for each chunk.
    """
    results = []

    for chunk in chunks:
        prompt = generate_prompt(chunk)

        try:
            response = model.generate_content(prompt)
            
                        # ✅ FIXED: Extract from parts[0].text instead of response.text
            content = ""
            if hasattr(response, "text") and response.text:
                content = response.text.strip()
            elif hasattr(response, "parts") and response.parts:
                content = response.parts[0].text.strip()

            result = parse_response(content)

            result["score"] = calculate_risk_score(result.get("issue", ""))
            result["sql_recommendation"] = generate_sql_recommendations(result.get("suggestion", ""))

            results.append(result)


        except Exception as e:
            results.append({
                "summary": "❌ Error during analysis.",
                "issue": str(e),
                "suggestion": "Please check the input or API key."
            })

    return results


def generate_prompt(chunk: str) -> str:
    """
    Builds a prompt asking Gemini to summarize and analyze a slow query log chunk.
    """
    return f"""
You are an expert MySQL performance analyst.

Here is a chunk of a slow query log:
------------------
{chunk}
------------------

Please provide the following:
1. A summary of the log
2. The most likely performance issue(s)
3. Suggestions to optimize or resolve the issue(s)

Use clear and short bullet points.
Answer in the format:

Summary: ...
Issue: ...
Suggestion: ...
"""


def parse_response(content: str) -> dict:
    """
    Parses the raw Gemini response into structured fields: summary, issue, suggestion.
    Even if they span multiple lines.
    """
    result = {"summary": "", "issue": "", "suggestion": ""}
    current_section = None

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.lower().startswith("summary:"):
            current_section = "summary"
            result["summary"] = line[len("summary:"):].strip()
        elif line.lower().startswith("issue:"):
            current_section = "issue"
            result["issue"] = line[len("issue:"):].strip()
        elif line.lower().startswith("suggestion:"):
            current_section = "suggestion"
            result["suggestion"] = line[len("suggestion:"):].strip()
        elif current_section:
            # Multi-line content → append with newline
            result[current_section] += "\n" + line

    return result

def calculate_risk_score(issue_text: str) -> int:
    """Assigns a risk score based on keywords in the issue description."""
    issue_text = issue_text.lower()
    score = 0

    if "full table scan" in issue_text or "no index" in issue_text:
        score += 40
    if "repeated query" in issue_text or "duplicate query" in issue_text:
        score += 20
    if "select *" in issue_text:
        score += 10
    if "like '%" in issue_text or "leading wildcard" in issue_text:
        score += 15
    if "missing index" in issue_text:
        score += 30
    if "inefficient" in issue_text:
        score += 10

    return min(score, 100)


def generate_sql_recommendations(suggestion_text: str) -> list:
    """Extracts and formats likely SQL optimization suggestions from AI output."""
    lines = suggestion_text.splitlines()
    recommendations = []

    for line in lines:
        line = line.strip()

        # Recommend creating index
        if "create index" in line.lower() or "add index" in line.lower():
            if "on" in line.lower():
                recommendations.append(line)

        # Recommend avoiding SELECT *
        elif "select *" in line.lower():
            recommendations.append("Avoid SELECT *; select only needed columns.")

        # LIKE wildcard optimization
        elif "like '%" in line.lower() or "leading wildcard" in line.lower():
            recommendations.append("Avoid leading wildcard in LIKE; consider FULLTEXT or RIGHT().")

        # Query caching suggestion
        elif "cache" in line.lower():
            recommendations.append("Consider query result caching (e.g., Redis, Memcached).")

    return recommendations


def build_prompt_with_log(user_question: str, log_data: str) -> str:
    safe_question = user_question.replace("'", "\"")
    return f"""
        You are a MySQL performance expert. A user has uploaded a slow query log and has a question.

        Here is the user's question:
        "{safe_question}"

        Here is the related MySQL log:
        ----------------------
        {log_data}
        ----------------------

        Based on the log, please provide an expert-level answer to the question.
        Use clear, concise language.
        """
