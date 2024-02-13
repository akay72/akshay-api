import openai
import os
# Load configuration from the JSON file
def generate_outreach_email(lead_name, lead_website):
    # Set your OpenAI API key here. Consider using environment variables for production
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    prompt = f"""Lead information: ["{lead_name}","{lead_website}"]
                Product/service details: "National Utilisource is one of the leading North American providers of top-rated energy supply to consumers looking for large-scale energy consumption."""
    messages = [
        {"role": "system", "content": "You are a Sales Representative. Draft an initial outreach email to a potential lead based on the provided details."},
        {"role": "user", "content": prompt}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    return response.choices[0].message['content']
