import os
import pandas as pd
from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL, XSD
from rdflib.term import URIRef
import json  # For parsing stringified JSON in movies.csv
import ast  # Alternative for literal evaluation if JSON parsing fails


def define_ontology_namespaces():
    ont_namespace_string = "http://example.org/movieontology/"
    data_namespace_string = "http://example.org/movieontology/data/"

    ont_ns = Namespace(ont_namespace_string)
    data_ns = Namespace(data_namespace_string)
    return ont_ns, data_ns


def create_ontology_graph_and_bind_prefixes(ont_ns, data_ns):
    graph = Graph()
    graph.bind("ex", ont_ns)
    graph.bind("data", data_ns)
    graph.bind("rdf", RDF)
    graph.bind("rdfs", RDFS)
    graph.bind("owl", OWL)
    graph.bind("xsd", XSD)
    return graph


def define_ontology_classes(graph, ont_ns):
    classes = {
        "Movie": ont_ns.Movie,
        "Person": ont_ns.Person,
        "Actor": ont_ns.Actor,
        "Director": ont_ns.Director,
        "Character": ont_ns.Character,
        "Genre": ont_ns.Genre
    }

    for name, uri in classes.items():
        graph.add((uri, RDF.type, OWL.Class))

    graph.add((classes["Actor"], RDFS.subClassOf, classes["Person"]))
    graph.add((classes["Director"], RDFS.subClassOf, classes["Person"]))

    return classes


def define_ontology_data_properties(graph, ont_ns, classes):
    data_properties_definitions = [
        (ont_ns.title, classes["Movie"], XSD.string),
        (ont_ns.releaseYear, classes["Movie"], XSD.integer),
        (ont_ns.duration, classes["Movie"], XSD.integer),
        (ont_ns.rating, classes["Movie"], XSD.float),
        # UniqueID for Movie
        (ont_ns.hasUniqueID, classes["Movie"], XSD.string, True, False),
        (ont_ns.name, classes["Person"], XSD.string),
        (ont_ns.birthDate, classes["Person"], XSD.date),
        # UniqueID for Person
        (ont_ns.personHasUniqueID, classes["Person"], XSD.string, False, True),
        (ont_ns.characterName, classes["Character"], XSD.string),
        # UniqueID for Character
        (ont_ns.characterHasUniqueID,
         classes["Character"], XSD.string, True, False),
        (ont_ns.genreName, classes["Genre"], XSD.string),
        # UniqueID for Genre
        (ont_ns.genreHasUniqueID, classes["Genre"], XSD.string, True, False),
        # For genre description
        (ont_ns.genreDescription, classes["Genre"], XSD.string)
    ]

    data_properties = {}
    for prop_uri_tuple in data_properties_definitions:
        prop_uri = prop_uri_tuple[0]
        domain_uri = prop_uri_tuple[1]
        range_uri = prop_uri_tuple[2]
        is_functional = prop_uri_tuple[3] if len(prop_uri_tuple) > 3 else False
        is_inverse_functional = prop_uri_tuple[4] if len(
            prop_uri_tuple) > 4 else False

        graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
        if domain_uri:
            graph.add((prop_uri, RDFS.domain, domain_uri))
        if range_uri:
            graph.add((prop_uri, RDFS.range, range_uri))
        if is_functional:
            graph.add((prop_uri, RDF.type, OWL.FunctionalProperty))
        if is_inverse_functional:
            graph.add((prop_uri, RDF.type, OWL.InverseFunctionalProperty))
        data_properties[prop_uri.split('/')[-1]] = prop_uri

    return data_properties


def define_ontology_object_properties(graph, ont_ns, classes):
    object_properties_definitions = [
        (ont_ns.hasActor, classes["Movie"], classes["Actor"], ont_ns.actedIn),
        (ont_ns.actedIn, classes["Actor"], classes["Movie"], ont_ns.hasActor),
        (ont_ns.hasDirector, classes["Movie"],
         classes["Director"], ont_ns.directed),
        (ont_ns.directed, classes["Director"],
         classes["Movie"], ont_ns.hasDirector),
        (ont_ns.belongsToGenre, classes["Movie"], classes["Genre"], None),
        (ont_ns.hasCharacter, classes["Movie"],
         classes["Character"], ont_ns.characterIn),
        (ont_ns.characterIn, classes["Character"],
         classes["Movie"], ont_ns.hasCharacter),
        (ont_ns.playsCharacter, classes["Actor"], classes["Character"], None)
    ]

    object_properties = {}
    for prop_uri, domain_uri, range_uri, inverse_prop_uri in object_properties_definitions:
        graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
        if domain_uri:
            graph.add((prop_uri, RDFS.domain, domain_uri))
        if range_uri:
            graph.add((prop_uri, RDFS.range, range_uri))
        if inverse_prop_uri:
            graph.add((prop_uri, OWL.inverseOf, inverse_prop_uri))
        object_properties[prop_uri.split('/')[-1]] = prop_uri

    return object_properties


def safe_literal_eval(s):
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        # Fallback for potentially tricky strings, try replacing single quotes if it looks like JSON
        try:
            return json.loads(s.replace("'", "\""))
        except json.JSONDecodeError:
            print(f"Warning: Could not parse string: {s}")
            return None


def load_data_from_csv(file_path):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            print(f"Error reading CSV {file_path}: {e}")
            return pd.DataFrame()
    print(f"Warning: File not found {file_path}")
    return pd.DataFrame()


def populate_instances_from_data(graph, data_ns, classes, data_props, obj_props, data_dir):

    actors_df = load_data_from_csv(os.path.join(
        data_dir, "actors.csv"))  # id,name,birthDate
    for _, row in actors_df.iterrows():
        actor_id = str(row['id']).strip()
        person_uri = data_ns[f"person_{actor_id}"]
        graph.add((person_uri, RDF.type, classes["Person"]))
        # Actor is a subclass of Person
        graph.add((person_uri, RDF.type, classes["Actor"]))
        graph.add(
            (person_uri, data_props["personHasUniqueID"], Literal(actor_id)))
        if pd.notna(row.get('name')):
            graph.add((person_uri, data_props["name"], Literal(
                str(row['name']).strip(), datatype=XSD.string)))
        if pd.notna(row.get('birthDate')):
            try:
                graph.add((person_uri, data_props["birthDate"], Literal(
                    str(row['birthDate']).strip(), datatype=XSD.date)))
            except ValueError:
                print(
                    f"Warning: Could not parse birthDate '{row['birthDate']}' for actor {actor_id}")

    directors_df = load_data_from_csv(os.path.join(
        data_dir, "directors.csv"))  # id,name,birthDate
    for _, row in directors_df.iterrows():
        director_id = str(row['id']).strip()
        person_uri = data_ns[f"person_{director_id}"]
        graph.add((person_uri, RDF.type, classes["Person"]))
        # Director is a subclass of Person
        graph.add((person_uri, RDF.type, classes["Director"]))
        graph.add(
            (person_uri, data_props["personHasUniqueID"], Literal(director_id)))
        if pd.notna(row.get('name')):
            graph.add((person_uri, data_props["name"], Literal(
                str(row['name']).strip(), datatype=XSD.string)))
        if pd.notna(row.get('birthDate')):
            try:
                graph.add((person_uri, data_props["birthDate"], Literal(
                    str(row['birthDate']).strip(), datatype=XSD.date)))
            except ValueError:
                print(
                    f"Warning: Could not parse birthDate '{row['birthDate']}' for director {director_id}")

    characters_df = load_data_from_csv(
        os.path.join(data_dir, "characters.csv"))  # id,name
    for _, row in characters_df.iterrows():
        char_id = str(row['id']).strip()
        character_uri = data_ns[f"character_{char_id}"]
        graph.add((character_uri, RDF.type, classes["Character"]))
        graph.add(
            (character_uri, data_props["characterHasUniqueID"], Literal(char_id)))
        if pd.notna(row.get('name')):
            graph.add((character_uri, data_props["characterName"], Literal(
                str(row['name']).strip(), datatype=XSD.string)))

    # Store created genres to avoid duplicates if only name is key
    # However, the 'genres' column in movies.csv has descriptions, making them more unique.
    # We will create genre instances on the fly when processing movies.
    processed_genres = {}

    movies_df = load_data_from_csv(os.path.join(data_dir, "movies.csv"))
    # Columns: id,title,releaseYear,duration,rating,directorID,actorCharacterPairs,genres,genres_tru
    for _, row in movies_df.iterrows():
        movie_id_str = str(row['id']).strip()
        movie_uri = data_ns[f"movie_{movie_id_str}"]
        graph.add((movie_uri, RDF.type, classes["Movie"]))
        # Changed from hasUniqueMovieID
        graph.add(
            (movie_uri, data_props["hasUniqueID"], Literal(movie_id_str)))

        if pd.notna(row.get('title')):
            graph.add((movie_uri, data_props["title"], Literal(
                str(row['title']).strip(), datatype=XSD.string)))
        if pd.notna(row.get('releaseYear')):
            try:
                graph.add((movie_uri, data_props["releaseYear"], Literal(
                    int(row['releaseYear']), datatype=XSD.integer)))
            except ValueError:
                print(
                    f"Warning: Could not parse releaseYear '{row['releaseYear']}' for movie {movie_id_str}")
        if pd.notna(row.get('duration')):
            try:
                graph.add((movie_uri, data_props["duration"], Literal(
                    int(row['duration']), datatype=XSD.integer)))
            except ValueError:
                print(
                    f"Warning: Could not parse duration '{row['duration']}' for movie {movie_id_str}")
        if pd.notna(row.get('rating')):
            try:
                graph.add((movie_uri, data_props["rating"], Literal(
                    float(row['rating']), datatype=XSD.float)))
            except ValueError:
                print(
                    f"Warning: Could not parse rating '{row['rating']}' for movie {movie_id_str}")

        if pd.notna(row.get('directorID')):
            director_id = str(row['directorID']).strip()
            director_uri = data_ns[f"person_{director_id}"]
            graph.add((movie_uri, obj_props["hasDirector"], director_uri))
            # Ensure director instance exists if not defined separately (though actors/directors CSVs should handle this)
            if (director_uri, RDF.type, classes["Director"]) not in graph:
                graph.add((director_uri, RDF.type, classes["Director"]))
                # Also Person
                graph.add((director_uri, RDF.type, classes["Person"]))
                graph.add(
                    (director_uri, data_props["personHasUniqueID"], Literal(director_id)))
                # Name and birthDate would be missing if not in directors.csv

        if pd.notna(row.get('actorCharacterPairs')):
            actor_char_pairs_str = str(row['actorCharacterPairs'])
            pairs = safe_literal_eval(actor_char_pairs_str)
            if isinstance(pairs, list):
                for pair in pairs:
                    if isinstance(pair, dict) and 'actorID' in pair and 'characterID' in pair:
                        actor_id = str(pair['actorID']).strip()
                        char_id = str(pair['characterID']).strip()

                        actor_uri = data_ns[f"person_{actor_id}"]
                        character_uri = data_ns[f"character_{char_id}"]

                        graph.add(
                            (movie_uri, obj_props["hasActor"], actor_uri))
                        graph.add(
                            (actor_uri, obj_props["playsCharacter"], character_uri))
                        # Movie has this character
                        graph.add(
                            (movie_uri, obj_props["hasCharacter"], character_uri))
                        # Character is in this movie
                        graph.add(
                            (character_uri, obj_props["characterIn"], movie_uri))

                        # Ensure actor/character instances exist if not defined separately
                        if (actor_uri, RDF.type, classes["Actor"]) not in graph:
                            graph.add((actor_uri, RDF.type, classes["Actor"]))
                            graph.add((actor_uri, RDF.type, classes["Person"]))
                            graph.add(
                                (actor_uri, data_props["personHasUniqueID"], Literal(actor_id)))
                        if (character_uri, RDF.type, classes["Character"]) not in graph:
                            graph.add(
                                (character_uri, RDF.type, classes["Character"]))
                            graph.add(
                                (character_uri, data_props["characterHasUniqueID"], Literal(char_id)))

        if pd.notna(row.get('genres')):
            genres_str = str(row['genres'])
            genre_list_data = safe_literal_eval(genres_str)
            if isinstance(genre_list_data, list):
                for genre_data in genre_list_data:
                    if isinstance(genre_data, dict) and 'name' in genre_data:
                        genre_name_val = str(genre_data['name']).strip()
                        genre_desc_val = str(
                            genre_data.get('description', '')).strip()

                        # Create a URI based on a sanitized name to try and reuse genre instances
                        sane_genre_name = "".join(
                            c if c.isalnum() else "_" for c in genre_name_val.lower())
                        genre_uri = data_ns[f"genre_{sane_genre_name}"]

                        if (genre_uri, RDF.type, classes["Genre"]) not in graph:
                            graph.add((genre_uri, RDF.type, classes["Genre"]))
                            graph.add((genre_uri, data_props["genreName"], Literal(
                                genre_name_val, datatype=XSD.string)))
                            # Use a unique ID for genre if needed, here sane_genre_name acts as one
                            graph.add(
                                (genre_uri, data_props["genreHasUniqueID"], Literal(sane_genre_name)))
                            if genre_desc_val:
                                graph.add((genre_uri, data_props["genreDescription"], Literal(
                                    genre_desc_val, datatype=XSD.string)))

                        graph.add(
                            (movie_uri, obj_props["belongsToGenre"], genre_uri))
            # Fallback or alternative: genres_tru column
        elif pd.notna(row.get('genres_tru')):
            genres_tru_str = str(row['genres_tru'])
            for genre_name_val_tru in genres_tru_str.split('|'):
                genre_name_val_tru = genre_name_val_tru.strip()
                if genre_name_val_tru and genre_name_val_tru != "(no genres listed)":
                    sane_genre_name_tru = "".join(
                        c if c.isalnum() else "_" for c in genre_name_val_tru.lower())
                    genre_uri_tru = data_ns[f"genre_{sane_genre_name_tru}"]
                    if (genre_uri_tru, RDF.type, classes["Genre"]) not in graph:
                        graph.add((genre_uri_tru, RDF.type, classes["Genre"]))
                        graph.add((genre_uri_tru, data_props["genreName"], Literal(
                            genre_name_val_tru, datatype=XSD.string)))
                        graph.add(
                            (genre_uri_tru, data_props["genreHasUniqueID"], Literal(sane_genre_name_tru)))
                    graph.add(
                        (movie_uri, obj_props["belongsToGenre"], genre_uri_tru))


def serialize_graph(graph, output_dir, file_name_base):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    rdf_file_path = os.path.join(output_dir, f"{file_name_base}.ttl")
    # Using .owl extension for RDF/XML
    owl_file_path = os.path.join(output_dir, f"{file_name_base}.owl")

    graph.serialize(destination=rdf_file_path, format="turtle")
    print(f"RDF (Turtle) file saved to: {rdf_file_path}")

    graph.serialize(destination=owl_file_path, format="xml")
    print(f"OWL (RDF/XML) file saved to: {owl_file_path}")


def main():
    data_directory = "./data"
    output_directory = "./data"
    output_file_basename = "movie_ontology_and_data"

    ont_ns, data_ns = define_ontology_namespaces()

    graph = create_ontology_graph_and_bind_prefixes(ont_ns, data_ns)

    defined_classes = define_ontology_classes(graph, ont_ns)

    defined_data_properties = define_ontology_data_properties(
        graph, ont_ns, defined_classes)

    defined_object_properties = define_ontology_object_properties(
        graph, ont_ns, defined_classes)

    populate_instances_from_data(graph, data_ns, defined_classes,
                                 defined_data_properties, defined_object_properties, data_directory)

    serialize_graph(graph, output_directory, output_file_basename)

    print(f"Processed {len(graph)} triples.")


if __name__ == "__main__":
    main()
