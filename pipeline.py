import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Get Anthropic API key
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

def fetch_recent_logs() -> str:
    """
    Fetches all records from the server_logs table and returns them as a formatted JSON string.
    
    Returns:
        str: A JSON string containing the server logs data.
    
    Raises:
        Exception: If there's an error connecting to the database or querying the table.
    """
    try:
        # Check if credentials are available
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in the .env file")
        
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Query the server_logs table
        response = supabase.table('server_logs').select('*').execute()
        
        # Check if data is empty
        if not response.data:
            return json.dumps({"message": "No logs found in the server_logs table"}, indent=2)
        
        # Format the data as a clean JSON string
        return json.dumps(response.data, indent=2, default=str)
    
    except Exception as e:
        # Handle connection or query errors
        error_message = f"Error fetching logs: {str(e)}"
        return json.dumps({"error": error_message}, indent=2)

def analyze_anomalies(data_json: str) -> str:
    """
    Analyzes server log data using Claude AI to identify anomalies.
    
    Args:
        data_json (str): JSON string containing server log data.
    
    Returns:
        str: Claude's analysis report in markdown format.
    
    Raises:
        Exception: If there's an error with the Anthropic API.
    """
    try:
        # Check if API key is available
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY must be set in the .env file")
        
        # Initialize Anthropic client
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # System prompt for Claude
        system_prompt = """You are an expert Data Analyst monitoring server performance. Review this JSON data of daily server logs. Identify any severe anomalies (like massive spikes in response times), explain why they are anomalous, and output a clean, 3-bullet-point summary report in markdown."""
        
        # Create the message
        message = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Please analyze this server log data:\n\n{data_json}"
                }
            ]
        )
        
        return message.content[0].text
    
    except Exception as e:
        # Handle API errors
        error_message = f"Error analyzing data with Claude: {str(e)}"
        return f"## Analysis Error\n\n- {error_message}"

# Example usage (uncomment to test)
if __name__ == "__main__":
    print("Fetching recent logs...")
    logs = fetch_recent_logs()
    print("Logs retrieved successfully.\n")
    
    print("Analyzing anomalies with Claude AI...")
    analysis = analyze_anomalies(logs)
    print("Analysis complete.\n")
    
    print("=== CLAUDE'S ANALYSIS REPORT ===")
    print(analysis)