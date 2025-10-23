from neo4j import GraphDatabase
import os

def test_connection(uri, username, password):
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful' AS message")
            print(result.single()["message"])
        driver.close()
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

# Usage
if __name__ == "__main__":
    uri=os.getenv("NEO4J_URI")
    username=os.getenv("NEO4J_USERNAME")
    password=os.getenv("NEO4J_PASSWORD")    
    
    test_connection(uri, username, password)