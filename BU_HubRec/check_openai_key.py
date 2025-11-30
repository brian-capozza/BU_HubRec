import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai import APIStatusError

async def check_key_access():
    """Loads environment variables and attempts a test API call."""
    
    # 1. Load the .env file from the current directory
    load_dotenv()
    
    # Verify the key is in the environment
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ CRITICAL FAILURE: OPENAI_API_KEY not found in the environment.")
        print("Ensure the key is set in your .env file in the same directory.")
        return

    print("✅ Key found in environment. Attempting connection test...")

    try:
        # 2. Initialize the client (it automatically uses the environment variable)
        client = AsyncOpenAI()

        # 3. Make a simple, low-cost API request (The "ping")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say 'Key confirmed'"}
            ],
            max_tokens=5
        )

        # 4. Check the response content
        if "key confirmed" in response.choices[0].message.content.lower():
            print("\n🎉 SUCCESS: Connection to OpenAI is established!")
            print("The API key is valid and accessible by the AsyncOpenAI client.")
        else:
            # This is highly unlikely if the API call succeeded, but good to check
            print("\n⚠️ WARNING: API call succeeded but content was unexpected.")
            
    except APIStatusError as e:
        # This catches HTTP errors like 401 (Invalid key), 429 (Rate limit), etc.
        if e.status_code == 401:
            print(f"\n❌ FAILURE (401 Unauthorized): The key is LOADED but INVALID.")
            print("Please check the key value in your .env file. It is likely expired or misspelled.")
        else:
            print(f"\n❌ FAILURE: An API error occurred (Status {e.status_code}).")
            print(f"Error details: {e}")
            
    except Exception as e:
        # Catch network errors, unexpected crashes, etc.
        print(f"\n❌ FATAL ERROR: An unexpected error occurred: {type(e).__name__} - {e}")


if __name__ == "__main__":
    asyncio.run(check_key_access())