# Usage example and extended functionality for the MovieLens N3 Ontology Reasoner

import json
import pandas as pd
from movielens_reasoner import MovieLensReasoner, Movie, User
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os


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

    # def analyze_genre_trends(self) -> pd.DataFrame:
    #     """Analyze genre trends and popularity - Fixed with empty data handling"""
    #     genre_data = []

    #     for genre in self.reasoner.genres:
    #         if genre == "(no genres listed)":
    #             continue

    #         genre_movies = [m for m in self.reasoner.movies.values()
    #                         if genre in m.genres and m.rating_count > 0]

    #         if genre_movies:
    #             total_ratings = sum(m.rating_count for m in genre_movies)
    #             # Weighted average calculation
    #             total_weighted_rating = sum(
    #                 m.average_rating * m.rating_count for m in genre_movies)
    #             avg_rating = total_weighted_rating / total_ratings if total_ratings > 0 else 0
    #             movie_count = len(genre_movies)

    #             # Calculate era distribution
    #             classic_count = sum(
    #                 1 for m in genre_movies if m.movie_era == "Classic")
    #             contemporary_count = sum(
    #                 1 for m in genre_movies if m.movie_era == "Contemporary Hit")

    #             # Get stats from reasoner
    #             genre_stats = self.reasoner.genre_stats.get(genre, {})

    #             genre_data.append({
    #                 "genre": genre,
    #                 "movie_count": movie_count,
    #                 "total_ratings": total_ratings,
    #                 "average_rating": round(avg_rating, 2),
    #                 "classic_movies": classic_count,
    #                 "contemporary_hits": contemporary_count,
    #                 "popularity_level": genre_stats.get("popularity_level", "MEDIUM"),
    #                 "market_appeal": genre_stats.get("market_appeal", "Standard")
    #             })

    def analyze_genre_trends(self) -> pd.DataFrame:
        """Analyze genre trends and popularity - Enhanced with proper categorization"""
        genre_data = []

        for genre in self.reasoner.genres:
            if genre == "(no genres listed)":
                continue

            genre_movies = [m for m in self.reasoner.movies.values()
                            if genre in m.genres and m.rating_count > 0]

            if genre_movies:
                total_ratings = sum(m.rating_count for m in genre_movies)
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
                    "market_appeal": genre_stats.get("market_appeal", "Standard"),
                    "ratings_per_movie": round(total_ratings / movie_count, 1)
                })

        if not genre_data:
            return pd.DataFrame(columns=[
                "genre", "movie_count", "total_ratings", "average_rating",
                "classic_movies", "contemporary_hits", "popularity_level",
                "market_appeal", "ratings_per_movie"
            ])

        return pd.DataFrame(genre_data).sort_values("total_ratings", ascending=False)

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

    def generate_markdown_report(self, output_file: str = None) -> str:
        """Generate comprehensive markdown report"""
        if output_file is None:
            output_file = os.path.join('./', "movielens_analysis_report.md")
            # reasoner.data_path, "ontologies", "analysis_report.md")

        # Get all the analysis data
        stats = self.get_reasoning_statistics()
        genre_df = self.analyze_genre_trends()
        hidden_gems = self.find_hidden_gems()
        user_segments = self.analyze_user_segments()

        # Build markdown content
        lines = [
            "# MovieLens N3 Ontology Reasoning Report",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "## Executive Summary",
            "",
            f"This report presents the results of applying 24 N3 reasoning rules to the MovieLens dataset, "
            f"containing {len(self.reasoner.movies):,} movies, {len(self.reasoner.users):,} users, "
            f"and {len(self.reasoner.ratings):,} ratings.",
            "",
            "---",
            "",
            "## Reasoning Statistics",
            "",
            "### Movie Quality Distribution",
            ""
        ]

        # Movie quality table
        lines.append("| Quality Tier | Count | Percentage |")
        lines.append("|--------------|-------|------------|")
        total_movies = len(self.reasoner.movies)
        for tier, count in stats["quality_distribution"].items():
            percentage = (count / total_movies) * 100
            lines.append(f"| {tier} | {count:,} | {percentage:.1f}% |")

        lines.extend([
            "",
            "### Movie Era Distribution",
            "",
            "| Era | Count |",
            "|-----|-------|"
        ])

        for era, count in stats["era_distribution"].items():
            lines.append(f"| {era} | {count:,} |")

        lines.extend([
            "",
            "### User Behavior Analysis",
            "",
            "| Behavior Type | Count |",
            "|---------------|-------|"
        ])

        for behavior, count in stats["user_behavior_distribution"].items():
            lines.append(f"| {behavior} | {count:,} |")

        # Recommendation statistics
        rec_stats = stats["recommendation_stats"]
        lines.extend([
            "",
            "### Recommendation Engine Performance",
            "",
            f"- **Total Recommendations Generated**: {rec_stats['total_recommendations']:,}",
            f"- **Users with Recommendations**: {rec_stats['users_with_recommendations']:,}",
            f"- **Average Recommendations per User**: {rec_stats['average_recommendations_per_user']:.1f}",
            "",
            "---",
            "",
            "## Genre Analysis",
            ""
        ])

        # Genre analysis tables
        if not genre_df.empty:
            lines.extend([
                "### Top Genres by Total Ratings",
                "",
                "| Rank | Genre | Movies | Total Ratings | Avg Rating | Popularity Level |",
                "|------|-------|--------|---------------|------------|------------------|"
            ])

            for i, (_, row) in enumerate(genre_df.head(10).iterrows(), 1):
                lines.append(
                    f"| {i} | {row['genre']} | {row['movie_count']} | {row['total_ratings']:,} | {row['average_rating']:.2f} | {row['popularity_level']} |")

            # Separate by popularity levels
            mainstream = genre_df[genre_df['popularity_level'] == 'HIGH']
            niche = genre_df[genre_df['popularity_level'] == 'NICHE']

            if not mainstream.empty:
                lines.extend([
                    "",
                    "### Mainstream Genres",
                    "",
                    "| Genre | Total Ratings | Movies | Market Appeal |",
                    "|-------|---------------|--------|---------------|"
                ])
                for _, row in mainstream.iterrows():
                    lines.append(
                        f"| {row['genre']} | {row['total_ratings']:,} | {row['movie_count']} | {row['market_appeal']} |")

            if not niche.empty:
                lines.extend([
                    "",
                    "### Niche Genres",
                    "",
                    "| Genre | Avg Rating | Movies | Market Appeal |",
                    "|-------|------------|--------|---------------|"
                ])
                for _, row in niche.iterrows():
                    lines.append(
                        f"| {row['genre']} | {row['average_rating']:.2f} | {row['movie_count']} | {row['market_appeal']} |")

        lines.extend([
            "",
            "---",
            "",
            "## Hidden Gems Discovery",
            ""
        ])

        if hidden_gems:
            lines.extend([
                "High-quality movies with limited exposure that deserve more attention:",
                "",
                "| Rank | Movie Title | Rating | Vote Count |",
                "|------|-------------|--------|------------|"
            ])

            for i, (title, rating, count) in enumerate(hidden_gems[:15], 1):
                lines.append(f"| {i} | {title} | {rating:.2f} | {count} |")
        else:
            lines.append("*No hidden gems identified with current criteria.*")

        lines.extend([
            "",
            "---",
            "",
            "## User Segmentation Analysis",
            ""
        ])

        if user_segments:
            for segment, data in user_segments.items():
                if data['count'] > 0:
                    lines.extend([
                        f"### {segment}",
                        f"**Users**: {data['count']:,}",
                        ""
                    ])

                    if data['preferred_genres']:
                        lines.append("**Top Preferred Genres**:")
                        top_genres = sorted(data['preferred_genres'].items(
                        ), key=lambda x: x[1], reverse=True)[:5]
                        for genre, count in top_genres:
                            lines.append(f"- {genre}: {count} users")
                        lines.append("")

                    if data['rating_behaviors']:
                        lines.append("**Rating Behaviors**:")
                        for behavior, count in data['rating_behaviors'].items():
                            lines.append(f"- {behavior}: {count} users")
                        lines.append("")

        # Sample recommendations
        lines.extend([
            "---",
            "",
            "## 🎬 Sample Personalized Recommendations",
            ""
        ])

        # Get sample recommendations for a few users
        sample_users = list(self.reasoner.users.keys())[:3]
        for user_id in sample_users:
            recs = self.get_movie_recommendations_for_user(user_id, limit=5)
            if recs:
                lines.extend([
                    f"### User {user_id}",
                    "",
                    "| Movie | Reason | Details |",
                    "|-------|--------|---------|"
                ])
                for title, reason, details in recs:
                    lines.append(f"| {title} | {reason} | {details} |")
                lines.append("")

        # Business insights
        lines.extend([
            "---",
            "",
            "## Business Insights",
            "",
            "### Key Findings",
            ""
        ])

        # Generate insights based on data
        excellent_count = stats["quality_distribution"].get("Excellent", 0)
        total_movies = sum(stats["quality_distribution"].values())
        excellent_pct = (excellent_count / total_movies) * \
            100 if total_movies > 0 else 0

        lines.extend([
            f"- **Quality Distribution**: {excellent_pct:.1f}% of movies achieve 'Excellent' status",
            f"- **Genre Diversity**: {len(genre_df)} distinct genres identified in the dataset",
            f"- **Hidden Opportunities**: {len(hidden_gems)} underrated movies identified for promotion",
            f"- **User Engagement**: {rec_stats['users_with_recommendations']} users eligible for personalized recommendations"
        ])

        if not mainstream.empty and not niche.empty:
            lines.extend([
                "",
                "### Strategic Recommendations",
                "",
                f"- **Mainstream Focus**: Leverage {len(mainstream)} high-volume genres for broad market appeal",
                f"- **Niche Cultivation**: Develop {len(niche)} specialized genres for targeted audiences",
                "- **Quality Enhancement**: Focus on elevating movies currently in 'Good' tier to 'Excellent'",
                "- **Discovery Features**: Implement hidden gems recommendations to improve catalog utilization"
            ])

        lines.extend([
            "",
            "---",
            "",
            "## Technical Details",
            "",
            "### Reasoning Rules Applied",
            "",
            "This analysis applied 24 N3 reasoning rules across the following categories:",
            "",
            "- **Movie Quality Classification** (Rules 1-4): Excellent, Good, Poor, Controversial",
            "- **Genre Analysis** (Rules 5-6): Popular and Niche genre identification",
            "- **Temporal Analysis** (Rules 7-8): Classic movies and Contemporary hits",
            "- **User Preferences** (Rules 12-14): Genre preferences and reviewer behavior",
            "- **Content Similarity** (Rules 15-16): Genre and quality-based similarity",
            "- **Advanced Recommendations** (Rules 17-19): Cross-genre and hidden gems",
            "- **Contextual Analysis** (Rules 20-21): Seasonal and viewing context",
            "- **Business Intelligence** (Rules 22-24): Data quality and audience segmentation",
            "",
            "### Data Processing Statistics",
            "",
            f"- **Movies Processed**: {len(self.reasoner.movies):,}",
            f"- **Ratings Analyzed**: {len(self.reasoner.ratings):,}",
            f"- **Users Profiled**: {len(self.reasoner.users):,}",
            f"- **Genres Identified**: {len(self.reasoner.genres)}",
            f"- **Reasoning Outputs**: {sum(stats['quality_distribution'].values()):,} classifications",
            "",
            "---",
            "",
            "*Report generated by MovieLens N3 Ontology Reasoner*"
        ])

        # Write to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"Markdown report saved to {output_file}")
        return '\n'.join(lines)


def example_usage():
    """Example of how to use the MovieLens reasoner"""

    print("MovieLens N3 Ontology Reasoner - Usage Example")
    print("." * 60)

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
    print("\n" + "."*50)
    print("REASONING STATISTICS")
    print("."*50)

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

    print("\n" + "."*50)
    print("GENRE DISTRIBUTION DIAGNOSTICS")
    print("."*50)
    reasoner.diagnose_genre_distribution()

    # Genre analysis
    print("\n" + "."*50)
    print("GENRE ANALYSIS")
    print("."*50)

    # genre_df = analyzer.analyze_genre_trends()
    # print("Top 10 Genres by Total Ratings:")
    # print(genre_df.head(10)[
    #       ["genre", "movie_count", "total_ratings", "average_rating"]].to_string(index=False))

    genre_df = analyzer.analyze_genre_trends()
    print("All Genres by Popularity Level:")
    print(genre_df[["genre", "popularity_level", "market_appeal",
          "total_ratings", "movie_count"]].to_string(index=False))

    print("\nMainstream Genres:")
    mainstream = genre_df[genre_df['popularity_level'] == 'HIGH']
    if not mainstream.empty:
        print(mainstream[["genre", "total_ratings",
              "movie_count"]].to_string(index=False))
    else:
        print("No mainstream genres found")

    print("\nNiche Genres:")
    niche = genre_df[genre_df['popularity_level'] == 'NICHE']
    if not niche.empty:
        print(niche[["genre", "average_rating", "movie_count"]
                    ].to_string(index=False))
    else:
        print("No niche genres found")

    print("\nMedium Tier Genres:")
    medium = genre_df[genre_df['popularity_level'] == 'MEDIUM']
    if not medium.empty:
        print(medium[["genre", "total_ratings", "movie_count"]
                     ].head().to_string(index=False))
    else:
        print("No medium tier genres found")

    # Hidden gems
    print("\n" + "."*50)
    print("HIDDEN GEMS")
    print("."*50)

    hidden_gems = analyzer.find_hidden_gems()
    print("Top 10 Hidden Gems:")
    for i, (title, rating, count) in enumerate(hidden_gems[:10], 1):
        print(f"  {i:2d}. {title} (Rating: {rating:.2f}, Votes: {count})")

    # User recommendations example
    print("\n" + "."*50)
    print("SAMPLE USER RECOMMENDATIONS")
    print("."*50)

    # Get a few sample users
    sample_users = list(reasoner.users.keys())[:5]
    for user_id in sample_users:
        print(f"\nRecommendations for User {user_id}:")
        recs = analyzer.get_movie_recommendations_for_user(user_id, limit=5)
        if recs:
            for i, (title, reason, details) in enumerate(recs, 1):
                print(f"  {i}. {title} - {reason} ({details})")
        else:
            print("  No specific recommendations available")

    # Export results
    print("\n" + "."*50)
    print("EXPORTING RESULTS")
    print("."*50)

    analyzer.export_reasoning_results("movielens_reasoning_results.json")
    print("Results exported successfully!")

    # Generate Markdown Report
    print("\n" + "."*50)
    print("GENERATING MARKDOWN REPORT")
    print("."*50)

    report_content = analyzer.generate_markdown_report()
    report_file = os.path.join('./', "movielens_analysis_report.md")
    # reasoner.data_path, "ontologies", "analysis_report.md")
    print(f"Comprehensive markdown report saved to: {report_file}")
    print(f"Report length: {len(report_content.split())} words")

    return reasoner, analyzer


if __name__ == "__main__":
    # Run the example
    reasoner, analyzer = example_usage()

    print("\n" + "."*60)
    print("MovieLens N3 Ontology Reasoner completed successfully!")
    print("Check 'movielens_reasoning_results.json' for detailed results.")
    print("."*60)
