# Usage example and extended functionality for the MovieLens N3 Ontology Reasoner

import json
import pandas as pd
from movielens_reasoner import MovieLensReasoner, Movie, User
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns


class MovieLensAnalyzer:
    """Extended analyzer with visualization and export capabilities"""

    def __init__(self, reasoner: MovieLensReasoner):
        self.reasoner = reasoner

    def export_reasoning_results(self, output_file: str = "reasoning_results.json"):
        """Export reasoning results to JSON"""
        results = {
            "movies": {},
            "users": {},
            "genre_stats": self.reasoner.genre_stats,
            "recommendations_summary": {},
            "statistics": self.get_reasoning_statistics()
        }

        # Export movie data with reasoning results
        for movie_id, movie in self.reasoner.movies.items():
            results["movies"][movie_id] = {
                "title": movie.title,
                "genres": movie.genres,
                "release_year": movie.release_year,
                "average_rating": movie.average_rating,
                "rating_count": movie.rating_count,
                "quality_tier": movie.quality_tier,
                "recommendation_priority": movie.recommendation_priority,
                "content_type": movie.content_type,
                "movie_era": movie.movie_era,
                "trend_status": movie.trend_status,
                "seasonal_type": movie.seasonal_type,
                "viewing_occasion": movie.viewing_occasion
            }

        # Export user data with reasoning results
        for user_id, user in self.reasoner.users.items():
            results["users"][user_id] = {
                "rating_behavior": user.rating_behavior,
                "user_type": user.user_type,
                "preferred_genres": user.preferred_genres,
                "audience_segment": user.audience_segment
            }

        # Export recommendation summary
        for user_id, recs in self.reasoner.recommendations.items():
            rec_summary = {}
            for movie_id, reason in recs:
                if reason not in rec_summary:
                    rec_summary[reason] = []
                rec_summary[reason].append(movie_id)
            results["recommendations_summary"][user_id] = rec_summary

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"Reasoning results exported to {output_file}")

    def get_reasoning_statistics(self) -> Dict:
        """Get comprehensive statistics from reasoning"""
        stats = {}

        # Movie quality statistics
        quality_counts = {}
        for movie in self.reasoner.movies.values():
            tier = movie.quality_tier or "Unclassified"
            quality_counts[tier] = quality_counts.get(tier, 0) + 1
        stats["quality_distribution"] = quality_counts

        # Era distribution
        era_counts = {}
        for movie in self.reasoner.movies.values():
            era = movie.movie_era or "Unclassified"
            era_counts[era] = era_counts.get(era, 0) + 1
        stats["era_distribution"] = era_counts

        # User behavior distribution
        behavior_counts = {}
        for user in self.reasoner.users.values():
            behavior = user.rating_behavior or "Unclassified"
            behavior_counts[behavior] = behavior_counts.get(behavior, 0) + 1
        stats["user_behavior_distribution"] = behavior_counts

        # Recommendation statistics
        total_recommendations = sum(
            len(recs) for recs in self.reasoner.recommendations.values())
        unique_users_with_recs = len(
            [uid for uid, recs in self.reasoner.recommendations.items() if recs])
        stats["recommendation_stats"] = {
            "total_recommendations": total_recommendations,
            "users_with_recommendations": unique_users_with_recs,
            "average_recommendations_per_user": total_recommendations / max(unique_users_with_recs, 1)
        }

        return stats

    def get_movie_recommendations_for_user(self, user_id: str, limit: int = 10) -> List[Tuple[str, str, str]]:
        """Get personalized movie recommendations for a specific user"""
        if user_id not in self.reasoner.users:
            return []

        recommendations = []

        # Get explicit recommendations from reasoning
        if user_id in self.reasoner.recommendations:
            for movie_id, reason in self.reasoner.recommendations[user_id][:limit]:
                if movie_id in self.reasoner.movies:
                    movie = self.reasoner.movies[movie_id]
                    recommendations.append(
                        (movie.title, reason, f"Rating: {movie.average_rating:.2f}"))

        # Add similar movies based on user preferences
        user = self.reasoner.users[user_id]
        if user.preferred_genres and len(recommendations) < limit:
            for movie in self.reasoner.movies.values():
                if len(recommendations) >= limit:
                    break

                if (movie.quality_tier in ["Excellent", "Good"] and
                        any(genre in user.preferred_genres for genre in movie.genres)):

                    # Check if not already recommended
                    if movie.title not in [rec[0] for rec in recommendations]:
                        recommendations.append((
                            movie.title,
                            "Genre preference match",
                            f"Rating: {movie.average_rating:.2f}"
                        ))

        return recommendations

    # def analyze_genre_trends(self) -> pd.DataFrame:
    #     """Analyze genre trends and popularity"""
    #     genre_data = []

    #     for genre in self.reasoner.genres:
    #         if genre == "(no genres listed)":
    #             continue

    #         genre_movies = [
    #             m for m in self.reasoner.movies.values() if genre in m.genres]

    #         if genre_movies:
    #             total_ratings = sum(m.rating_count for m in genre_movies)
    #             avg_rating = sum(
    #                 m.average_rating * m.rating_count for m in genre_movies) / max(total_ratings, 1)
    #             movie_count = len(genre_movies)

    #             # Calculate era distribution
    #             classic_count = sum(
    #                 1 for m in genre_movies if m.movie_era == "Classic")
    #             contemporary_count = sum(
    #                 1 for m in genre_movies if m.movie_era == "Contemporary Hit")

    #             genre_data.append({
    #                 "genre": genre,
    #                 "movie_count": movie_count,
    #                 "total_ratings": total_ratings,
    #                 "average_rating": avg_rating,
    #                 "classic_movies": classic_count,
    #                 "contemporary_hits": contemporary_count,
    #                 "popularity_level": self.reasoner.genre_stats.get(genre, {}).get("popularity_level", "MEDIUM"),
    #                 "market_appeal": self.reasoner.genre_stats.get(genre, {}).get("market_appeal", "Standard")
    #             })

    #     return pd.DataFrame(genre_data).sort_values("total_ratings", ascending=False)

    def analyze_genre_trends(self) -> pd.DataFrame:
        """Analyze genre trends and popularity - Fixed with empty data handling"""
        genre_data = []

        for genre in self.reasoner.genres:
            if genre == "(no genres listed)":
                continue

            genre_movies = [m for m in self.reasoner.movies.values()
                            if genre in m.genres and m.rating_count > 0]

            if genre_movies:
                total_ratings = sum(m.rating_count for m in genre_movies)
                # Weighted average calculation
                total_weighted_rating = sum(
                    m.average_rating * m.rating_count for m in genre_movies)
                avg_rating = total_weighted_rating / total_ratings if total_ratings > 0 else 0
                movie_count = len(genre_movies)

                # Calculate era distribution
                classic_count = sum(
                    1 for m in genre_movies if m.movie_era == "Classic")
                contemporary_count = sum(
                    1 for m in genre_movies if m.movie_era == "Contemporary Hit")

                # Get stats from reasoner
                genre_stats = self.reasoner.genre_stats.get(genre, {})

                genre_data.append({
                    "genre": genre,
                    "movie_count": movie_count,
                    "total_ratings": total_ratings,
                    "average_rating": round(avg_rating, 2),
                    "classic_movies": classic_count,
                    "contemporary_hits": contemporary_count,
                    "popularity_level": genre_stats.get("popularity_level", "MEDIUM"),
                    "market_appeal": genre_stats.get("market_appeal", "Standard")
                })

        # Handle empty data case
        if not genre_data:
            # Return empty DataFrame with proper columns
            return pd.DataFrame(columns=[
                "genre", "movie_count", "total_ratings", "average_rating",
                "classic_movies", "contemporary_hits", "popularity_level", "market_appeal"
            ])

        return pd.DataFrame(genre_data).sort_values("total_ratings", ascending=False)

    # def find_hidden_gems(self, min_rating: float = 4.0, max_ratings: int = 100) -> List[Tuple[str, float, int]]:
    #     """Find hidden gem movies based on criteria"""
    #     hidden_gems = []

    #     for movie in self.reasoner.movies.values():
    #         if (movie.average_rating >= min_rating and
    #             20 <= movie.rating_count <= max_ratings and
    #                 movie.quality_tier != "Insufficient Data"):
    #             hidden_gems.append(
    #                 (movie.title, movie.average_rating, movie.rating_count))

    #     return sorted(hidden_gems, key=lambda x: x[1], reverse=True)

    def find_hidden_gems(self, min_rating: float = 3.8, max_ratings: int = 50) -> List[Tuple[str, float, int]]:
        """Find hidden gem movies based on slight relaxed criteria due to smaller dataset"""
        hidden_gems = []

        for movie in self.reasoner.movies.values():
            if (movie.average_rating >= min_rating and
                10 <= movie.rating_count <= max_ratings and  # Lowered minimum from 20 to 10
                    movie.quality_tier not in ["Insufficient Data", "Poor"]):
                hidden_gems.append(
                    (movie.title, movie.average_rating, movie.rating_count))

        return sorted(hidden_gems, key=lambda x: x[1], reverse=True)

    def analyze_user_segments(self) -> Dict:
        """Analyze user segments and their characteristics"""
        segments = {}

        for user in self.reasoner.users.values():
            segment = user.audience_segment or "Unclassified"
            if segment not in segments:
                segments[segment] = {
                    "count": 0,
                    "rating_behaviors": {},
                    "preferred_genres": {}
                }

            segments[segment]["count"] += 1

            # Track rating behaviors
            behavior = user.rating_behavior or "Standard"
            segments[segment]["rating_behaviors"][behavior] = segments[segment]["rating_behaviors"].get(
                behavior, 0) + 1

            # Track preferred genres
            if user.preferred_genres:
                for genre in user.preferred_genres:
                    segments[segment]["preferred_genres"][genre] = segments[segment]["preferred_genres"].get(
                        genre, 0) + 1

        return segments


def example_usage():
    """Example of how to use the MovieLens reasoner"""

    print("MovieLens N3 Ontology Reasoner - Usage Example")
    print("=" * 60)

    # Initialize and run reasoner
    print("1. Initializing reasoner...")
    reasoner = MovieLensReasoner()

    print("2. Loading MovieLens data...")
    reasoner.load_data()

    print("3. Applying N3 reasoning rules...")
    reasoner.apply_reasoning_rules()

    print("4. Generating analysis...")
    analyzer = MovieLensAnalyzer(reasoner)

    # Basic statistics
    print("\n" + "="*50)
    print("REASONING STATISTICS")
    print("="*50)

    stats = analyzer.get_reasoning_statistics()

    print("Movie Quality Distribution:")
    for tier, count in stats["quality_distribution"].items():
        print(f"  {tier}: {count}")

    print("\nUser Behavior Distribution:")
    for behavior, count in stats["user_behavior_distribution"].items():
        print(f"  {behavior}: {count}")

    print(f"\nRecommendation Statistics:")
    rec_stats = stats["recommendation_stats"]
    print(f"  Total recommendations: {rec_stats['total_recommendations']}")
    print(
        f"  Users with recommendations: {rec_stats['users_with_recommendations']}")
    print(
        f"  Average per user: {rec_stats['average_recommendations_per_user']:.2f}")

    # Genre analysis
    print("\n" + "="*50)
    print("GENRE ANALYSIS")
    print("="*50)

    genre_df = analyzer.analyze_genre_trends()
    print("Top 10 Genres by Total Ratings:")
    print(genre_df.head(10)[
          ["genre", "movie_count", "total_ratings", "average_rating"]].to_string(index=False))

    # Hidden gems
    print("\n" + "="*50)
    print("HIDDEN GEMS")
    print("="*50)

    hidden_gems = analyzer.find_hidden_gems()
    print("Top 10 Hidden Gems:")
    for i, (title, rating, count) in enumerate(hidden_gems[:10], 1):
        print(f"  {i:2d}. {title} (Rating: {rating:.2f}, Votes: {count})")

    # User recommendations example
    print("\n" + "="*50)
    print("SAMPLE USER RECOMMENDATIONS")
    print("="*50)

    # Get a sample user
    sample_users = list(reasoner.users.keys())[:3]
    for user_id in sample_users:
        print(f"\nRecommendations for User {user_id}:")
        recs = analyzer.get_movie_recommendations_for_user(user_id, limit=5)
        if recs:
            for i, (title, reason, details) in enumerate(recs, 1):
                print(f"  {i}. {title} - {reason} ({details})")
        else:
            print("  No specific recommendations available")

    # Export results
    print("\n" + "="*50)
    print("EXPORTING RESULTS")
    print("="*50)

    analyzer.export_reasoning_results("movielens_reasoning_results.json")
    print("Results exported successfully!")

    return reasoner, analyzer


# Imma not use this RN
def create_requirements_file():
    """Create requirements.txt for the project"""
    requirements = [
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0"
    ]

    with open("requirements.txt", "w") as f:
        f.write("\n".join(requirements))

    print("requirements.txt created successfully!")


if __name__ == "__main__":
    # Run the example
    reasoner, analyzer = example_usage()

    # Create requirements file
    # create_requirements_file()

    print("\n" + "="*60)
    print("MovieLens N3 Ontology Reasoner completed successfully!")
    print("Check 'movielens_reasoning_results.json' for detailed results.")
    print("="*60)
