"""
RDF Ontology Manager for Music Industry Data
Converts reasoning results to RDF graphs and exports in multiple formats.
Handles URI generation, datatype conversion, and comprehensive RDF validation.
"""

import json
import logging
import re
from datetime import datetime, date
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from pathlib import Path
from collections import defaultdict, Counter

try:
    from rdflib import Graph, Namespace, URIRef, Literal, BNode
    from rdflib.namespace import RDF, RDFS, OWL, XSD
    RDFLIB_AVAILABLE = True
except ImportError:
    print("Warning: rdflib not available. Install with: pip install rdflib")
    RDFLIB_AVAILABLE = False

# Import the core reasoner
from music_reasoner import MusicReasonerEngine, normalize_id

logger = logging.getLogger(__name__)


class RDFOntologyManager:
    """
    Manages RDF representation of music industry ontology data.
    Converts entity data and reasoning results to RDF graphs,
    handles URI generation, and exports to multiple RDF formats.
    """

    def __init__(self, reasoner: MusicReasonerEngine):
        """Initialize RDF manager with reasoning engine instance."""
        if not RDFLIB_AVAILABLE:
            raise ImportError(
                "rdflib is required for RDF operations. Install with: pip install rdflib")

        self.reasoner = reasoner
        self.graph = Graph()

        # Define namespaces
        self.ns = Namespace("http://example.org/music#")
        self.music_ns = Namespace("http://example.org/music/")

        # Bind namespaces to graph
        self.graph.bind("music", self.ns)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("xsd", XSD)

        # RDF statistics
        self.rdf_stats = {
            'total_triples': 0,
            'entity_counts': defaultdict(int),
            'property_usage': defaultdict(int),
            'unique_subjects': set(),
            'unique_predicates': set(),
            'unique_objects': set()
        }

        # URI cache for consistency
        self.uri_cache = {}

        logger.info("RDF Ontology Manager initialized")

    def convert_to_rdf(self) -> None:
        """
        Convert all entities and reasoning results to RDF triples.
        This is the main method that orchestrates the entire conversion process.
        """
        logger.info("Starting RDF conversion...")

        try:
            # Clear existing graph
            self.graph = Graph()
            self._bind_namespaces()

            # Add ontology metadata
            self._add_ontology_metadata()

            # Add class definitions
            self._add_class_definitions()

            # Add property definitions
            self._add_property_definitions()

            # Convert entities
            self._convert_songs()
            self._convert_artists()
            self._convert_albums()
            self._convert_record_labels()
            self._convert_genres()
            self._convert_awards()

            # Add reasoning results
            self._add_reasoning_results()

            # Calculate statistics
            self._calculate_rdf_statistics()

            logger.info(
                f"RDF conversion completed. Generated {len(self.graph)} triples.")

        except Exception as e:
            logger.error(f"Error during RDF conversion: {e}")
            raise

    def _bind_namespaces(self) -> None:
        """Bind all necessary namespaces to the graph."""
        self.graph.bind("music", self.ns)
        self.graph.bind("musicdata", self.music_ns)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("xsd", XSD)

    def _add_ontology_metadata(self) -> None:
        """Add ontology metadata triples."""
        ontology_uri = URIRef("http://example.org/music")

        self.graph.add((ontology_uri, RDF.type, OWL.Ontology))
        self.graph.add((ontology_uri, RDFS.label, Literal(
            "Music Industry Ontology", datatype=XSD.string)))
        self.graph.add((ontology_uri, RDFS.comment, Literal(
            "An ontology for representing songs, artists, albums, record labels, genres, and awards in the music industry",
            datatype=XSD.string
        )))
        self.graph.add((ontology_uri, OWL.versionInfo,
                       Literal("1.0", datatype=XSD.string)))
        self.graph.add((ontology_uri, URIRef("http://purl.org/dc/terms/created"),
                       Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))

    def _add_class_definitions(self) -> None:
        """Add OWL class definitions to the graph."""
        classes = {
            'Song': "A musical composition",
            'Artist': "A person or group who creates or performs music",
            'Album': "A collection of songs released together",
            'RecordLabel': "A company that manages the production, distribution, and promotion of music",
            'Genre': "A category or style of music",
            'Award': "A recognition given for musical achievement",
            'Single': "A song released as a standalone track or as a primary track from an album",
            'ExtendedPlay': "A musical recording that contains more music than a single but is shorter than an album",
            'CollaborativeSong': "A song performed by multiple artists",
            'SuccessfulLabel': "A record label with multiple award-winning artists",
            'EstablishedArtist': "An artist with multiple albums and awards"
        }

        for class_name, description in classes.items():
            class_uri = self.ns[class_name]
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.label, Literal(
                class_name, datatype=XSD.string)))
            self.graph.add((class_uri, RDFS.comment, Literal(
                description, datatype=XSD.string)))

        # Add subclass relationships
        self.graph.add((self.ns.Single, RDFS.subClassOf, self.ns.Song))
        self.graph.add((self.ns.ExtendedPlay, RDFS.subClassOf, self.ns.Album))
        self.graph.add((self.ns.CollaborativeSong,
                       RDFS.subClassOf, self.ns.Song))
        self.graph.add(
            (self.ns.SuccessfulLabel, RDFS.subClassOf, self.ns.RecordLabel))
        self.graph.add((self.ns.EstablishedArtist,
                       RDFS.subClassOf, self.ns.Artist))

    def _add_property_definitions(self) -> None:
        """Add property definitions to the graph."""
        # Data properties
        data_properties = {
            'title': (XSD.string, "The title of a song"),
            'duration': (XSD.int, "The duration of a song in seconds"),
            'releaseDate': (XSD.date, "The date when a song was released"),
            'name': (XSD.string, "The name of an artist"),
            'birthDate': (XSD.date, "The birth date of an artist"),
            'nationality': (XSD.string, "The nationality of an artist"),
            'albumTitle': (XSD.string, "The title of an album"),
            'releaseYear': (XSD.int, "The year when an album was released"),
            'labelName': (XSD.string, "The name of a record label"),
            'location': (XSD.string, "The location of a record label"),
            'genreName': (XSD.string, "The name of a genre"),
            'description': (XSD.string, "A description of a genre"),
            'awardName': (XSD.string, "The name of an award"),
            'year': (XSD.int, "The year an award was given"),
            'awardingBody': (XSD.string, "The organization that gives the award"),
            'popularityScore': (XSD.int, "Calculated popularity metric"),
            'collaborationStrength': (XSD.int, "Numeric measure of collaboration strength"),
            'labelSuccessRating': (XSD.int, "Success metric for record labels")
        }

        for prop_name, (datatype, comment) in data_properties.items():
            prop_uri = self.ns[prop_name]
            self.graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.graph.add((prop_uri, RDFS.label, Literal(
                prop_name, datatype=XSD.string)))
            self.graph.add(
                (prop_uri, RDFS.comment, Literal(comment, datatype=XSD.string)))
            self.graph.add((prop_uri, RDFS.range, datatype))

        # Object properties
        object_properties = {
            'performedBy': "Relates a song to the artist(s) who perform it",
            'featuredOn': "Relates a song to the album(s) it appears on",
            'hasGenre': "Relates a song or album to its genre(s)",
            'hasWonAward': "Relates a song or artist to awards they have won",
            'signedTo': "Relates an artist to the record label they are signed to",
            'releasedByArtist': "Relates an album to the artist(s) who released it",
            'releasedByLabel': "Relates an album to the record label that released it",
            'collaboratesWith': "Relates artists who have performed songs together",
            'influencedBy': "Relates artists through genre and collaboration networks",
            'isContributor': "Relates an entity to albums they contributed to",
            'contemporaryOf': "Relates artists who were active in the same time period"
        }

        for prop_name, comment in object_properties.items():
            prop_uri = self.ns[prop_name]
            self.graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
            self.graph.add((prop_uri, RDFS.label, Literal(
                prop_name, datatype=XSD.string)))
            self.graph.add(
                (prop_uri, RDFS.comment, Literal(comment, datatype=XSD.string)))

        # Add symmetric property
        self.graph.add((self.ns.collaboratesWith,
                       RDF.type, OWL.SymmetricProperty))

        # Add transitive property
        self.graph.add(
            (self.ns.influencedBy, RDF.type, OWL.TransitiveProperty))

    def _convert_songs(self) -> None:
        """Convert song entities to RDF triples."""
        logger.info(f"Converting {len(self.reasoner.songs)} songs to RDF...")

        for song in self.reasoner.songs.values():
            song_uri = self._create_safe_uri("song", song.id)

            # Basic class assertion
            if song.is_collaborative:
                self.graph.add((song_uri, RDF.type, self.ns.CollaborativeSong))
            else:
                self.graph.add((song_uri, RDF.type, self.ns.Song))

            # Data properties
            if song.title:
                self.graph.add((song_uri, self.ns.title, Literal(
                    song.title, datatype=XSD.string)))

            if song.duration > 0:
                self.graph.add((song_uri, self.ns.duration,
                               Literal(song.duration, datatype=XSD.int)))

            if song.release_date:
                self.graph.add((song_uri, self.ns.releaseDate, Literal(
                    song.release_date.isoformat(), datatype=XSD.date)))

            # Object properties - artists
            for artist_id in song.artist_ids:
                if artist_id in self.reasoner.artists:
                    artist_uri = self._create_safe_uri("artist", artist_id)
                    self.graph.add((song_uri, self.ns.performedBy, artist_uri))

            # Object properties - albums
            for album_id in song.album_ids:
                if album_id in self.reasoner.albums:
                    album_uri = self._create_safe_uri("album", album_id)
                    self.graph.add((song_uri, self.ns.featuredOn, album_uri))

            # Object properties - genres
            for genre_id in song.genre_ids:
                if genre_id in self.reasoner.genres:
                    genre_uri = self._create_safe_uri("genre", genre_id)
                    self.graph.add((song_uri, self.ns.hasGenre, genre_uri))

            # Object properties - awards
            for award_id in song.award_ids:
                if award_id in self.reasoner.awards:
                    award_uri = self._create_safe_uri("award", award_id)
                    self.graph.add((song_uri, self.ns.hasWonAward, award_uri))

            self.rdf_stats['entity_counts']['songs'] += 1

    def _convert_artists(self) -> None:
        """Convert artist entities to RDF triples."""
        logger.info(
            f"Converting {len(self.reasoner.artists)} artists to RDF...")

        for artist in self.reasoner.artists.values():
            artist_uri = self._create_safe_uri("artist", artist.id)

            # Basic class assertion
            if artist.is_established:
                self.graph.add(
                    (artist_uri, RDF.type, self.ns.EstablishedArtist))
            else:
                self.graph.add((artist_uri, RDF.type, self.ns.Artist))

            # Data properties
            if artist.name:
                self.graph.add((artist_uri, self.ns.name, Literal(
                    artist.name, datatype=XSD.string)))

            if artist.birth_date:
                self.graph.add((artist_uri, self.ns.birthDate, Literal(
                    artist.birth_date.isoformat(), datatype=XSD.date)))

            if artist.nationality:
                self.graph.add((artist_uri, self.ns.nationality, Literal(
                    artist.nationality, datatype=XSD.string)))

            if artist.popularity_score > 0:
                self.graph.add((artist_uri, self.ns.popularityScore, Literal(
                    artist.popularity_score, datatype=XSD.int)))

            # Object properties - label
            if artist.label_id and artist.label_id in self.reasoner.record_labels:
                label_uri = self._create_safe_uri("label", artist.label_id)
                self.graph.add((artist_uri, self.ns.signedTo, label_uri))

            # Object properties - collaborations
            for partner_id in artist.collaboration_partners:
                if partner_id in self.reasoner.artists:
                    partner_uri = self._create_safe_uri("artist", partner_id)
                    self.graph.add(
                        (artist_uri, self.ns.collaboratesWith, partner_uri))

                    # Add collaboration strength if available
                    if partner_id in artist.collaboration_strength:
                        strength = artist.collaboration_strength[partner_id]
                        # Create a blank node for the qualified relationship
                        collab_node = BNode()
                        self.graph.add(
                            (artist_uri, self.ns.hasCollaborationStrength, collab_node))
                        self.graph.add(
                            (collab_node, self.ns.withArtist, partner_uri))
                        self.graph.add((collab_node, self.ns.collaborationStrength, Literal(
                            strength, datatype=XSD.int)))

            # Object properties - influences
            for influenced_id in artist.influenced_by:
                if influenced_id in self.reasoner.artists:
                    influenced_uri = self._create_safe_uri(
                        "artist", influenced_id)
                    self.graph.add(
                        (artist_uri, self.ns.influencedBy, influenced_uri))

            # Object properties - contemporaries
            for contemporary_id in artist.contemporary_artists:
                if contemporary_id in self.reasoner.artists:
                    contemporary_uri = self._create_safe_uri(
                        "artist", contemporary_id)
                    self.graph.add(
                        (artist_uri, self.ns.contemporaryOf, contemporary_uri))

            self.rdf_stats['entity_counts']['artists'] += 1

    def _convert_albums(self) -> None:
        """Convert album entities to RDF triples."""
        logger.info(f"Converting {len(self.reasoner.albums)} albums to RDF...")

        for album in self.reasoner.albums.values():
            album_uri = self._create_safe_uri("album", album.id)

            # Basic class assertion
            self.graph.add((album_uri, RDF.type, self.ns.Album))

            # Data properties
            if album.album_title:
                self.graph.add((album_uri, self.ns.albumTitle, Literal(
                    album.album_title, datatype=XSD.string)))

            if album.release_year > 0:
                self.graph.add((album_uri, self.ns.releaseYear, Literal(
                    album.release_year, datatype=XSD.int)))

            if album.total_duration > 0:
                self.graph.add((album_uri, self.ns.totalDuration, Literal(
                    album.total_duration, datatype=XSD.int)))

            # Object properties - artists
            for artist_id in album.artist_ids:
                if artist_id in self.reasoner.artists:
                    artist_uri = self._create_safe_uri("artist", artist_id)
                    self.graph.add(
                        (album_uri, self.ns.releasedByArtist, artist_uri))

            # Object properties - label
            if album.label_id and album.label_id in self.reasoner.record_labels:
                label_uri = self._create_safe_uri("label", album.label_id)
                self.graph.add((album_uri, self.ns.releasedByLabel, label_uri))

            # Object properties - genres (including inherited)
            for genre_id in album.genre_ids:
                if genre_id in self.reasoner.genres:
                    genre_uri = self._create_safe_uri("genre", genre_id)
                    self.graph.add((album_uri, self.ns.hasGenre, genre_uri))

                    # Mark inherited genres
                    if genre_id in album.inherited_genres:
                        self.graph.add(
                            (album_uri, self.ns.hasInheritedGenre, genre_uri))

            # Object properties - songs
            for song_id in album.song_ids:
                if song_id in self.reasoner.songs:
                    song_uri = self._create_safe_uri("song", song_id)
                    self.graph.add((album_uri, self.ns.features, song_uri))

            # Object properties - contributors
            for contributor_id in album.contributors:
                if contributor_id in self.reasoner.artists:
                    contributor_uri = self._create_safe_uri(
                        "artist", contributor_id)
                    self.graph.add(
                        (contributor_uri, self.ns.isContributor, album_uri))
                elif contributor_id in self.reasoner.record_labels:
                    contributor_uri = self._create_safe_uri(
                        "label", contributor_id)
                    self.graph.add(
                        (contributor_uri, self.ns.isContributor, album_uri))

            self.rdf_stats['entity_counts']['albums'] += 1

    def _convert_record_labels(self) -> None:
        """Convert record label entities to RDF triples."""
        logger.info(
            f"Converting {len(self.reasoner.record_labels)} record labels to RDF...")

        for label in self.reasoner.record_labels.values():
            label_uri = self._create_safe_uri("label", label.id)

            # Basic class assertion
            if label.is_successful:
                self.graph.add((label_uri, RDF.type, self.ns.SuccessfulLabel))
            else:
                self.graph.add((label_uri, RDF.type, self.ns.RecordLabel))

            # Data properties
            if label.label_name:
                self.graph.add((label_uri, self.ns.labelName, Literal(
                    label.label_name, datatype=XSD.string)))

            if label.location:
                self.graph.add((label_uri, self.ns.location, Literal(
                    label.location, datatype=XSD.string)))

            if label.success_rating > 0:
                self.graph.add((label_uri, self.ns.labelSuccessRating, Literal(
                    label.success_rating, datatype=XSD.int)))

            # Object properties - signed artists
            for artist_id in label.signed_artists:
                if artist_id in self.reasoner.artists:
                    artist_uri = self._create_safe_uri("artist", artist_id)
                    self.graph.add(
                        (label_uri, self.ns.hasSignedArtist, artist_uri))

            self.rdf_stats['entity_counts']['record_labels'] += 1

    def _convert_genres(self) -> None:
        """Convert genre entities to RDF triples."""
        logger.info(f"Converting {len(self.reasoner.genres)} genres to RDF...")

        for genre in self.reasoner.genres.values():
            genre_uri = self._create_safe_uri("genre", genre.id)

            # Basic class assertion
            self.graph.add((genre_uri, RDF.type, self.ns.Genre))

            # Data properties
            if genre.genre_name:
                self.graph.add((genre_uri, self.ns.genreName, Literal(
                    genre.genre_name, datatype=XSD.string)))

            if genre.description:
                self.graph.add((genre_uri, self.ns.description, Literal(
                    genre.description, datatype=XSD.string)))

            # Object properties - related genres
            for related_id in genre.related_genres:
                if related_id in self.reasoner.genres:
                    related_uri = self._create_safe_uri("genre", related_id)
                    self.graph.add((genre_uri, RDFS.seeAlso, related_uri))

            self.rdf_stats['entity_counts']['genres'] += 1

    def _convert_awards(self) -> None:
        """Convert award entities to RDF triples."""
        logger.info(f"Converting {len(self.reasoner.awards)} awards to RDF...")

        for award in self.reasoner.awards.values():
            award_uri = self._create_safe_uri("award", award.id)

            # Basic class assertion
            self.graph.add((award_uri, RDF.type, self.ns.Award))

            # Data properties
            if award.award_name:
                self.graph.add((award_uri, self.ns.awardName, Literal(
                    award.award_name, datatype=XSD.string)))

            if award.year > 0:
                self.graph.add(
                    (award_uri, self.ns.year, Literal(award.year, datatype=XSD.int)))

            if award.awarding_body:
                self.graph.add((award_uri, self.ns.awardingBody, Literal(
                    award.awarding_body, datatype=XSD.string)))

            # Object properties - awarded to artists
            for artist_id in award.artist_ids:
                if artist_id in self.reasoner.artists:
                    artist_uri = self._create_safe_uri("artist", artist_id)
                    self.graph.add((award_uri, self.ns.awardWonBy, artist_uri))

            # Object properties - awarded to songs
            for song_id in award.song_ids:
                if song_id in self.reasoner.songs:
                    song_uri = self._create_safe_uri("song", song_id)
                    self.graph.add((award_uri, self.ns.awardWonBy, song_uri))

            self.rdf_stats['entity_counts']['awards'] += 1

    def _add_reasoning_results(self) -> None:
        """Add additional triples representing reasoning results."""
        logger.info("Adding reasoning results to RDF graph...")

        # Mark collaborative songs
        for song_id in self.reasoner.collaborative_songs:
            if song_id in self.reasoner.songs:
                song_uri = self._create_safe_uri("song", song_id)
                self.graph.add((song_uri, RDF.type, self.ns.CollaborativeSong))

        # Mark successful labels
        for label_id in self.reasoner.successful_labels:
            if label_id in self.reasoner.record_labels:
                label_uri = self._create_safe_uri("label", label_id)
                self.graph.add((label_uri, RDF.type, self.ns.SuccessfulLabel))

        # Mark established artists
        for artist_id in self.reasoner.established_artists:
            if artist_id in self.reasoner.artists:
                artist_uri = self._create_safe_uri("artist", artist_id)
                self.graph.add(
                    (artist_uri, RDF.type, self.ns.EstablishedArtist))

    def _create_safe_uri(self, prefix: str, identifier: str) -> URIRef:
        """
        Create a safe URI reference with consistent generation.
        Handles special characters and ensures web-safe URIs.
        """
        cache_key = f"{prefix}_{identifier}"
        if cache_key in self.uri_cache:
            return self.uri_cache[cache_key]

        clean_id = self._clean_identifier(identifier)
        uri = self.music_ns[f"{prefix}_{clean_id}"]
        self.uri_cache[cache_key] = uri
        return uri

    def _clean_identifier(self, text: str) -> str:
        """
        Clean identifier text for safe URI generation.
        Removes special characters and ensures valid URI format.
        """
        # Convert to string and handle None
        if text is None:
            text = "unknown"
        text = str(text)

        # Replace problematic characters with underscores
        cleaned = re.sub(r'[^\w\-_]', '_', text)

        # Ensure doesn't start with a number
        if cleaned and cleaned[0].isdigit():
            cleaned = f"id_{cleaned}"

        # Remove multiple underscores and trailing underscores
        cleaned = re.sub(r'_+', '_', cleaned).strip('_')

        # Ensure not empty
        if not cleaned:
            cleaned = "unknown"

        return cleaned

    def _calculate_rdf_statistics(self) -> None:
        """Calculate comprehensive RDF statistics."""
        self.rdf_stats['total_triples'] = len(self.graph)

        # Count unique subjects, predicates, objects
        for s, p, o in self.graph:
            self.rdf_stats['unique_subjects'].add(s)
            self.rdf_stats['unique_predicates'].add(p)
            self.rdf_stats['unique_objects'].add(o)
            self.rdf_stats['property_usage'][str(p)] += 1

        # Convert sets to counts
        self.rdf_stats['unique_subjects'] = len(
            self.rdf_stats['unique_subjects'])
        self.rdf_stats['unique_predicates'] = len(
            self.rdf_stats['unique_predicates'])
        self.rdf_stats['unique_objects'] = len(
            self.rdf_stats['unique_objects'])

    def export_multiple_formats(self, output_dir: str) -> Dict[str, str]:
        """
        Export RDF graph in multiple serialization formats.
        Returns dictionary mapping format names to file paths.
        """
        if not self.graph:
            raise ValueError("Graph is empty. Run convert_to_rdf() first.")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        formats = {
            'turtle': ('ttl', 'turtle'),
            'n3': ('n3', 'n3'),
            'rdf_xml': ('rdf', 'xml'),
            'json_ld': ('jsonld', 'json-ld'),
            'n_triples': ('nt', 'nt')
        }

        exported_files = {}

        for format_name, (extension, rdflib_format) in formats.items():
            try:
                file_path = output_path / f"music_ontology.{extension}"
                logger.info(f"Exporting {format_name} format to {file_path}")

                # Serialize the graph
                serialized = self.graph.serialize(format=rdflib_format)

                # Write to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    if isinstance(serialized, bytes):
                        f.write(serialized.decode('utf-8'))
                    else:
                        f.write(serialized)

                exported_files[format_name] = str(file_path)
                logger.info(f"Successfully exported {format_name} format")

            except Exception as e:
                logger.error(f"Failed to export {format_name} format: {e}")
                exported_files[format_name] = f"Error: {e}"

        return exported_files

    def validate_rdf_graph(self) -> Dict[str, Any]:
        """
        Perform comprehensive validation of the RDF graph.
        Returns validation results and quality metrics.
        """
        logger.info("Validating RDF graph...")

        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'statistics': self.rdf_stats.copy(),
            'quality_metrics': {}
        }

        try:
            # Check for basic graph integrity
            if len(self.graph) == 0:
                validation_results['errors'].append("Graph is empty")
                validation_results['is_valid'] = False
                return validation_results

            # Validate URI patterns
            invalid_uris = []
            for s, p, o in self.graph:
                for uri in [s, p, o]:
                    if isinstance(uri, URIRef):
                        uri_str = str(uri)
                        if not self._is_valid_uri(uri_str):
                            invalid_uris.append(uri_str)

            if invalid_uris:
                validation_results['warnings'].append(
                    f"Found {len(invalid_uris)} potentially invalid URIs")

            # Check for dangling references
            subjects = set()
            objects = set()
            for s, p, o in self.graph:
                if isinstance(s, URIRef):
                    subjects.add(s)
                if isinstance(o, URIRef):
                    objects.add(o)

            dangling_objects = objects - subjects
            if dangling_objects:
                validation_results['warnings'].append(
                    f"Found {len(dangling_objects)} dangling object references")

            # Calculate quality metrics
            validation_results['quality_metrics'] = {
                'uri_consistency_score': 1.0 - (len(invalid_uris) / max(1, len(self.graph))),
                'reference_integrity_score': 1.0 - (len(dangling_objects) / max(1, len(objects))),
                'graph_density': len(self.graph) / max(1, len(subjects)),
                'entity_coverage': {
                    'songs_coverage': len([s for s in subjects if 'song_' in str(s)]) / max(1, len(self.reasoner.songs)),
                    'artists_coverage': len([s for s in subjects if 'artist_' in str(s)]) / max(1, len(self.reasoner.artists)),
                    'albums_coverage': len([s for s in subjects if 'album_' in str(s)]) / max(1, len(self.reasoner.albums))
                }
            }

            logger.info("RDF graph validation completed")

        except Exception as e:
            validation_results['errors'].append(f"Validation error: {e}")
            validation_results['is_valid'] = False
            logger.error(f"RDF validation failed: {e}")

        return validation_results

    def _is_valid_uri(self, uri_str: str) -> bool:
        """Check if URI string is valid according to basic URI syntax."""
        try:
            # Basic URI validation
            if not uri_str.startswith(('http://', 'https://', 'urn:')):
                return False

            # Check for invalid characters
            invalid_chars = [' ', '\t', '\n', '\r']
            for char in invalid_chars:
                if char in uri_str:
                    return False

            return True
        except Exception:
            return False

    def generate_rdf_statistics_report(self, output_path: str) -> None:
        """Generate detailed RDF statistics report in JSON format."""
        logger.info(f"Generating RDF statistics report at {output_path}")

        # Prepare statistics with serializable data
        stats_report = {
            'metadata': {
                'report_type': 'RDF Statistics Report',
                'generated_at': datetime.now().isoformat(),
                'graph_size': len(self.graph)
            },
            'basic_statistics': {
                'total_triples': self.rdf_stats['total_triples'],
                'unique_subjects': self.rdf_stats['unique_subjects'],
                'unique_predicates': self.rdf_stats['unique_predicates'],
                'unique_objects': self.rdf_stats['unique_objects']
            },
            'entity_distribution': dict(self.rdf_stats['entity_counts']),
            'property_usage': dict(sorted(self.rdf_stats['property_usage'].items(),
                                          key=lambda x: x[1], reverse=True)),
            'validation_results': self.validate_rdf_graph()
        }

        # Add namespace analysis
        namespace_usage = defaultdict(int)
        for s, p, o in self.graph:
            for uri in [s, p, o]:
                if isinstance(uri, URIRef):
                    namespace = self._extract_namespace(str(uri))
                    if namespace:
                        namespace_usage[namespace] += 1

        stats_report['namespace_usage'] = dict(namespace_usage)

        # Save report
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats_report, f, indent=2,
                      default=str, ensure_ascii=False)

        logger.info(f"RDF statistics report saved to {output_path}")

    def _extract_namespace(self, uri_str: str) -> Optional[str]:
        """Extract namespace from URI string."""
        try:
            if '#' in uri_str:
                return uri_str.split('#')[0] + '#'
            elif '/' in uri_str:
                parts = uri_str.split('/')
                if len(parts) > 3:
                    return '/'.join(parts[:-1]) + '/'
            return None
        except Exception:
            return None

    def get_sparql_endpoint_data(self) -> Dict[str, Any]:
        """
        Prepare data for SPARQL querying.
        Returns graph and useful example queries.
        """
        return {
            'graph': self.graph,
            'total_triples': len(self.graph),
            'example_queries': {
                'all_collaborative_songs': """
                    PREFIX music: <http://example.org/music#>
                    SELECT ?song ?title WHERE {
                        ?song a music:CollaborativeSong ;
                              music:title ?title .
                    }
                """,
                'established_artists_with_labels': """
                    PREFIX music: <http://example.org/music#>
                    SELECT ?artist ?name ?label WHERE {
                        ?artist a music:EstablishedArtist ;
                                music:name ?name ;
                                music:signedTo ?labelUri .
                        ?labelUri music:labelName ?label .
                    }
                """,
                'genre_popularity': """
                    PREFIX music: <http://example.org/music#>
                    SELECT ?genre ?genreName (COUNT(?song) AS ?songCount) WHERE {
                        ?song music:hasGenre ?genre .
                        ?genre music:genreName ?genreName .
                    }
                    GROUP BY ?genre ?genreName
                    ORDER BY DESC(?songCount)
                """,
                'collaboration_networks': """
                    PREFIX music: <http://example.org/music#>
                    SELECT ?artist1 ?name1 ?artist2 ?name2 WHERE {
                        ?artist1 music:collaboratesWith ?artist2 ;
                                 music:name ?name1 .
                        ?artist2 music:name ?name2 .
                        FILTER(?artist1 != ?artist2)
                    }
                """
            }
        }


class RDFOntologyUsage:
    """
    High-level interface for using the RDF Ontology Manager.
    Provides simple methods for converting data to RDF and exporting in various formats.
    """

    def __init__(self, reasoner: MusicReasonerEngine):
        """Initialize RDF usage interface."""
        self.reasoner = reasoner
        self.rdf_manager = RDFOntologyManager(reasoner)

    def create_complete_rdf_export(self, output_dir: str = "./data/rdf_output") -> Dict[str, Any]:
        """
        Create complete RDF export with all formats and reports.
        This is the main method for end-users.
        """
        logger.info("Creating complete RDF export...")

        try:
            # Convert to RDF
            self.rdf_manager.convert_to_rdf()

            # Export in all formats
            exported_files = self.rdf_manager.export_multiple_formats(
                output_dir)

            # Generate statistics report
            stats_path = Path(output_dir) / "rdf_statistics.json"
            self.rdf_manager.generate_rdf_statistics_report(str(stats_path))

            # Validate graph
            validation_results = self.rdf_manager.validate_rdf_graph()

            # Get SPARQL data
            sparql_data = self.rdf_manager.get_sparql_endpoint_data()

            return {
                'status': 'success',
                'exported_files': exported_files,
                'statistics_report': str(stats_path),
                'validation_results': validation_results,
                'graph_size': len(self.rdf_manager.graph),
                'sparql_queries': sparql_data['example_queries'],
                'total_triples': sparql_data['total_triples']
            }

        except Exception as e:
            logger.error(f"RDF export failed: {e}")
            return {
                'status': 'error',
                'error_message': str(e)
            }

    def quick_turtle_export(self, output_path: str) -> bool:
        """Quick export to Turtle format only."""
        try:
            self.rdf_manager.convert_to_rdf()
            serialized = self.rdf_manager.graph.serialize(format='turtle')

            with open(output_path, 'w', encoding='utf-8') as f:
                if isinstance(serialized, bytes):
                    f.write(serialized.decode('utf-8'))
                else:
                    f.write(serialized)

            logger.info(f"Quick Turtle export saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Quick Turtle export failed: {e}")
            return False


def main():
    """Example usage of the RDF Ontology Manager."""
    # This would typically be called after running the reasoner
    from music_reasoner import MusicReasonerEngine

    # Initialize and load data
    reasoner = MusicReasonerEngine()
    try:
        reasoner.load_csv_data("./data")
        reasoner.apply_reasoning_rules()
    except Exception as e:
        logger.error(f"Failed to load data or apply reasoning: {e}")
        return

    # Create RDF export
    rdf_usage = RDFOntologyUsage(reasoner)
    result = rdf_usage.create_complete_rdf_export("./rdf_output")

    if result['status'] == 'success':
        print("RDF export completed successfully!")
        print(f"Generated {result['total_triples']} triples")
        print(f"Exported files: {list(result['exported_files'].keys())}")
        print(f"Statistics report: {result['statistics_report']}")

        if result['validation_results']['is_valid']:
            print("RDF graph validation: PASSED")
        else:
            print("RDF graph validation: FAILED")
            for error in result['validation_results']['errors']:
                print(f"  Error: {error}")
    else:
        print(f"RDF export failed: {result['error_message']}")


if __name__ == "__main__":
    main()
