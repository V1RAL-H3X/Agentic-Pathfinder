from neo4j import GraphDatabase

# Update these with your local Neo4j credentials and URI
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "your_password_here")


def test_connection():
    # Establish a driver connection
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # Verify connectivity
        driver.verify_connectivity()
        print("Successfully connected to Neo4j!")

        # Run a simple query to count nodes or grab a few labels
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN labels(n) AS Label, count(n) AS Count")
            print("\nDatabase Node Summary:")
            for record in result:
                print(f"- {record['Label']}: {record['Count']} nodes")


if __name__ == "__main__":
    test_connection()