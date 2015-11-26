# tag::basic[]
from neo4j.v1 import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost")
session = driver.session()

for n, n_sq in session.run("UNWIND range(1, 5) as n RETURN n, n *n AS n_sq"):
    print(n, n_sq)

session.close()
# tag::basic[]
