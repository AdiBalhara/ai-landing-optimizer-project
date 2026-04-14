from utils.llm import get_llm


def analyze_ad(ad_text):
    llm = get_llm()
    prompt = f"""
    Analyze this ad and return JSON:

    {{
      "audience": "",
      "tone": "",
      "offer": "",
      "message": ""
    }}

    Ad:
    {ad_text}
    """

    return llm.invoke(prompt)