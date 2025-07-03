#!/usr/bin/env python3
"""
RDF Ontology Manager for MovieLens N3 Reasoner
Handles complete RDF graph creation, serialization, and statistics generation.
"""

import os
import json
import logging
from typing import Dict, Tuple
from datetime import datetime

from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD

from movielens_reasoner import MovieLensReasoner

logger = logging.getLogger(__name__)


class RDFOntologyManager:
    """
    Manages RDF graph creation, serialization, and statistics for MovieLens ontology
    """

    def __init__(self, reasoner: MovieLensReasoner):
        self.reasoner = reasoner
        self.graph = Graph()

        # Namespace setup
        self.ns = Namespace("http://example.org/movies#")
        self.graph.bind("", self.ns)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)

        # File paths
        self.ontology_path = os.path.join(reasoner.data_path, "../paste.txt")
        self.output_dir = os.path.join(reasoner.data_path, "ontologies")

    def load_ontology_schema(self):
        """Parse N3 ontology file and add schema to graph"""
        if os.path.exists(self.ontology_path):
            try:
                self.graph.parse(self.ontology_path, format="n3")
                logger.info("Loaded ontology schema from N3 file")
            except Exception as e:
                logger.warning(f"Could not parse N3 ontology: {e}")
                self._add_basic_schema()
        else:
            logger.info("N3 ontology file not found, adding basic schema")
            self._add_basic_schema()

    def _add_basic_schema(self):
        """Add basic ontology schema if N3 file not available"""
        # Ontology declaration
        ontology_uri = URIRef("http://example.org/movies")
        self.graph.add((ontology_uri, RDF.type, OWL.Ontology))
        self.graph.add((ontology_uri, RDFS.label, Literal(
            "Movies Ontology MovieLens v02")))

        # Classes
        classes = ['Movie', 'User', 'UserRating',
                   'Tag', 'Genre', 'Actor', 'Director']
        for cls in classes:
            cls_uri = self.ns[cls]
            self.graph.add((cls_uri, RDF.type, OWL.Class))
            self.graph.add((cls_uri, RDFS.label, Literal(cls)))

        # Data properties
        data_properties = [
            'movieID', 'title', 'releaseYear', 'averageRating', 'ratingCount', 'duration',
            'userID', 'age', 'occupation', 'ratingValue', 'ratingTimestamp',
            'tagName', 'tagRelevance', 'qualityTier', 'recommendationPriority',
            'contentType', 'movieEra', 'trendStatus', 'seasonalType', 'viewingOccasion',
            'ratingBehavior', 'userType', 'audienceSegment', 'genreName'
        ]
        for prop in data_properties:
            prop_uri = self.ns[prop]
            self.graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))

        # Object properties
        object_properties = [
            'belongsToGenre', 'ratedBy', 'ratingBy', 'ratingFor', 'taggedWith',
            'preferredGenre', 'similarTo', 'actorIn', 'directorOf', 'hasActor',
            'frequentCollaborator', 'recommendedFor'
        ]
        for prop in object_properties:
            prop_uri = self.ns[prop]
            self.graph.add((prop_uri, RDF.type, OWL.ObjectProperty))

    def convert_csv_to_rdf(self):
        """Convert all CSV data to RDF triples"""
        logger.info("Converting CSV data to RDF triples...")

        self._convert_movies_to_rdf()
        self._convert_users_to_rdf()
        self._convert_ratings_to_rdf()
        self._convert_tags_to_rdf()
        self._convert_genres_to_rdf()
        self._add_reasoning_results_to_rdf()

        logger.info(f"Converted CSV data to {len(self.graph)} RDF triples")

    def _clean_identifier(self, text: str) -> str:
        """Clean text for use as RDF identifier - Enhanced"""
        import re
        # Remove/replace problematic characters
        cleaned = re.sub(r'[^\w\-_]', '_', str(text))
        # Ensure it doesn't start with a number (XML name rules)
        if cleaned and cleaned[0].isdigit():
            cleaned = f"id_{cleaned}"
        # Remove multiple underscores
        cleaned = re.sub(r'_+', '_', cleaned)
        # Remove trailing underscores
        cleaned = cleaned.strip('_')
        return cleaned or "unknown"

    def _create_safe_uri(self, prefix: str, identifier: str) -> URIRef:
        """Create a safe URI from an identifier"""
        clean_id = self._clean_identifier(identifier)
        return self.ns[f"{prefix}_{clean_id}"]

    def _convert_movies_to_rdf(self):
        """Convert movie entities to RDF - URI-safe version"""
        for movie_id, movie in self.reasoner.movies.items():
            # Create safe URI
            movie_uri = self._create_safe_uri("movie", movie_id)

            self.graph.add((movie_uri, RDF.type, self.ns.Movie))
            # Store original ID as literal for reference
            self.graph.add((movie_uri, self.ns.movieID, Literal(
                str(movie_id), datatype=XSD.string)))
            self.graph.add((movie_uri, self.ns.title, Literal(movie.title)))

            if movie.release_year:
                self.graph.add((movie_uri, self.ns.releaseYear, Literal(
                    movie.release_year, datatype=XSD.integer)))
            if movie.average_rating > 0:
                self.graph.add((movie_uri, self.ns.averageRating, Literal(
                    movie.average_rating, datatype=XSD.float)))
            if movie.rating_count > 0:
                self.graph.add((movie_uri, self.ns.ratingCount, Literal(
                    movie.rating_count, datatype=XSD.integer)))
            if movie.duration:
                self.graph.add((movie_uri, self.ns.duration, Literal(
                    movie.duration, datatype=XSD.integer)))

            # Add reasoning results with explicit datatyping
            if movie.quality_tier:
                self.graph.add((movie_uri, self.ns.qualityTier, Literal(
                    movie.quality_tier, datatype=XSD.string)))
            if movie.recommendation_priority:
                self.graph.add((movie_uri, self.ns.recommendationPriority, Literal(
                    movie.recommendation_priority, datatype=XSD.string)))
            if movie.movie_era:
                self.graph.add((movie_uri, self.ns.movieEra, Literal(
                    movie.movie_era, datatype=XSD.string)))
            if movie.content_type:
                self.graph.add((movie_uri, self.ns.contentType, Literal(
                    movie.content_type, datatype=XSD.string)))
            if movie.trend_status:
                self.graph.add((movie_uri, self.ns.trendStatus, Literal(
                    movie.trend_status, datatype=XSD.string)))
            if movie.seasonal_type:
                self.graph.add((movie_uri, self.ns.seasonalType, Literal(
                    movie.seasonal_type, datatype=XSD.string)))
            if movie.viewing_occasion:
                self.graph.add((movie_uri, self.ns.viewingOccasion, Literal(
                    movie.viewing_occasion, datatype=XSD.string)))

    def _convert_users_to_rdf(self):
        """Convert user entities to RDF - URI-safe version"""
        for user_id, user in self.reasoner.users.items():
            user_uri = self._create_safe_uri("user", user_id)

            self.graph.add((user_uri, RDF.type, self.ns.User))
            self.graph.add((user_uri, self.ns.userID, Literal(
                str(user_id), datatype=XSD.string)))

            if user.age:
                self.graph.add((user_uri, self.ns.age, Literal(
                    user.age, datatype=XSD.integer)))
            if user.occupation:
                self.graph.add((user_uri, self.ns.occupation, Literal(
                    user.occupation, datatype=XSD.string)))
            if user.rating_behavior:
                self.graph.add((user_uri, self.ns.ratingBehavior, Literal(
                    user.rating_behavior, datatype=XSD.string)))
            if user.user_type:
                self.graph.add((user_uri, self.ns.userType, Literal(
                    user.user_type, datatype=XSD.string)))
            if user.audience_segment:
                self.graph.add((user_uri, self.ns.audienceSegment, Literal(
                    user.audience_segment, datatype=XSD.string)))

    def _convert_ratings_to_rdf(self):
        """Convert rating entities to RDF - URI-safe version"""
        for i, rating in enumerate(self.reasoner.ratings):
            rating_uri = self._create_safe_uri("rating", str(i))
            user_uri = self._create_safe_uri("user", rating.user_id)
            movie_uri = self._create_safe_uri("movie", rating.movie_id)

            self.graph.add((rating_uri, RDF.type, self.ns.UserRating))
            self.graph.add((rating_uri, self.ns.ratingValue,
                           Literal(rating.rating, datatype=XSD.float)))
            self.graph.add((rating_uri, self.ns.ratingTimestamp,
                           Literal(rating.timestamp, datatype=XSD.dateTime)))

            # Object property relationships with safe URIs
            self.graph.add((rating_uri, self.ns.ratingBy, user_uri))
            self.graph.add((rating_uri, self.ns.ratingFor, movie_uri))
            self.graph.add((movie_uri, self.ns.ratedBy, rating_uri))

    def _convert_genres_to_rdf(self):
        """Convert genres and genre relationships to RDF - URI-safe version"""
        for genre in self.reasoner.genres:
            if genre != "(no genres listed)":
                genre_uri = self._create_safe_uri("genre", genre)
                self.graph.add((genre_uri, RDF.type, self.ns.Genre))
                self.graph.add((genre_uri, self.ns.genreName,
                               Literal(genre, datatype=XSD.string)))

        # Add movie-genre relationships with consistent URI generation
        for movie_id, movie in self.reasoner.movies.items():
            movie_uri = self._create_safe_uri("movie", movie_id)
            for genre in movie.genres:
                if genre != "(no genres listed)":
                    genre_uri = self._create_safe_uri("genre", genre)
                    self.graph.add(
                        (movie_uri, self.ns.belongsToGenre, genre_uri))

    def _convert_tags_to_rdf(self):
        """Convert tag entities to RDF - URI-safe version"""
        for i, tag in enumerate(self.reasoner.tags):
            # Create safe URIs
            tag_uri = self._create_safe_uri("tag", str(i))
            movie_uri = self._create_safe_uri("movie", tag.movie_id)

            self.graph.add((tag_uri, RDF.type, self.ns.Tag))
            self.graph.add((tag_uri, self.ns.tagName, Literal(
                tag.tag_name, datatype=XSD.string)))
            self.graph.add((tag_uri, self.ns.tagRelevance,
                           Literal(tag.relevance, datatype=XSD.float)))

            # Store original movie ID reference for debugging
            self.graph.add((tag_uri, self.ns.tagForMovieID, Literal(
                str(tag.movie_id), datatype=XSD.string)))

            # Object property relationships with safe URIs
            self.graph.add((movie_uri, self.ns.taggedWith, tag_uri))
            self.graph.add((tag_uri, self.ns.appliedToMovie, movie_uri))

    def _add_reasoning_results_to_rdf(self):
        """Add derived knowledge from reasoning to RDF - URI-safe version"""
        # Add user preferences with consistent URIs
        for user_id, preferred_genres in self.reasoner.user_preferences.items():
            user_uri = self._create_safe_uri("user", user_id)
            for genre in preferred_genres:
                genre_uri = self._create_safe_uri("genre", genre)
                self.graph.add((user_uri, self.ns.preferredGenre, genre_uri))

        # Add movie similarities with consistent URIs
        for movie_id, similar_movies in self.reasoner.movie_similarities.items():
            movie_uri = self._create_safe_uri("movie", movie_id)
            for similar_id in similar_movies:
                similar_uri = self._create_safe_uri("movie", similar_id)
                self.graph.add((movie_uri, self.ns.similarTo, similar_uri))

        # Add recommendations with consistent URIs
        for user_id, recommendations in self.reasoner.recommendations.items():
            user_uri = self._create_safe_uri("user", user_id)
            for movie_id, reason in recommendations:
                movie_uri = self._create_safe_uri("movie", movie_id)
                self.graph.add((movie_uri, self.ns.recommendedFor, user_uri))
                # Add recommendation reason as annotation
                rec_uri = self._create_safe_uri(
                    "recommendation", f"{user_id}_{movie_id}")
                self.graph.add((rec_uri, RDF.type, self.ns.Recommendation))
                self.graph.add((rec_uri, self.ns.recommendationReason,
                               Literal(reason, datatype=XSD.string)))
                self.graph.add((rec_uri, self.ns.recommendationFor, user_uri))
                self.graph.add((rec_uri, self.ns.recommendationOf, movie_uri))

    def save_rdf_formats(self, output_dir: str = None):
        """Save RDF graph in multiple formats"""
        if output_dir is None:
            output_dir = self.output_dir

        os.makedirs(output_dir, exist_ok=True)

        formats = {
            'turtle': '.ttl',
            'n3': '.n3',
            'xml': '.rdf',
            'json-ld': '.jsonld',
            'nt': '.nt'
        }

        saved_files = []
        for fmt, ext in formats.items():
            output_file = os.path.join(output_dir, f"movielens_ontology{ext}")
            try:
                self.graph.serialize(destination=output_file, format=fmt)
                saved_files.append(output_file)
                logger.info(f"Saved {fmt.upper()} format to {output_file}")
            except Exception as e:
                logger.error(f"Failed to save {fmt} format: {e}")

        return saved_files

    def generate_rdf_statistics(self, output_dir: str = None) -> Tuple[Dict, str]:
        """Generate comprehensive RDF statistics"""
        if output_dir is None:
            output_dir = self.output_dir

        stats = {}

        # Basic counts
        stats['total_triples'] = len(self.graph)

        # Count instances by class
        class_counts = {}
        for s, p, o in self.graph.triples((None, RDF.type, None)):
            class_name = str(o).split(
                '#')[-1] if '#' in str(o) else str(o).split('/')[-1]
            if class_name not in ['Class', 'DatatypeProperty', 'ObjectProperty', 'Ontology']:
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
        stats['class_instances'] = class_counts

        # Property usage statistics
        property_counts = {}
        for s, p, o in self.graph:
            prop_name = str(p).split(
                '#')[-1] if '#' in str(p) else str(p).split('/')[-1]
            property_counts[prop_name] = property_counts.get(prop_name, 0) + 1
        stats['property_usage'] = dict(
            sorted(property_counts.items(), key=lambda x: x[1], reverse=True))

        # Unique counts
        subjects = set(s for s, p, o in self.graph)
        predicates = set(p for s, p, o in self.graph)
        objects = set(o for s, p, o in self.graph)

        stats['unique_subjects'] = len(subjects)
        stats['unique_predicates'] = len(predicates)
        stats['unique_objects'] = len(objects)
        stats['unique_entities'] = len(subjects | objects)

        # Generate text report
        report_lines = [
            "=" * 80,
            "MOVIELENS RDF ONTOLOGY STATISTICS",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"Total Triples: {stats['total_triples']:,}",
            f"Unique Subjects: {stats['unique_subjects']:,}",
            f"Unique Predicates: {stats['unique_predicates']:,}",
            f"Unique Objects: {stats['unique_objects']:,}",
            f"Unique Entities: {stats['unique_entities']:,}",
            "",
            "CLASS INSTANCE COUNTS:",
            "-" * 40
        ]

        for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"{class_name:<20}: {count:>8,}")

        report_lines.extend([
            "",
            "TOP 20 PROPERTY USAGE:",
            "-" * 40
        ])

        for prop_name, count in list(stats['property_usage'].items())[:20]:
            report_lines.append(f"{prop_name:<30}: {count:>8,}")

        # Add reasoning-specific statistics
        reasoning_props = ['qualityTier', 'movieEra',
                           'ratingBehavior', 'preferredGenre', 'similarTo']
        reasoning_counts = {prop: property_counts.get(
            prop, 0) for prop in reasoning_props}

        report_lines.extend([
            "",
            "REASONING RESULTS STATISTICS:",
            "-" * 40
        ])

        for prop, count in reasoning_counts.items():
            report_lines.append(f"{prop:<30}: {count:>8,}")

        report_text = "\n".join(report_lines)

        # Save statistics files
        os.makedirs(output_dir, exist_ok=True)

        # Text report
        stats_file = os.path.join(output_dir, "rdf_statistics.txt")
        with open(stats_file, 'w') as f:
            f.write(report_text)

        # JSON statistics
        stats_json_file = os.path.join(output_dir, "rdf_statistics.json")
        with open(stats_json_file, 'w') as f:
            json.dump(stats, f, indent=2, default=str)

        logger.info(
            f"RDF statistics saved to {stats_file} and {stats_json_file}")

        return stats, report_text

    def load_complete_graph(self):
        """Load complete knowledge graph with ontology and data"""
        logger.info("Loading complete RDF knowledge graph...")

        # Load ontology schema
        self.load_ontology_schema()

        # Ensure reasoner has data and reasoning results
        if not self.reasoner.movies:
            self.reasoner.load_data()

        if not any(movie.quality_tier for movie in self.reasoner.movies.values()):
            self.reasoner.apply_reasoning_rules()

        # Convert CSV data to RDF
        self.convert_csv_to_rdf()

        logger.info(
            f"Complete knowledge graph loaded with {len(self.graph)} triples")
        return self.graph

    def export_complete_ontology(self, output_dir: str = None):
        """Export complete ontology in all RDF formats with validation"""
        if output_dir is None:
            output_dir = self.output_dir

        logger.info("Exporting complete RDF ontology...")

        # Diagnose potential issues first
        self.diagnose_uri_issues()

        # Load complete graph
        self.load_complete_graph()

        # Validate consistency
        is_valid = self.validate_rdf_consistency()
        if not is_valid:
            logger.warning(
                "RDF validation found issues - check output carefully")

        # Save in all RDF formats
        saved_files = self.save_rdf_formats(output_dir)

        # Generate and save statistics
        stats, report_text = self.generate_rdf_statistics(output_dir)

        # Create summary
        summary = {
            'export_timestamp': datetime.now().isoformat(),
            'output_directory': output_dir,
            'total_triples': stats['total_triples'],
            'saved_files': saved_files,
            'formats': ['Turtle (.ttl)', 'N3 (.n3)', 'RDF/XML (.rdf)', 'JSON-LD (.jsonld)', 'N-Triples (.nt)'],
            'statistics_files': [
                os.path.join(output_dir, "rdf_statistics.txt"),
                os.path.join(output_dir, "rdf_statistics.json")
            ]
        }

        # Save export summary
        summary_file = os.path.join(output_dir, "export_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"RDF ontology export completed successfully")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Total triples: {stats['total_triples']:,}")

        return summary, stats, report_text

    def diagnose_uri_issues(self):
        """Diagnose potential URI and ID issues"""
        print("=== RDF URI DIAGNOSTICS ===")

        # Check movie ID patterns
        movie_ids = list(self.reasoner.movies.keys())
        print(f"Sample movie IDs: {movie_ids[:10]}")

        # Check for problematic characters
        problematic_ids = []
        for movie_id in movie_ids:
            if not movie_id.replace('_', '').replace('-', '').isalnum():
                problematic_ids.append(movie_id)

        if problematic_ids:
            print(f"Problematic IDs found: {problematic_ids[:5]}")
        else:
            print("All movie IDs are URI-safe")

        # Check cross-references
        rating_movie_ids = set(r.movie_id for r in self.reasoner.ratings)
        movie_ids_set = set(self.reasoner.movies.keys())
        missing_refs = rating_movie_ids - movie_ids_set

        print(
            f"Cross-reference integrity: {len(missing_refs)} missing movie references")

        # Check URI generation
        sample_movie_id = movie_ids[0] if movie_ids else None
        if sample_movie_id:
            sample_uri = self.ns[f"movie_{sample_movie_id}"]
            print(f"Sample URI: {sample_uri}")

    def validate_rdf_consistency(self):
        """Validate RDF graph consistency and URI integrity"""
        print("=== RDF VALIDATION ===")

        # Check for broken references
        all_subjects = set(
            s for s, p, o in self.graph if isinstance(s, URIRef))
        all_objects = set(o for s, p, o in self.graph if isinstance(o, URIRef))
        all_uris = all_subjects | all_objects

        # Check for dangling references
        referenced_but_not_defined = all_objects - all_subjects
        if referenced_but_not_defined:
            print(
                f"WARNING: {len(referenced_but_not_defined)} dangling URI references")
            print(f"Sample: {list(referenced_but_not_defined)[:3]}")

        # Check URI patterns
        movie_uris = [uri for uri in all_uris if 'movie_' in str(uri)]
        user_uris = [uri for uri in all_uris if 'user_' in str(uri)]

        print(f"Movie URIs: {len(movie_uris)}")
        print(f"User URIs: {len(user_uris)}")
        print(f"Total valid URIs: {len(all_uris)}")

        return len(referenced_but_not_defined) == 0


def main():
    """Main function to demonstrate RDF ontology export"""
    print("MovieLens RDF Ontology Manager")
    print("=" * 50)

    # Initialize reasoner
    print("1. Initializing MovieLens reasoner...")
    reasoner = MovieLensReasoner()

    # Load data and apply reasoning
    print("2. Loading data and applying reasoning...")
    reasoner.load_data()
    reasoner.apply_reasoning_rules()

    # Initialize RDF manager
    print("3. Initializing RDF ontology manager...")
    rdf_manager = RDFOntologyManager(reasoner)

    # Export complete ontology
    print("4. Exporting complete RDF ontology...")
    summary, stats, report = rdf_manager.export_complete_ontology()

    # Display results
    print("\n" + "=" * 50)
    print("EXPORT SUMMARY")
    print("=" * 50)
    print(f"Output directory: {summary['output_directory']}")
    print(f"Total triples: {summary['total_triples']:,}")
    print(f"Formats saved: {len(summary['formats'])}")

    print("\nClass distribution:")
    for class_name, count in list(stats['class_instances'].items())[:8]:
        print(f"  {class_name}: {count:,}")

    print(f"\nFiles saved:")
    for file_path in summary['saved_files']:
        print(f"  {os.path.basename(file_path)}")

    print(f"\nStatistics reports:")
    for file_path in summary['statistics_files']:
        print(f"  {os.path.basename(file_path)}")

    print("\n" + "=" * 50)
    print("RDF ontology export completed successfully!")
    print("=" * 50)

    return rdf_manager, summary, stats


if __name__ == "__main__":
    rdf_manager, summary, stats = main()
