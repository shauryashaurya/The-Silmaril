#!/usr/bin/env python3
"""
MovieLens N3 Ontology Reasoner
Implements all 24 reasoning rules from the MovieLens ontology for intelligent movie recommendation and analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
import os
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Movie:
    """Movie entity with computed properties"""
    movie_id: str
    title: str
    genres: List[str]
    release_year: int = None
    average_rating: float = 0.0
    rating_count: int = 0
    # Derived properties from reasoning
    quality_tier: str = None
    recommendation_priority: str = None
    content_type: str = None
    movie_era: str = None
    trend_status: str = None
    seasonal_type: str = None
    viewing_occasion: str = None
    duration: int = None  # Would need additional data source


@dataclass
class User:
    """User entity with behavioral analysis"""
    user_id: str
    age: int = None
    occupation: str = None
    # Derived properties
    rating_behavior: str = None
    user_type: str = None
    preferred_genres: List[str] = None
    audience_segment: str = None


@dataclass
class UserRating:
    """Individual rating with metadata"""
    user_id: str
    movie_id: str
    rating: float
    timestamp: datetime


@dataclass
class Tag:
    """Movie tag with relevance"""
    movie_id: str
    tag_name: str
    relevance: float = 1.0


class MovieLensReasoner:
    """
    N3 Ontology Reasoner for MovieLens data implementing all 24 reasoning rules
    """

    def __init__(self, data_path: str = "./data/ml-latest-small"):
        self.data_path = data_path
        self.movies: Dict[str, Movie] = {}
        self.users: Dict[str, User] = {}
        self.ratings: List[UserRating] = []
        self.tags: List[Tag] = []
        self.genres: Set[str] = set()

        # Derived knowledge from reasoning
        self.genre_stats: Dict[str, Dict] = {}
        self.user_preferences: Dict[str, List[str]] = {}
        self.movie_similarities: Dict[str, List[str]] = {}
        self.recommendations: Dict[str, List[Tuple[str, str]]] = {}

        self.current_year = datetime.now().year

    # def load_data(self):
    #     """Load MovieLens CSV data"""
    #     logger.info("Loading MovieLens data...")

    #     # Load movies
    #     movies_df = pd.read_csv(os.path.join(self.data_path, "movies.csv"))
    #     for _, row in movies_df.iterrows():
    #         # Extract release year from title (usually in parentheses at the end)
    #         release_year = self._extract_year_from_title(row['title'])
    #         genres = row['genres'].split(
    #             '|') if pd.notna(row['genres']) else []

    #         movie = Movie(
    #             movie_id=str(row['movieId']),
    #             title=row['title'],
    #             genres=genres,
    #             release_year=release_year
    #         )
    #         self.movies[movie.movie_id] = movie
    #         self.genres.update(genres)

    #     # Load ratings
    #     ratings_df = pd.read_csv(os.path.join(self.data_path, "ratings.csv"))
    #     for _, row in ratings_df.iterrows():
    #         rating = UserRating(
    #             user_id=str(row['userId']),
    #             movie_id=str(row['movieId']),
    #             rating=float(row['rating']),
    #             timestamp=datetime.fromtimestamp(row['timestamp'])
    #         )
    #         self.ratings.append(rating)

    #     # Load tags if available
    #     tags_path = os.path.join(self.data_path, "tags.csv")
    #     if os.path.exists(tags_path):
    #         tags_df = pd.read_csv(tags_path)
    #         for _, row in tags_df.iterrows():
    #             tag = Tag(
    #                 movie_id=str(row['movieId']),
    #                 tag_name=row['tag'],
    #                 relevance=1.0  # Default relevance
    #             )
    #             self.tags.append(tag)

    #     # Initialize users from ratings
    #     user_ids = set(rating.user_id for rating in self.ratings)
    #     for user_id in user_ids:
    #         self.users[user_id] = User(user_id=user_id)

    #     logger.info(
    #         f"Loaded {len(self.movies)} movies, {len(self.users)} users, {len(self.ratings)} ratings")

    # def load_data(self):
    #     """Load MovieLens CSV data - Fixed ID matching - so typical when loading CSV data, floats get converted where they should not be etc..."""
    #     logger.info("Loading MovieLens data...")

    #     # Load movies
    #     movies_df = pd.read_csv(os.path.join(self.data_path, "movies.csv"))
    #     for _, row in movies_df.iterrows():
    #         # Extract release year from title (usually in parentheses at the end)
    #         release_year = self._extract_year_from_title(row['title'])
    #         genres = row['genres'].split(
    #             '|') if pd.notna(row['genres']) else []

    #         # Ensure consistent ID format - convert to int then string
    #         movie_id = str(int(float(row['movieId'])))

    #         movie = Movie(
    #             movie_id=movie_id,
    #             title=row['title'],
    #             genres=genres,
    #             release_year=release_year
    #         )
    #         self.movies[movie.movie_id] = movie
    #         self.genres.update(genres)

    #     # Load ratings
    #     ratings_df = pd.read_csv(os.path.join(self.data_path, "ratings.csv"))
    #     for _, row in ratings_df.iterrows():
    #         # Ensure consistent ID format - convert to int then string
    #         user_id = str(int(float(row['userId'])))
    #         movie_id = str(int(float(row['movieId'])))

    #         rating = UserRating(
    #             user_id=user_id,
    #             movie_id=movie_id,
    #             rating=float(row['rating']),
    #             timestamp=datetime.fromtimestamp(row['timestamp'])
    #         )
    #         self.ratings.append(rating)

    #     # Load tags if available
    #     tags_path = os.path.join(self.data_path, "tags.csv")
    #     if os.path.exists(tags_path):
    #         tags_df = pd.read_csv(tags_path)
    #         for _, row in tags_df.iterrows():
    #             # Ensure consistent ID format
    #             movie_id = str(int(float(row['movieId'])))

    #             tag = Tag(
    #                 movie_id=movie_id,
    #                 tag_name=row['tag'],
    #                 relevance=1.0  # Default relevance
    #             )
    #             self.tags.append(tag)

    #     # Initialize users from ratings
    #     user_ids = set(rating.user_id for rating in self.ratings)
    #     for user_id in user_ids:
    #         self.users[user_id] = User(user_id=user_id)

    #     logger.info(
    #         f"Loaded {len(self.movies)} movies, {len(self.users)} users, {len(self.ratings)} ratings")

    def load_data(self):
        """Load MovieLens CSV data - optimized"""
        logger.info("Loading MovieLens data...")

        # Load movies - fixed tuple unpacking
        movies_df = pd.read_csv(os.path.join(self.data_path, "movies.csv"))
        movies_df['movieId'] = movies_df['movieId'].astype(int).astype(str)

        for row in movies_df.itertuples(index=False, name=None):
            movie_id, title, genres_str = row
            release_year = self._extract_year_from_title(title)
            genres = genres_str.split('|') if pd.notna(genres_str) else []

            movie = Movie(
                movie_id=movie_id,
                title=title,
                genres=genres,
                release_year=release_year
            )
            self.movies[movie_id] = movie
            self.genres.update(genres)

        # Load ratings - fixed tuple unpacking
        ratings_df = pd.read_csv(os.path.join(self.data_path, "ratings.csv"))
        ratings_df['userId'] = ratings_df['userId'].astype(int).astype(str)
        ratings_df['movieId'] = ratings_df['movieId'].astype(int).astype(str)
        ratings_df['timestamp'] = pd.to_datetime(
            ratings_df['timestamp'], unit='s')

        # Convert to list of objects in bulk
        self.ratings = [
            UserRating(user_id=row[0], movie_id=row[1],
                       rating=float(row[2]), timestamp=row[3])
            for row in ratings_df.itertuples(index=False, name=None)
        ]

        # Load tags if available - fixed tuple unpacking
        tags_path = os.path.join(self.data_path, "tags.csv")
        if os.path.exists(tags_path):
            tags_df = pd.read_csv(tags_path)
            tags_df['movieId'] = tags_df['movieId'].astype(int).astype(str)

            self.tags = [
                Tag(movie_id=row[1], tag_name=row[2], relevance=1.0)
                for row in tags_df.itertuples(index=False, name=None)
            ]

        # Initialize users from ratings - use set for faster lookup
        user_ids = set(rating.user_id for rating in self.ratings)
        self.users = {user_id: User(user_id=user_id) for user_id in user_ids}

        logger.info(
            f"Loaded {len(self.movies)} movies, {len(self.users)} users, {len(self.ratings)} ratings")

    def _extract_year_from_title(self, title: str) -> int:
        """Extract release year from movie title"""
        # Look for year in parentheses at the end of title
        match = re.search(r'\((\d{4})\)$', title)
        return int(match.group(1)) if match else None

    # def compute_movie_statistics(self):
    #     """Compute aggregate statistics for movies"""
    #     logger.info("Computing movie statistics...")

    #     # Group ratings by movie
    #     movie_ratings = defaultdict(list)
    #     for rating in self.ratings:
    #         movie_ratings[rating.movie_id].append(rating.rating)

    #     # Update movie statistics
    #     for movie_id, ratings in movie_ratings.items():
    #         if movie_id in self.movies:
    #             self.movies[movie_id].average_rating = np.mean(ratings)
    #             self.movies[movie_id].rating_count = len(ratings)

    # def compute_movie_statistics(self):
    #     """Compute aggregate statistics for movies - Fixed with debugging"""
    #     logger.info("Computing movie statistics...")

    #     # Group ratings by movie
    #     movie_ratings = defaultdict(list)
    #     missing_movies = set()

    #     for rating in self.ratings:
    #         if rating.movie_id in self.movies:
    #             movie_ratings[rating.movie_id].append(rating.rating)
    #         else:
    #             missing_movies.add(rating.movie_id)

    #     if missing_movies:
    #         logger.warning(
    #             f"Found {len(missing_movies)} ratings for movies not in movies.csv")

    #     # Update movie statistics
    #     updated_count = 0
    #     for movie_id, ratings in movie_ratings.items():
    #         if movie_id in self.movies:
    #             self.movies[movie_id].average_rating = float(np.mean(ratings))
    #             self.movies[movie_id].rating_count = len(ratings)
    #             updated_count += 1

    #     logger.info(
    #         f"Updated statistics for {updated_count} movies out of {len(self.movies)} total movies")

    #     # Log some statistics
    #     movies_with_ratings = [
    #         m for m in self.movies.values() if m.rating_count > 0]
    #     if movies_with_ratings:
    #         avg_rating_count = np.mean(
    #             [m.rating_count for m in movies_with_ratings])
    #         logger.info(
    #             f"Average ratings per movie (for movies with ratings): {avg_rating_count:.1f}")
    #     else:
    #         logger.warning("No movies have any ratings!")

    def compute_movie_statistics(self):
        """Compute aggregate statistics for movies - Optimized"""
        logger.info("Computing movie statistics...")

        # Use pandas for fast aggregation
        ratings_df = pd.DataFrame([
            {'movie_id': r.movie_id, 'rating': r.rating}
            for r in self.ratings
        ])

        # Group and aggregate in one operation
        movie_stats = ratings_df.groupby(
            'movie_id')['rating'].agg(['mean', 'count'])

        # Update movie objects
        updated_count = 0
        for movie_id, stats in movie_stats.iterrows():
            if movie_id in self.movies:
                self.movies[movie_id].average_rating = float(stats['mean'])
                self.movies[movie_id].rating_count = int(stats['count'])
                updated_count += 1

        logger.info(f"Updated statistics for {updated_count} movies")

    # def apply_reasoning_rules(self):
    #     """Apply all 24 N3 reasoning rules"""
    #     logger.info("Applying N3 reasoning rules...")

    #     self.compute_movie_statistics()

    #     # Movie Quality Classification Rules (1-4)
    #     self._rule_01_excellent_movies()
    #     self._rule_02_good_movies()
    #     self._rule_03_poor_movies()
    #     self._rule_04_controversial_content()

    #     # Genre Analysis Rules (5-6)
    #     self._rule_05_popular_genres()
    #     self._rule_06_niche_genres()

    #     # Temporal Analysis Rules (7-8)
    #     self._rule_07_classic_movies()
    #     self._rule_08_recent_hits()

    #     # Career Analysis Rules (9-11) - Limited without actor/director data
    #     self._rule_09_prolific_analysis()
    #     self._rule_10_successful_patterns()
    #     self._rule_11_collaboration_detection()

    #     # User Preference Rules (12-14)
    #     self._rule_12_genre_preferences()
    #     self._rule_13_generous_reviewers()
    #     self._rule_14_critical_reviewers()

    #     # Content Similarity Rules (15-16)
    #     self._rule_15_genre_quality_similarity()
    #     self._rule_16_actor_similarity()

    #     # Advanced Recommendation Rules (17-19)
    #     self._rule_17_cross_genre_recommendations()
    #     self._rule_18_collaborative_filtering()
    #     self._rule_19_hidden_gems()

    #     # Seasonal/Contextual Rules (20-21)
    #     self._rule_20_holiday_classification()
    #     self._rule_21_viewing_context()

    #     # Business Intelligence Rules (22-24)
    #     self._rule_22_data_quality()
    #     self._rule_23_revenue_potential()
    #     self._rule_24_audience_segmentation()

    def apply_reasoning_rules(self):
        """Apply all 24 N3 reasoning rules - With progress tracking"""
        logger.info("Applying N3 reasoning rules...")

        self.compute_movie_statistics()

        rules = [
            ("Movie Quality Rules", [
                self._rule_01_excellent_movies,
                self._rule_02_good_movies,
                self._rule_03_poor_movies,
                self._rule_04_controversial_content
            ]),
            ("Genre Analysis Rules", [
                self._rule_05_popular_genres,
                self._rule_06_niche_genres
            ]),
            ("Temporal Analysis Rules", [
                self._rule_07_classic_movies,
                self._rule_08_recent_hits
            ]),
            ("User Preference Rules", [
                self._rule_12_genre_preferences,
                self._rule_13_generous_reviewers,
                self._rule_14_critical_reviewers
            ]),
            ("Content Similarity Rules", [
                self._rule_15_genre_quality_similarity,
                self._rule_16_actor_similarity
            ]),
            ("Recommendation Rules", [
                self._rule_17_cross_genre_recommendations,
                self._rule_18_collaborative_filtering,
                self._rule_19_hidden_gems
            ]),
            ("Contextual Rules", [
                self._rule_20_holiday_classification,
                self._rule_21_viewing_context
            ]),
            ("Business Intelligence Rules", [
                self._rule_22_data_quality,
                self._rule_23_revenue_potential,
                self._rule_24_audience_segmentation
            ])
        ]

        for category, rule_list in rules:
            logger.info(f"Processing {category}...")
            for rule_func in rule_list:
                rule_func()
            logger.info(f"Completed {category}")

    # MOVIE QUALITY CLASSIFICATION RULES (1-4)

    def _rule_01_excellent_movies(self):
        """Rule 1: High-Quality Movie Identification"""
        for movie in self.movies.values():
            if movie.average_rating > 4.0 and movie.rating_count > 20:  # Lowered from 100 to 20:
                movie.quality_tier = "Excellent"
                movie.recommendation_priority = "HIGH"

    def _rule_02_good_movies(self):
        """Rule 2: Good Quality Movie Classification"""
        for movie in self.movies.values():
            if (3.5 < movie.average_rating <= 4.0 and
                movie.rating_count > 10 and          # Lowered from 50 to 10
                    movie.quality_tier is None):
                movie.quality_tier = "Good"
                movie.recommendation_priority = "MEDIUM"

    def _rule_03_poor_movies(self):
        """Rule 3: Poor Quality Movie Detection"""
        for movie in self.movies.values():
            if movie.average_rating < 2.5 and movie.rating_count > 5:  # Lowered from 20 to 5
                movie.quality_tier = "Poor"
                movie.recommendation_priority = "LOW"

    def _rule_04_controversial_content(self):
        """Rule 4: Controversial Content Detection"""
        for movie in self.movies.values():
            if (2.8 < movie.average_rating < 3.2 and
                    movie.rating_count > 30):          # Lowered from 200 to 30
                movie.content_type = "Controversial"

    # GENRE ANALYSIS RULES (5-6)

    # def _rule_05_popular_genres(self):
    #     """Rule 5: Popular Genre Identification"""
    #     genre_ratings = defaultdict(int)
    #     for movie in self.movies.values():
    #         for genre in movie.genres:
    #             genre_ratings[genre] += movie.rating_count

    #     for genre, total_ratings in genre_ratings.items():
    #         if total_ratings > 5000:
    #             self.genre_stats[genre] = {
    #                 'popularity_level': 'HIGH',
    #                 'market_appeal': 'Mainstream'
    #             }
    # def _rule_05_popular_genres(self):
    #     """Rule 5: Popular Genre Identification - changing the calculation"""
    #     genre_ratings = defaultdict(int)
    #     genre_movies = defaultdict(int)
    #     # down from 5000, because it's a small dataset and we are generous minded ppl
    #     rating_count_qulifier = 1000
    #     for movie in self.movies.values():
    #         if movie.rating_count > 0:  # Only count movies with ratings
    #             for genre in movie.genres:
    #                 if genre != "(no genres listed)":
    #                     genre_ratings[genre] += movie.rating_count
    #                     genre_movies[genre] += 1

    #     for genre, total_ratings in genre_ratings.items():
    #         if total_ratings > rating_count_qulifier:
    #             self.genre_stats[genre] = {
    #                 'popularity_level': 'HIGH',
    #                 'market_appeal': 'Mainstream',
    #                 'total_ratings': total_ratings,
    #                 'movie_count': genre_movies[genre]
    #             }

    def _rule_05_popular_genres(self):
        """Rule 5: Popular Genre Identification - Calibrated thresholds"""
        genre_ratings = defaultdict(int)
        genre_movies = defaultdict(int)

        for movie in self.movies.values():
            if movie.rating_count > 0:
                for genre in movie.genres:
                    if genre != "(no genres listed)":
                        genre_ratings[genre] += movie.rating_count
                        genre_movies[genre] += 1

        # Calculate dataset-relative thresholds
        if genre_ratings:
            total_ratings = sum(genre_ratings.values())
            avg_ratings_per_genre = total_ratings / len(genre_ratings)

            # Top 30% of genres by ratings = mainstream
            mainstream_threshold = avg_ratings_per_genre * 1.5

            for genre, total_ratings in genre_ratings.items():
                if total_ratings > mainstream_threshold:
                    self.genre_stats[genre] = {
                        'popularity_level': 'HIGH',
                        'market_appeal': 'Mainstream',
                        'total_ratings': total_ratings,
                        'movie_count': genre_movies[genre]
                    }

    # def _rule_06_niche_genres(self):
    #     """Rule 6: Niche Genre Classification"""
    #     genre_data = defaultdict(list)
    #     for movie in self.movies.values():
    #         for genre in movie.genres:
    #             if movie.average_rating > 0:  # Has ratings
    #                 genre_data[genre].append(movie.average_rating)

    #     for genre, ratings in genre_data.items():
    #         if (len(ratings) < 20 and len(ratings) > 5 and
    #                 np.mean(ratings) > 3.8):
    #             self.genre_stats[genre] = {
    #                 'popularity_level': 'NICHE',
    #                 'market_appeal': 'Cult Following'
    #             }

    # def _rule_06_niche_genres(self):
    #     """Rule 6: Niche Genre Classification - v02, as earlier did not return anything meaningful"""
    #     genre_data = defaultdict(list)
    #     genre_movies = defaultdict(int)
    #     rating_count_qulifier = 2

    #     for movie in self.movies.values():
    #         if movie.average_rating > 0 and movie.rating_count >= rating_count_qulifier:  # Has sufficient ratings
    #             for genre in movie.genres:
    #                 if genre != "(no genres listed)":
    #                     genre_data[genre].append(movie.average_rating)
    #                     genre_movies[genre] += 1

    #     for genre, ratings in genre_data.items():
    #         if (5 <= len(ratings) <= 15 and  # Adjusted range: 5-15 movies instead of <20
    #                 np.mean(ratings) > 3.6):      # Lowered from 3.8 to 3.6, because 3.5 is like mid bro...
    #             if genre not in self.genre_stats:
    #                 self.genre_stats[genre] = {}
    #             self.genre_stats[genre].update({
    #                 'popularity_level': 'NICHE',
    #                 'market_appeal': 'Cult Following',
    #                 'movie_count': len(ratings),
    #                 'average_rating': np.mean(ratings)
    #             })

    def _rule_06_niche_genres(self):
        """Rule 6: Niche Genre Classification - Independent of popularity"""
        genre_data = defaultdict(list)
        genre_movies = defaultdict(int)
        genre_ratings = defaultdict(int)

        for movie in self.movies.values():
            if movie.average_rating > 0 and movie.rating_count >= 3:
                for genre in movie.genres:
                    if genre != "(no genres listed)":
                        genre_data[genre].append(movie.average_rating)
                        genre_movies[genre] += 1
                        genre_ratings[genre] += movie.rating_count

        # Calculate dataset-relative thresholds for niche detection
        if genre_movies:
            movie_counts = list(genre_movies.values())
            median_movie_count = sorted(movie_counts)[len(movie_counts)//2]

            for genre, ratings in genre_data.items():
                movie_count = len(ratings)
                avg_rating = sum(ratings) / len(ratings)

                # Niche criteria: Below median movie count BUT high quality
                if (movie_count <= median_movie_count and
                    movie_count >= 5 and  # Minimum for statistical significance
                        avg_rating > 3.7):    # High quality threshold

                    # Initialize if not exists, or update existing
                    if genre not in self.genre_stats:
                        self.genre_stats[genre] = {}

                    self.genre_stats[genre].update({
                        'popularity_level': 'NICHE',
                        'market_appeal': 'Cult Following',
                        'movie_count': movie_count,
                        'average_rating': avg_rating,
                        'total_ratings': genre_ratings[genre]
                    })

    def _add_medium_tier_genres(self):
        """Add medium tier for genres that are neither mainstream nor niche"""
        genre_ratings = defaultdict(int)
        genre_movies = defaultdict(int)

        for movie in self.movies.values():
            if movie.rating_count > 0:
                for genre in movie.genres:
                    if genre != "(no genres listed)":
                        genre_ratings[genre] += movie.rating_count
                        genre_movies[genre] += 1

        # Add medium tier for unclassified genres
        for genre in genre_ratings:
            if genre not in self.genre_stats:
                self.genre_stats[genre] = {
                    'popularity_level': 'MEDIUM',
                    'market_appeal': 'Standard',
                    'total_ratings': genre_ratings[genre],
                    'movie_count': genre_movies[genre]
                }

    # TEMPORAL ANALYSIS RULES (7-8)

    def _rule_07_classic_movies(self):
        """Rule 7: Classic Movie Identification"""
        for movie in self.movies.values():
            if (movie.release_year and
                self.current_year - movie.release_year > 25 and
                    movie.average_rating > 3.8):
                movie.movie_era = "Classic"

    def _rule_08_recent_hits(self):
        """Rule 8: Recent Hit Detection"""
        for movie in self.movies.values():
            if (movie.release_year and
                self.current_year - movie.release_year < 3 and
                movie.average_rating > 4.0 and
                    movie.rating_count > 500):
                movie.movie_era = "Contemporary Hit"
                movie.trend_status = "Trending"

    # CAREER ANALYSIS RULES (9-11) - Simplified without actor/director data

    def _rule_09_prolific_analysis(self):
        """Rule 9: Prolific Analysis (simplified without actor data)"""
        # This would require actor data - placeholder implementation
        pass

    def _rule_10_successful_patterns(self):
        """Rule 10: Successful Pattern Recognition (simplified)"""
        # This would require director data - placeholder implementation
        pass

    def _rule_11_collaboration_detection(self):
        """Rule 11: Collaboration Detection (simplified)"""
        # This would require actor/director data - placeholder implementation
        pass

    # USER PREFERENCE RULES (12-14)

    # def _rule_12_genre_preferences(self):
    #     """Rule 12: Genre Preference Detection"""
    #     user_genre_ratings = defaultdict(lambda: defaultdict(list))

    #     for rating in self.ratings:
    #         if rating.movie_id in self.movies and rating.rating > 4.0:
    #             movie = self.movies[rating.movie_id]
    #             for genre in movie.genres:
    #                 user_genre_ratings[rating.user_id][genre].append(
    #                     rating.rating)

    #     for user_id, genre_ratings in user_genre_ratings.items():
    #         preferred_genres = []
    #         for genre, ratings in genre_ratings.items():
    #             if len(ratings) > 5:  # Minimum threshold
    #                 preferred_genres.append(genre)
    #         self.user_preferences[user_id] = preferred_genres
    #         self.users[user_id].preferred_genres = preferred_genres

    def _rule_12_genre_preferences(self):
        """Rule 12: Genre Preference Detection - Optimized"""
        # Create user-genre-ratings mapping efficiently
        user_genre_high_ratings = defaultdict(lambda: defaultdict(list))

        for rating in self.ratings:
            if rating.rating > 4.0 and rating.movie_id in self.movies:
                movie = self.movies[rating.movie_id]
                for genre in movie.genres:
                    user_genre_high_ratings[rating.user_id][genre].append(
                        rating.rating)

        # Process preferences
        for user_id, genre_ratings in user_genre_high_ratings.items():
            preferred_genres = [genre for genre, ratings in genre_ratings.items()
                                if len(ratings) > 5]

            if preferred_genres:
                self.user_preferences[user_id] = preferred_genres
                self.users[user_id].preferred_genres = preferred_genres

    def _rule_13_generous_reviewers(self):
        """Rule 13: Generous Reviewer Detection"""
        user_ratings = defaultdict(list)
        for rating in self.ratings:
            user_ratings[rating.user_id].append(rating.rating)

        for user_id, ratings in user_ratings.items():
            if len(ratings) > 50 and np.mean(ratings) > 3.8:
                self.users[user_id].rating_behavior = "Generous"
                self.users[user_id].user_type = "Positive Reviewer"

    def _rule_14_critical_reviewers(self):
        """Rule 14: Critical Reviewer Detection"""
        user_ratings = defaultdict(list)
        for rating in self.ratings:
            user_ratings[rating.user_id].append(rating.rating)

        for user_id, ratings in user_ratings.items():
            if len(ratings) > 50 and np.mean(ratings) < 3.0:
                self.users[user_id].rating_behavior = "Critical"
                self.users[user_id].user_type = "Harsh Reviewer"

    # CONTENT SIMILARITY RULES (15-16)

    # def _rule_15_genre_quality_similarity(self):
    #     """Rule 15: Genre and Quality-Based Similarity"""
    #     movies_by_genre_tier = defaultdict(list)

    #     for movie in self.movies.values():
    #         if movie.quality_tier:
    #             for genre in movie.genres:
    #                 key = (genre, movie.quality_tier)
    #                 movies_by_genre_tier[key].append(movie.movie_id)

    #     for movies_list in movies_by_genre_tier.values():
    #         if len(movies_list) > 1:
    #             for i, movie1_id in enumerate(movies_list):
    #                 for movie2_id in movies_list[i+1:]:
    #                     movie1 = self.movies[movie1_id]
    #                     movie2 = self.movies[movie2_id]
    #                     if abs(movie1.average_rating - movie2.average_rating) < 0.5:
    #                         if movie1_id not in self.movie_similarities:
    #                             self.movie_similarities[movie1_id] = []
    #                         if movie2_id not in self.movie_similarities:
    #                             self.movie_similarities[movie2_id] = []
    #                         self.movie_similarities[movie1_id].append(
    #                             movie2_id)
    #                         self.movie_similarities[movie2_id].append(
    #                             movie1_id)

    def _rule_15_genre_quality_similarity(self):
        """Rule 15: Genre and Quality-Based Similarity - Optimized"""
        # Limit to top movies to avoid O(n²) complexity
        quality_movies = [m for m in self.movies.values()
                          if m.quality_tier in ["Excellent", "Good"] and m.rating_count > 10]

        # Group by (genre, quality_tier) for faster processing
        genre_quality_groups = defaultdict(list)
        for movie in quality_movies:
            if movie.quality_tier:
                for genre in movie.genres:
                    key = (genre, movie.quality_tier)
                    genre_quality_groups[key].append(movie)

        # Only process groups with multiple movies
        for (genre, tier), movies_list in genre_quality_groups.items():
            if len(movies_list) > 1:
                # Limit comparisons to prevent excessive runtime
                movies_list = movies_list[:20]  # Limit to top 20 per group

                for i, movie1 in enumerate(movies_list):
                    # Limit to 5 comparisons per movie
                    for movie2 in movies_list[i+1:i+6]:
                        if abs(movie1.average_rating - movie2.average_rating) < 0.5:
                            # Initialize if needed
                            if movie1.movie_id not in self.movie_similarities:
                                self.movie_similarities[movie1.movie_id] = []
                            if movie2.movie_id not in self.movie_similarities:
                                self.movie_similarities[movie2.movie_id] = []

                            self.movie_similarities[movie1.movie_id].append(
                                movie2.movie_id)
                            self.movie_similarities[movie2.movie_id].append(
                                movie1.movie_id)

    def _rule_16_actor_similarity(self):
        """Rule 16: Actor-Based Movie Similarity (simplified without actor data)"""
        # This would require actor data - placeholder implementation
        pass

    # ADVANCED RECOMMENDATION RULES (17-19)

    # def _rule_17_cross_genre_recommendations(self):
    #     """Rule 17: Cross-Genre Recommendation"""
    #     for user_id, preferred_genres in self.user_preferences.items():
    #         if user_id not in self.recommendations:
    #             self.recommendations[user_id] = []

    #         for movie in self.movies.values():
    #             if (movie.quality_tier == "Excellent" and
    #                 len(set(movie.genres) & set(preferred_genres)) > 0 and
    #                     len(set(movie.genres) - set(preferred_genres)) > 0):
    #                 self.recommendations[user_id].append(
    #                     (movie.movie_id, "Genre bridge"))

    def _rule_17_cross_genre_recommendations(self):
        """Rule 17: Cross-Genre Recommendation - optimized"""
        if not self.user_preferences:
            return

        # Pre-filter excellent movies by genre for faster lookup
        excellent_movies_by_genre = defaultdict(list)
        for movie in self.movies.values():
            if movie.quality_tier == "Excellent":
                for genre in movie.genres:
                    excellent_movies_by_genre[genre].append(movie)

        # Process only users with preferences, limit recommendations
        # Limit users
        for user_id, preferred_genres in list(self.user_preferences.items())[:100]:
            if user_id not in self.recommendations:
                self.recommendations[user_id] = []

            preferred_set = set(preferred_genres)
            recommendations_added = 0

            # Check only movies in preferred genres that also have other genres
            for genre in preferred_genres:
                if recommendations_added >= 5:  # Limit recommendations per user
                    break

                # Limit movies per genre
                for movie in excellent_movies_by_genre[genre][:10]:
                    movie_genres_set = set(movie.genres)
                    if (movie_genres_set & preferred_set and
                            movie_genres_set - preferred_set):  # Has both preferred and new genres
                        self.recommendations[user_id].append(
                            (movie.movie_id, "Genre bridge"))
                        recommendations_added += 1
                        if recommendations_added >= 5:
                            break

    # def _rule_18_collaborative_filtering(self):
    #     """Rule 18: Collaborative Filtering Pattern"""
    #     # Find users with similar preferences who both liked the same movies
    #     similar_users = defaultdict(set)

    #     for user1_id, genres1 in self.user_preferences.items():
    #         for user2_id, genres2 in self.user_preferences.items():
    #             if user1_id != user2_id and set(genres1) & set(genres2):
    #                 # Check if they both liked the same movies
    #                 user1_high_ratings = {r.movie_id for r in self.ratings
    #                                       if r.user_id == user1_id and r.rating > 4.0}
    #                 user2_high_ratings = {r.movie_id for r in self.ratings
    #                                       if r.user_id == user2_id and r.rating > 4.0}

    #                 if user1_high_ratings & user2_high_ratings:
    #                     similar_users[user1_id].add(user2_id)
    #                     similar_users[user2_id].add(user1_id)

    def _rule_18_collaborative_filtering(self):
        """Rule 18: Collaborative Filtering Pattern - Optimized"""
        if not self.user_preferences:
            return

        # Create user high-rating sets efficiently
        user_high_ratings = {}
        for rating in self.ratings:
            if rating.rating > 4.0:
                if rating.user_id not in user_high_ratings:
                    user_high_ratings[rating.user_id] = set()
                user_high_ratings[rating.user_id].add(rating.movie_id)

        # Limit to users with sufficient data and preferences
        active_users = [uid for uid, ratings in user_high_ratings.items()
                        if len(ratings) >= 10 and uid in self.user_preferences][:50]  # Limit to 50 users

        similar_users = defaultdict(set)

        # Compare only active users with shared preferences
        for i, user1_id in enumerate(active_users):
            genres1 = set(self.user_preferences[user1_id])
            user1_ratings = user_high_ratings[user1_id]

            # Limit comparisons per user
            for user2_id in active_users[i+1:i+6]:
                genres2 = set(self.user_preferences[user2_id])

                # Quick check: must have overlapping preferences
                if genres1 & genres2:
                    user2_ratings = user_high_ratings[user2_id]
                    shared_movies = user1_ratings & user2_ratings

                    # Must have at least 3 shared high-rated movies
                    if len(shared_movies) >= 3:
                        similar_users[user1_id].add(user2_id)
                        similar_users[user2_id].add(user1_id)

        logger.info(
            f"Found {len(similar_users)} users with similar preferences")

    # def _rule_19_hidden_gems(self):
    #     """Rule 19: Hidden Gem Discovery"""
    #     for movie in self.movies.values():
    #         if (movie.average_rating > 4.0 and
    #             20 < movie.rating_count < 100 and
    #             movie.release_year and
    #                 self.current_year - movie.release_year > 5):
    #             # Add to general recommendations as hidden gems
    #             for user_id in self.users.keys():
    #                 if user_id not in self.recommendations:
    #                     self.recommendations[user_id] = []
    #                 self.recommendations[user_id].append(
    #                     (movie.movie_id, "Hidden Gem"))

    # def _rule_19_hidden_gems(self):
    #     """Rule 19: Hidden Gem Discovery - v02 - Relaxed criteria"""
    #     hidden_gem_candidates = []

    #     for movie in self.movies.values():
    #         if (movie.average_rating > 3.8 and          # Lowered from 4.0 to 3.8
    #             10 <= movie.rating_count <= 50 and      # Lowered range: 10-50 instead of 20-100
    #             movie.release_year and
    #                 self.current_year - movie.release_year > 3):  # Lowered from 5 to 3 years

    #             hidden_gem_candidates.append(movie.movie_id)

    #             # Add to recommendations for all users
    #             # Limit to first 100 users for performance
    #             for user_id in list(self.users.keys())[:100]:
    #                 if user_id not in self.recommendations:
    #                     self.recommendations[user_id] = []
    #                 self.recommendations[user_id].append(
    #                     (movie.movie_id, "Hidden Gem"))

    #     logger.info(
    #         f"Found {len(hidden_gem_candidates)} hidden gem candidates")

    # def _rule_19_hidden_gems(self):
    #     """Rule 19: Hidden Gem Discovery - Optimized, relaxed criteria from v02 apply here too"""
    #     hidden_gems = []

    #     for movie in self.movies.values():
    #         if (movie.average_rating > 3.8 and
    #             10 <= movie.rating_count <= 50 and
    #             movie.release_year and
    #                 self.current_year - movie.release_year > 3):
    #             hidden_gems.append(movie.movie_id)

    #     logger.info(f"Found {len(hidden_gems)} hidden gems")

    #     # Add to recommendations more efficiently - limit users
    #     if hidden_gems:
    #         sample_users = list(self.users.keys())[:50]  # Limit to 50 users
    #         for user_id in sample_users:
    #             if user_id not in self.recommendations:
    #                 self.recommendations[user_id] = []
    #             # Add only top 3 hidden gems per user
    #             for gem_id in hidden_gems[:3]:
    #                 self.recommendations[user_id].append(
    #                     (gem_id, "Hidden Gem"))

    def _rule_19_hidden_gems(self):
        """Rule 19: Hidden Gem Discovery - Highly optimized"""
        # Find hidden gems efficiently
        hidden_gems = []

        for movie in self.movies.values():
            if (movie.average_rating > 3.8 and
                10 <= movie.rating_count <= 50 and
                movie.release_year and
                self.current_year - movie.release_year > 3 and
                    movie.quality_tier not in ["Poor", "Insufficient Data"]):
                hidden_gems.append((movie.movie_id, movie.average_rating))

        # Sort by rating and take top gems
        hidden_gems.sort(key=lambda x: x[1], reverse=True)
        top_gems = [gem_id for gem_id,
                    _ in hidden_gems[:10]]  # Limit to top 10

        logger.info(f"Found {len(top_gems)} top hidden gems")

        # Add to recommendations efficiently - very limited scope
        if top_gems:
            # Only add to users who have made many ratings (active users)
            active_user_ratings = defaultdict(int)
            for rating in self.ratings:
                active_user_ratings[rating.user_id] += 1

            active_users = [uid for uid, count in active_user_ratings.items()
                            if count >= 20][:20]  # Top 20 most active users only

            for user_id in active_users:
                if user_id not in self.recommendations:
                    self.recommendations[user_id] = []

                # Add only top 3 hidden gems per user
                for gem_id in top_gems[:3]:
                    self.recommendations[user_id].append(
                        (gem_id, "Hidden Gem"))

    # SEASONAL/CONTEXTUAL RULES (20-21)

    def _rule_20_holiday_classification(self):
        """Rule 20: Holiday Movie Classification"""
        holiday_keywords = {
            'Christmas': ['christmas', 'xmas', 'holiday', 'santa'],
            'Halloween': ['halloween', 'horror', 'scary', 'monster']
        }

        for tag in self.tags:
            tag_lower = tag.tag_name.lower()
            for holiday, keywords in holiday_keywords.items():
                if any(keyword in tag_lower for keyword in keywords):
                    if tag.movie_id in self.movies:
                        self.movies[tag.movie_id].seasonal_type = holiday

    def _rule_21_viewing_context(self):
        """Rule 21: Viewing Context Recommendations"""
        for movie in self.movies.values():
            # Estimate duration based on genre (simplified approach)
            long_genres = {'Drama', 'Epic', 'War', 'Biography'}
            short_genres = {'Comedy', 'Animation', 'Short'}

            if any(genre in long_genres for genre in movie.genres):
                estimated_duration = 150  # minutes
            elif any(genre in short_genres for genre in movie.genres):
                estimated_duration = 90
            else:
                estimated_duration = 120  # default

            movie.duration = estimated_duration

            if estimated_duration > 150 and movie.average_rating > 3.8:
                movie.viewing_occasion = "Weekend"
            elif estimated_duration < 100 and movie.average_rating > 3.5:
                movie.viewing_occasion = "Weekday"

    # BUSINESS INTELLIGENCE RULES (22-24)

    def _rule_22_data_quality(self):
        """Rule 22: Data Quality Assessment"""
        # rating_count_qualifier = 3  # let's be a bit generous...
        rating_count_qualifier = 2  # let's be even more generous...
        for movie in self.movies.values():
            if movie.rating_count < rating_count_qualifier:
                # Mark as insufficient data quality
                movie.quality_tier = "Insufficient Data"

    def _rule_23_revenue_potential(self):
        """Rule 23: Revenue Potential Analysis"""
        for movie in self.movies.values():
            if (movie.quality_tier == "Excellent" and
                    movie.movie_era == "Contemporary Hit"):
                # High revenue potential
                pass  # Would add business metadata

    def _rule_24_audience_segmentation(self):
        """Rule 24: Audience Segmentation for Marketing"""
        # Simplified age-based segmentation
        for user in self.users.values():
            if user.preferred_genres:
                primary_genre = user.preferred_genres[0] if user.preferred_genres else None
                if primary_genre == "Action":
                    user.audience_segment = "Action Fans"
                elif primary_genre == "Drama":
                    user.audience_segment = "Drama Enthusiasts"
                elif primary_genre == "Comedy":
                    user.audience_segment = "Comedy Lovers"

    def diagnose_data_issues(self):
        """Diagnose potential data loading and statistics computation issues"""
        print(f"=== DATA DIAGNOSTICS ===")
        print(f"Total movies loaded: {len(self.movies)}")
        print(f"Total ratings loaded: {len(self.ratings)}")
        print(f"Total users: {len(self.users)}")
        print(f"Total genres: {len(self.genres)}")

        # Check movie IDs from ratings vs movies
        rating_movie_ids = set(r.movie_id for r in self.ratings)
        movie_ids = set(self.movies.keys())

        print(f"Unique movie IDs in ratings: {len(rating_movie_ids)}")
        print(f"Unique movie IDs in movies: {len(movie_ids)}")
        print(f"Intersection: {len(rating_movie_ids & movie_ids)}")
        print(
            f"Ratings for missing movies: {len(rating_movie_ids - movie_ids)}")

        # Check data types
        if self.ratings:
            sample_rating = self.ratings[0]
            print(
                f"Sample rating movie_id type: {type(sample_rating.movie_id)} = {sample_rating.movie_id}")

        if self.movies:
            sample_movie_id = next(iter(self.movies.keys()))
            print(
                f"Sample movie_id type: {type(sample_movie_id)} = {sample_movie_id}")

        # Check movies with ratings after statistics computation
        movies_with_ratings = [
            m for m in self.movies.values() if m.rating_count > 0]
        print(f"Movies with rating_count > 0: {len(movies_with_ratings)}")

        if movies_with_ratings:
            sample_movie = movies_with_ratings[0]
            print(
                f"Sample movie with ratings: {sample_movie.title} (count: {sample_movie.rating_count}, avg: {sample_movie.average_rating:.2f})")

    def diagnose_genre_distribution(self):
        """Diagnose genre rating distributions to calibrate thresholds"""
        print("=== GENRE DISTRIBUTION ANALYSIS ===")

        genre_ratings = defaultdict(int)
        genre_movies = defaultdict(int)
        genre_avg_ratings = defaultdict(list)

        for movie in self.movies.values():
            if movie.rating_count > 0:
                for genre in movie.genres:
                    if genre != "(no genres listed)":
                        genre_ratings[genre] += movie.rating_count
                        genre_movies[genre] += 1
                        genre_avg_ratings[genre].append(movie.average_rating)

        # Sort by total ratings
        sorted_genres = sorted(genre_ratings.items(),
                               key=lambda x: x[1], reverse=True)

        print(f"{'Genre':<15} {'Movies':<8} {'Total Ratings':<12} {'Avg Rating':<10}")
        print("-" * 50)

        for genre, total_ratings in sorted_genres:
            movie_count = genre_movies[genre]
            avg_rating = sum(
                genre_avg_ratings[genre]) / len(genre_avg_ratings[genre])
            print(
                f"{genre:<15} {movie_count:<8} {total_ratings:<12} {avg_rating:<10.2f}")

        # Show distribution statistics
        rating_counts = list(genre_ratings.values())
        print(f"\nRating Distribution Stats:")
        print(f"Min: {min(rating_counts)}")
        print(f"Max: {max(rating_counts)}")
        print(f"Median: {sorted(rating_counts)[len(rating_counts)//2]}")
        print(f"Mean: {sum(rating_counts)/len(rating_counts):.0f}")

    def generate_report(self) -> str:
        """Generate comprehensive reasoning report"""
        report = ["=" * 80]
        report.append("MOVIELENS N3 ONTOLOGY REASONING REPORT")
        report.append("=" * 80)
        report.append("")

        # Movie Quality Distribution
        quality_dist = Counter(
            movie.quality_tier for movie in self.movies.values() if movie.quality_tier)
        report.append("MOVIE QUALITY DISTRIBUTION:")
        for tier, count in quality_dist.most_common():
            report.append(f"  {tier}: {count} movies")
        report.append("")

        # Genre Analysis
        report.append("GENRE ANALYSIS:")
        for genre, stats in self.genre_stats.items():
            report.append(f"  {genre}: {stats}")
        report.append("")

        # Era Classification
        era_dist = Counter(
            movie.movie_era for movie in self.movies.values() if movie.movie_era)
        report.append("MOVIE ERA DISTRIBUTION:")
        for era, count in era_dist.most_common():
            report.append(f"  {era}: {count} movies")
        report.append("")

        # User Behavior Analysis
        behavior_dist = Counter(
            user.rating_behavior for user in self.users.values() if user.rating_behavior)
        report.append("USER BEHAVIOR DISTRIBUTION:")
        for behavior, count in behavior_dist.most_common():
            report.append(f"  {behavior}: {count} users")
        report.append("")

        # Top Recommendations by Category
        report.append("SAMPLE RECOMMENDATIONS:")
        excellent_movies = [
            m for m in self.movies.values() if m.quality_tier == "Excellent"]
        if excellent_movies:
            report.append("  Top Excellent Movies:")
            for movie in sorted(excellent_movies, key=lambda x: x.average_rating, reverse=True)[:5]:
                report.append(
                    f"    {movie.title} (Rating: {movie.average_rating:.2f}, Count: {movie.rating_count})")
        report.append("")

        # Hidden Gems
        hidden_gems = []
        for user_recs in self.recommendations.values():
            hidden_gems.extend(
                [movie_id for movie_id, reason in user_recs if reason == "Hidden Gem"])

        if hidden_gems:
            gem_counts = Counter(hidden_gems)
            report.append("  Top Hidden Gems:")
            for movie_id, _ in gem_counts.most_common(5):
                if movie_id in self.movies:
                    movie = self.movies[movie_id]
                    report.append(
                        f"    {movie.title} (Rating: {movie.average_rating:.2f})")

        return "\n".join(report)


def main():
    """Main execution function"""
    reasoner = MovieLensReasoner()

    try:
        # Load data
        reasoner.load_data()

        # Apply reasoning rules
        reasoner.apply_reasoning_rules()

        # run diagnostics...
        print("\n" + "="*50)
        print("DATA DIAGNOSTICS")
        print("="*50)
        reasoner.diagnose_data_issues()

        # Generate and display report
        report = reasoner.generate_report()
        print(report)

        # Save detailed results
        logger.info("Reasoning complete. Results available in reasoner object.")

        return reasoner

    except Exception as e:
        logger.error(f"Error during reasoning: {e}")
        raise


if __name__ == "__main__":
    reasoner = main()
