import asyncio
import argparse
from utils.database import connect_db
from utils.file_tools import read_file_async
from dotenv import load_dotenv


load_dotenv()

async def main():
  
    parser = argparse.ArgumentParser(description="Lire un fichier et afficher son contenu")
    parser.add_argument("path", help="Chemin vers le fichier à lire")
    args = parser.parse_args()

    path = args.path
    print(f"Reading file: {path}")
    conn = await connect_db()

    if not conn:
        return 
    
    try:
        page_num = 1
        text = ""
        
        async for page_text in read_file_async(path):
            text += page_text
            page_num += 1
                
        print("\nSaving to database...")
        await conn.execute("INSERT INTO documents (content) VALUES ($1)", text)
        
        print("Saving to file...")
        with open("output.txt", "w", encoding="utf-8") as output_file:
            output_file.write(text)
        print("Text has been written to output.txt")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await conn.close()
        



if __name__ == "__main__":
    asyncio.run(main())