# The Silmaril    
        
<html>     
	<img src="./images/silmarils.png" width="95%" align="center" alt="The-Silmaril: Practice #ontology building with Python (and other languages), © Shaurya Agarwal, 2025" />      
</html>        
      
      
Practice **#ontology engineering** with Python (and other languages).       
        
---    
      
## List of Ontologies    
      
### I. Very simple ones, to better understand the concepts      
      
I have tried to include rudimentary explanations on how to work out the ontologies, how one can create sample data to hydrate the ontology and finally how one can ask simple questions on the ontology (in PySpark).  
  
1. [Movie Domain](https://github.com/shauryashaurya/The-Silmaril/tree/main/o-01)      
2. [Music Domain](https://github.com/shauryashaurya/The-Silmaril/tree/main/o-02)      
      
### II. Getting more 'real' (and interesting) now        
      
  
Things are getting more intense... 'real-world' adjacent. Get a cup of coffee, put your game face on. :)
         
In some examples/exercises, we will leverage the "connected" nature of Ontologies for analysis, and see if we can build an intuition about how the Ontological representation is more beneficial for certain types of questions.
For the technically inclined, we'll try to show differences in code as well (comparing relational/OOP code with ontology/semantic approach).      
       
3. [Supply Chain (logistics, orders, suppliers, warehouses)](https://github.com/shauryashaurya/The-Silmaril/tree/main/o-03)      
4. [Property & Casualty Insurance](https://github.com/shauryashaurya/The-Silmaril/tree/main/o-04)       
5. [Construction (projects, tasks, materials, subcontractors, etc.)](https://github.com/shauryashaurya/The-Silmaril/tree/main/o-05)      
6. [Manufacturing (production lines, work orders, materials, products, etc.)](https://github.com/shauryashaurya/The-Silmaril/tree/main/o-06)      
7. [Stock Market / Equities Trading](https://github.com/shauryashaurya/The-Silmaril/tree/main/o-07)      
8. [Healthcare / EHR + Claims](https://github.com/shauryashaurya/The-Silmaril/tree/main/o-08)      

In future ontologies, we'll explore higher order problems like matching two ontologies, looking for limitations in an ontology etc. etc.  
  
  
### III. Higher order fun with Ontologies
    
As we get into more interesting Ontology examples, things get even more interesting for us.   
	
9. [Pharmaceutical Supply Chain *( + Bonus: Ontology Matching)*](https://github.com/shauryashaurya/The-Silmaril/tree/main/o-09)      
10. [EPCC / LEMS / PMBoK based ontology for a large construction project](https://github.com/shauryashaurya/The-Silmaril/tree/main/o-10)      
  
.  
---  
  
# Q&A

### Why no OWL yet?  
The project started with a focus on #Palantir Foundry, which does not have *direct* support for OWL (or RDF etc.), though one could write python code within foundry (or leverage libraries like `owlrl` and `rdflib` to play around with OWL data).  
  
### Really, why no OWL?  
*   **Foundry *Ontology*:** A data modeling and integration layer built *on top* of datasets. It's object-oriented and designed for operational use cases, data analysis, and application building *within* the Foundry ecosystem. It's optimized for performance and usability within Foundry's tools.
*   **OWL:** A formal language for knowledge representation based on description logics.  It uses RDF, RDFS, and related standards.  It's designed for open-world reasoning and inferencing.
*   ***versus*:** OWL can be thought of as a language for defining the *deepest conceptual model* of a domain, while Foundry's Ontology is for building a *practical, queryable, and actionable view* of data within Foundry. Net-net, at a practical pragmatic prosaic over-simplified level, Foundry provides a *framework* to define the Object Oriented hierarchy, along with actions etc. for easy integration across disparate (different-different) sources of data, while this was possible with libraries like Java-Spring (and other OOPs-Enterprise-Frameworks) it was not as easy to do or easy to understand once done. Foundry gets us closer, it just calls it "Ontology". OWL2 is knowledge engineering, it's busy with representing knowledge, not enterprise integration. 
  
Morever,  
*   **Foundry:** Primarily focused on data integration, operational workflows, building data-driven applications, and supporting decision-making *based on existing data*.
*   **OWL:** Often used for building knowledge bases, semantic web applications, and tasks requiring complex logical inference.
*   **Example:**  In Foundry, you're more likely to be building an application to track and manage assets, analyze supply chain data, or create a risk assessment dashboard than to be building a purely knowledge-based reasoning system.

Additionally,  
*   **Foundry:** 
	-- The Action framework allows you to define user-initiated actions that modify data in the Ontology. This is crucial for building operational applications. 
	-- Workshop provides a drag-and-drop interface for building interactive applications that directly use the Foundry Ontology. This is a major advantage for creating user-facing applications based on your data.
	-- The Ontology is tightly integrated with Foundry's robust security model. Permissions can be defined at the object type, property, and even individual object level. This is essential for building secure applications in enterprise environments.

*   **OWL:**  
	-- Doesn't have a concept of "actions" in the same way that Foundry does.  OWL is about *describing* knowledge, not about *acting* on it.
	-- Security and access control are typically handled *outside* the ontology itself (e.g., at the level of the triple store or application).
*   **Example:** In Foundry, you can create an Action to "Approve a Request" that updates the status of a `Request` object and potentially triggers other downstream actions.  This kind of operational workflow is not directly addressed by OWL.    
  
Finally, think about **Data Lineage and Provenance:**  
  
    *   **Foundry:**  Provides built-in data lineage tracking. You can see where data came from, how it was transformed, and who modified it. This is crucial for data governance and auditability.
    *   **OWL:** While you can *represent* provenance information using RDF and OWL (e.g., using the PROV-O ontology), it's not a core, built-in feature.
    * **Implication:** For tracking the origin and transformations of data which is important in many real-world scenarios, Foundry is better suited.
   
So, for now I thought I'll focus on Foundry first. This is not to say I am avoiding OWL, there are [other projects](https://github.com/shauryashaurya/elegant) I am working on, in parallel, where I am creating reasoners and proof checkers that will leverage OWL. In this initiative, I want to focus on 'how' to think about ontologies, without getting bogged down by the learning curve of OWL (which is not trivial) or getting stuck in unnecessary details of the myriad syntactical details instead of building a good intuition about how ontologies work.  
   
.  
  

  