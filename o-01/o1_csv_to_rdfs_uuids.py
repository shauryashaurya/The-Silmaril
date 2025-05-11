import os
import pandas as pd
from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL, XSD
from rdflib.term import URIRef
import json
import ast
import uuid

# ... (All functions from define_ontology_namespaces to populate_instances_from_data remain the same as the corrected version from the previous step) ...
# Functions that remain unchanged:
# def define_ontology_namespaces():
# def create_ontology_graph_and_bind_prefixes(ont_ns):
# def define_ontology_classes(graph, ont_ns):
# def define_ontology_data_properties(graph, ont_ns, classes):
# def define_ontology_object_properties(graph, ont_ns, classes):
# def safe_literal_eval(s_val):
# def load_data_from_csv(file_path):
# def get_or_create_urn(original_id_str, id_to_urn_map):
# def populate_instances_from_data(graph, ont_ns, classes, data_props_map, obj_props_map, data_dir):
# (Make sure these are the versions that correctly handle data_props_map and obj_props_map)


def define_ontology_namespaces():
    ont_namespace_string = "http://example.org/movieontology/"
    ont_ns = Namespace(ont_namespace_string)
    return ont_ns


def create_ontology_graph_and_bind_prefixes(ont_ns):
    graph = Graph()
    graph.bind("ex", ont_ns)
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

    for class_uri in classes.values():
        graph.add((class_uri, RDF.type, OWL.Class))

    graph.add((classes["Actor"], RDFS.subClassOf, classes["Person"]))
    graph.add((classes["Director"], RDFS.subClassOf, classes["Person"]))

    return classes


def define_ontology_data_properties(graph, ont_ns, classes):
    data_properties_definitions = [
        (ont_ns.title, classes["Movie"], XSD.string, False, False, "title"),
        (ont_ns.releaseYear, classes["Movie"],
         XSD.integer, False, False, "releaseYear"),
        (ont_ns.duration, classes["Movie"],
         XSD.integer, False, False, "duration"),
        (ont_ns.rating, classes["Movie"], XSD.float, False, False, "rating"),
        (ont_ns.externalID, None, XSD.string, True, False, "externalID"),
        (ont_ns.name, classes["Person"], XSD.string, False, False, "name"),
        (ont_ns.birthDate, classes["Person"],
         XSD.date, False, False, "birthDate"),
        (ont_ns.characterName, classes["Character"],
         XSD.string, False, False, "characterName"),
        (ont_ns.genreName, classes["Genre"],
         XSD.string, False, False, "genreName"),
        (ont_ns.genreDescription, classes["Genre"],
         XSD.string, False, False, "genreDescription")
    ]

    created_data_properties = {}
    for prop_uri, domain_uri, range_uri, is_functional, is_inverse_functional, dict_key_name in data_properties_definitions:
        graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
        if domain_uri:
            graph.add((prop_uri, RDFS.domain, domain_uri))
        if range_uri:
            graph.add((prop_uri, RDFS.range, range_uri))
        if is_functional:
            graph.add((prop_uri, RDF.type, OWL.FunctionalProperty))
        if is_inverse_functional:
            graph.add((prop_uri, RDF.type, OWL.InverseFunctionalProperty))
        created_data_properties[dict_key_name] = prop_uri

    return created_data_properties


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

    created_object_properties = {}
    for prop_uri, domain_uri, range_uri, inverse_prop_uri in object_properties_definitions:
        graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
        if domain_uri:
            graph.add((prop_uri, RDFS.domain, domain_uri))
        if range_uri:
            graph.add((prop_uri, RDFS.range, range_uri))
        if inverse_prop_uri:
            graph.add((prop_uri, OWL.inverseOf, inverse_prop_uri))
        created_object_properties[prop_uri.split('/')[-1]] = prop_uri

    return created_object_properties


def safe_literal_eval(s_val):
    if not isinstance(s_val, str):
        return s_val
    try:
        return ast.literal_eval(s_val)
    except (ValueError, SyntaxError, TypeError):
        try:
            return json.loads(s_val.replace("'", "\""))
        except json.JSONDecodeError:
            print(
                f"Warning: Could not parse string as Python literal or JSON: {s_val}")
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


def get_or_create_urn(original_id_str, id_to_urn_map):
    if original_id_str not in id_to_urn_map:
        id_to_urn_map[original_id_str] = URIRef(f"urn:uuid:{uuid.uuid4()}")
    return id_to_urn_map[original_id_str]


def populate_instances_from_data(graph, ont_ns, classes, data_props_map, obj_props_map, data_dir):

    actor_id_to_urn = {}
    director_id_to_urn = {}
    character_id_to_urn = {}
    movie_id_to_urn = {}
    genre_name_to_urn = {}

    external_id_prop = data_props_map["externalID"]

    actors_df = load_data_from_csv(os.path.join(data_dir, "actors.csv"))
    for _, row in actors_df.iterrows():
        original_actor_id = str(row['id']).strip()
        actor_urn = get_or_create_urn(original_actor_id, actor_id_to_urn)

        graph.add((actor_urn, RDF.type, classes["Person"]))
        graph.add((actor_urn, RDF.type, classes["Actor"]))
        graph.add((actor_urn, external_id_prop, Literal(original_actor_id)))
        if pd.notna(row.get('name')):
            graph.add((actor_urn, data_props_map["name"], Literal(
                str(row['name']).strip(), datatype=XSD.string)))
        if pd.notna(row.get('birthDate')):
            try:
                birth_date_str = str(row['birthDate']).strip()
                pd.to_datetime(birth_date_str)
                graph.add((actor_urn, data_props_map["birthDate"], Literal(
                    birth_date_str, datatype=XSD.date)))
            except (ValueError, TypeError) as e:
                print(
                    f"Warning: Could not parse birthDate '{row.get('birthDate')}' for actor {original_actor_id}. Error: {e}")

    directors_df = load_data_from_csv(os.path.join(data_dir, "directors.csv"))
    for _, row in directors_df.iterrows():
        original_director_id = str(row['id']).strip()
        director_urn = get_or_create_urn(
            original_director_id, director_id_to_urn)

        graph.add((director_urn, RDF.type, classes["Person"]))
        graph.add((director_urn, RDF.type, classes["Director"]))
        graph.add((director_urn, external_id_prop,
                  Literal(original_director_id)))
        if pd.notna(row.get('name')):
            graph.add((director_urn, data_props_map["name"], Literal(
                str(row['name']).strip(), datatype=XSD.string)))
        if pd.notna(row.get('birthDate')):
            try:
                birth_date_str = str(row['birthDate']).strip()
                pd.to_datetime(birth_date_str)
                graph.add((director_urn, data_props_map["birthDate"], Literal(
                    birth_date_str, datatype=XSD.date)))
            except (ValueError, TypeError) as e:
                print(
                    f"Warning: Could not parse birthDate '{row.get('birthDate')}' for director {original_director_id}. Error: {e}")

    characters_df = load_data_from_csv(
        os.path.join(data_dir, "characters.csv"))
    for _, row in characters_df.iterrows():
        original_char_id = str(row['id']).strip()
        character_urn = get_or_create_urn(
            original_char_id, character_id_to_urn)

        graph.add((character_urn, RDF.type, classes["Character"]))
        graph.add((character_urn, external_id_prop, Literal(original_char_id)))
        if pd.notna(row.get('name')):
            graph.add((character_urn, data_props_map["characterName"], Literal(
                str(row['name']).strip(), datatype=XSD.string)))

    movies_df = load_data_from_csv(os.path.join(data_dir, "movies.csv"))
    for _, row in movies_df.iterrows():
        original_movie_id = str(row['id']).strip()
        movie_urn = get_or_create_urn(original_movie_id, movie_id_to_urn)

        graph.add((movie_urn, RDF.type, classes["Movie"]))
        graph.add((movie_urn, external_id_prop, Literal(original_movie_id)))

        if pd.notna(row.get('title')):
            graph.add((movie_urn, data_props_map["title"], Literal(
                str(row['title']).strip(), datatype=XSD.string)))
        if pd.notna(row.get('releaseYear')):
            try:
                graph.add((movie_urn, data_props_map["releaseYear"], Literal(
                    int(float(row['releaseYear'])), datatype=XSD.integer)))
            except (ValueError, TypeError) as e:
                print(
                    f"Warning: Could not parse releaseYear '{row.get('releaseYear')}' for movie {original_movie_id}. Error: {e}")
        if pd.notna(row.get('duration')):
            try:
                graph.add((movie_urn, data_props_map["duration"], Literal(
                    int(float(row['duration'])), datatype=XSD.integer)))
            except (ValueError, TypeError) as e:
                print(
                    f"Warning: Could not parse duration '{row.get('duration')}' for movie {original_movie_id}. Error: {e}")
        if pd.notna(row.get('rating')):
            try:
                graph.add((movie_urn, data_props_map["rating"], Literal(
                    float(row['rating']), datatype=XSD.float)))
            except (ValueError, TypeError) as e:
                print(
                    f"Warning: Could not parse rating '{row.get('rating')}' for movie {original_movie_id}. Error: {e}")

        if pd.notna(row.get('directorID')):
            original_director_id = str(row['directorID']).strip()
            director_urn = get_or_create_urn(
                original_director_id, director_id_to_urn)
            graph.add((movie_urn, obj_props_map["hasDirector"], director_urn))
            if not any(graph.triples((director_urn, RDF.type, classes["Director"]))):
                graph.add((director_urn, RDF.type, classes["Director"]))
                graph.add((director_urn, RDF.type, classes["Person"]))
                graph.add((director_urn, external_id_prop,
                          Literal(original_director_id)))

        if pd.notna(row.get('actorCharacterPairs')):
            actor_char_pairs_str = row['actorCharacterPairs']
            pairs = safe_literal_eval(actor_char_pairs_str)
            if isinstance(pairs, list):
                for pair in pairs:
                    if isinstance(pair, dict) and 'actorID' in pair and 'characterID' in pair:
                        original_actor_id = str(pair['actorID']).strip()
                        original_char_id = str(pair['characterID']).strip()

                        actor_urn = get_or_create_urn(
                            original_actor_id, actor_id_to_urn)
                        character_urn = get_or_create_urn(
                            original_char_id, character_id_to_urn)

                        graph.add(
                            (movie_urn, obj_props_map["hasActor"], actor_urn))
                        graph.add(
                            (actor_urn, obj_props_map["playsCharacter"], character_urn))
                        graph.add(
                            (movie_urn, obj_props_map["hasCharacter"], character_urn))

                        if not any(graph.triples((actor_urn, RDF.type, classes["Actor"]))):
                            graph.add((actor_urn, RDF.type, classes["Actor"]))
                            graph.add((actor_urn, RDF.type, classes["Person"]))
                            graph.add((actor_urn, external_id_prop,
                                      Literal(original_actor_id)))
                        if not any(graph.triples((character_urn, RDF.type, classes["Character"]))):
                            graph.add(
                                (character_urn, RDF.type, classes["Character"]))
                            graph.add((character_urn, external_id_prop,
                                      Literal(original_char_id)))

        if pd.notna(row.get('genres')):
            genres_val = row['genres']
            genre_list_data = safe_literal_eval(genres_val)
            if isinstance(genre_list_data, list):
                for genre_data in genre_list_data:
                    if isinstance(genre_data, dict) and 'name' in genre_data:
                        genre_name_val = str(genre_data['name']).strip()
                        genre_desc_val = str(
                            genre_data.get('description', '')).strip()

                        genre_urn = genre_name_to_urn.get(genre_name_val)
                        if not genre_urn:
                            genre_urn = URIRef(f"urn:uuid:{uuid.uuid4()}")
                            genre_name_to_urn[genre_name_val] = genre_urn

                            graph.add((genre_urn, RDF.type, classes["Genre"]))
                            graph.add((genre_urn, data_props_map["genreName"], Literal(
                                genre_name_val, datatype=XSD.string)))
                            graph.add((genre_urn, external_id_prop, Literal(
                                genre_name_val.lower().replace(" ", "_"))))
                            if genre_desc_val:
                                graph.add((genre_urn, data_props_map["genreDescription"], Literal(
                                    genre_desc_val, datatype=XSD.string)))

                        graph.add(
                            (movie_urn, obj_props_map["belongsToGenre"], genre_urn))
        elif pd.notna(row.get('genres_tru')):
            genres_tru_str = str(row['genres_tru'])
            for genre_name_val_tru in genres_tru_str.split('|'):
                genre_name_val_tru = genre_name_val_tru.strip()
                if genre_name_val_tru and genre_name_val_tru != "(no genres listed)":
                    genre_urn_tru = genre_name_to_urn.get(genre_name_val_tru)
                    if not genre_urn_tru:
                        genre_urn_tru = URIRef(f"urn:uuid:{uuid.uuid4()}")
                        genre_name_to_urn[genre_name_val_tru] = genre_urn_tru

                        graph.add((genre_urn_tru, RDF.type, classes["Genre"]))
                        graph.add((genre_urn_tru, data_props_map["genreName"], Literal(
                            genre_name_val_tru, datatype=XSD.string)))
                        graph.add((genre_urn_tru, external_id_prop, Literal(
                            genre_name_val_tru.lower().replace(" ", "_"))))
                    graph.add(
                        (movie_urn, obj_props_map["belongsToGenre"], genre_urn_tru))


# Parameters data_props_map and obj_props_map are not used if context is hardcoded
def serialize_graph(graph, output_dir, file_name_base, ont_ns, data_props_map, obj_props_map):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    rdf_file_path = os.path.join(output_dir, f"{file_name_base}.ttl")
    owl_file_path = os.path.join(output_dir, f"{file_name_base}.owl")
    jsonld_file_path = os.path.join(output_dir, f"{file_name_base}.jsonld")

    graph.serialize(destination=rdf_file_path, format="turtle")
    print(f"RDF (Turtle) file saved to: {rdf_file_path}")

    graph.serialize(destination=owl_file_path, format="xml")
    print(f"OWL (RDF/XML) file saved to: {owl_file_path}")

    # Using the extensive, explicit context provided by the user
    context = {
        "ex": str(ont_ns),
        "rdf": str(RDF),
        "rdfs": str(RDFS),
        "owl": str(OWL),
        "xsd": str(XSD),
        "id": "@id",
        "type": "@type",
        "Movie": "ex:Movie",
        "Person": "ex:Person",
        "Actor": "ex:Actor",
        "Director": "ex:Director",
        "Character": "ex:Character",
        "Genre": "ex:Genre",
        "title": "ex:title",
        "releaseYear": {"@id": "ex:releaseYear", "@type": "xsd:integer"},
        "duration": {"@id": "ex:duration", "@type": "xsd:integer"},
        "rating": {"@id": "ex:rating", "@type": "xsd:float"},
        # Matches the key used in define_ontology_data_properties
        "externalID": "ex:externalID",
        "name": "ex:name",
        "birthDate": {"@id": "ex:birthDate", "@type": "xsd:date"},
        "characterName": "ex:characterName",
        "genreName": "ex:genreName",
        "genreDescription": "ex:genreDescription",
        "hasActor": {"@id": "ex:hasActor", "@type": "@id"},
        "actedIn": {"@id": "ex:actedIn", "@type": "@id"},
        "hasDirector": {"@id": "ex:hasDirector", "@type": "@id"},
        "directed": {"@id": "ex:directed", "@type": "@id"},
        "belongsToGenre": {"@id": "ex:belongsToGenre", "@type": "@id"},
        "hasCharacter": {"@id": "ex:hasCharacter", "@type": "@id"},
        "characterIn": {"@id": "ex:characterIn", "@type": "@id"},
        "playsCharacter": {"@id": "ex:playsCharacter", "@type": "@id"}
    }

    graph.serialize(destination=jsonld_file_path, format="json-ld",
                    context=context, indent=2, auto_compact=True)
    print(f"JSON-LD file saved to: {jsonld_file_path}")


def main():
    data_directory = "./data"
    output_directory = "./data"
    output_file_basename = "movie_ontology_data_uuid"

    ont_ns = define_ontology_namespaces()

    graph = create_ontology_graph_and_bind_prefixes(ont_ns)

    defined_classes = define_ontology_classes(graph, ont_ns)

    actual_data_properties = define_ontology_data_properties(
        graph, ont_ns, defined_classes)
    actual_object_properties = define_ontology_object_properties(
        graph, ont_ns, defined_classes)

    populate_instances_from_data(graph, ont_ns, defined_classes,
                                 actual_data_properties, actual_object_properties,
                                 data_directory)

    # Pass the property maps to serialize_graph only if needed by a dynamic context builder.
    # Since we are using a hardcoded extensive context, they are not strictly needed by serialize_graph itself
    # for building the context, but passing them doesn't hurt and keeps the signature consistent if we
    # were to switch back or if other parts of serialize_graph might use them.
    serialize_graph(graph, output_directory, output_file_basename, ont_ns,
                    actual_data_properties, actual_object_properties)

    print(f"Processed {len(graph)} triples.")


if __name__ == "__main__":
    main()
