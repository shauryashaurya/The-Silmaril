#!/usr/bin/env python3
"""
Music Ontology Reasoner Usage Analytics
Provides comprehensive analytics, reporting, and business intelligence
for the music industry ontology reasoning system.
"""

import json
import logging
from datetime import datetime, date
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict, Counter
from pathlib import Path
import pandas as pd

# Import the core reasoner
from music_reasoner import MusicReasonerEngine, normalize_id

# Configure logging
logging.basicConfig(
    filename='./music_reasoner_usage.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MusicAnalytics:
    """
    Analytics engine for music industry data.
    Provides statistical analysis, business intelligence, and comprehensive reporting
    based on ontological reasoning results.
    """

    def __init__(self, reasoner: MusicReasonerEngine):
        """Initialize analytics engine with a reasoning engine instance."""
        self.reasoner = reasoner
        self.analysis_timestamp = datetime.now()

    def generate_comprehensive_statistics(self) -> Dict[str, Any]:
        """
        Generate comprehensive statistical analysis of the music industry data.
        Returns detailed metrics covering all aspects of the ontology.
        """
        logger.info("Generating comprehensive statistics...")

        stats = {
            'overview': self._generate_overview_stats(),
            'collaboration_analysis': self._analyze_collaborations(),
            'genre_analysis': self._analyze_genres(),
            'artist_analysis': self._analyze_artists(),
            'album_analysis': self._analyze_albums(),
            'label_analysis': self._analyze_labels(),
            'award_analysis': self._analyze_awards(),
            'influence_network': self._analyze_influence_network(),
            'temporal_analysis': self._analyze_temporal_patterns(),
            'quality_metrics': self._calculate_quality_metrics(),
            'business_insights': self._extract_business_insights()
        }

        logger.info("Comprehensive statistics generation completed")
        return stats

    def _generate_overview_stats(self) -> Dict[str, Any]:
        """Generate high-level overview statistics."""
        return {
            'total_entities': {
                'songs': len(self.reasoner.songs),
                'artists': len(self.reasoner.artists),
                'albums': len(self.reasoner.albums),
                'record_labels': len(self.reasoner.record_labels),
                'genres': len(self.reasoner.genres),
                'awards': len(self.reasoner.awards)
            },
            'reasoning_results': {
                'collaborative_songs': len(self.reasoner.collaborative_songs),
                'established_artists': len(self.reasoner.established_artists),
                'successful_labels': len(self.reasoner.successful_labels),
                'total_inferences': self.reasoner.stats['inferences_made']
            },
            'processing_info': {
                'entities_loaded': self.reasoner.stats['entities_loaded'],
                'processing_time_seconds': self.reasoner.stats['processing_time'],
                'analysis_timestamp': self.analysis_timestamp.isoformat()
            }
        }

    def _analyze_collaborations(self) -> Dict[str, Any]:
        """Analyze collaboration patterns and relationships."""
        collaboration_stats = {
            'total_collaborative_songs': len(self.reasoner.collaborative_songs),
            'collaboration_distribution': {},
            'most_collaborative_artists': [],
            'collaboration_network_density': 0.0,
            'average_collaborations_per_artist': 0.0
        }

        # Analyze collaboration distribution
        collab_counts = Counter()
        for song in self.reasoner.songs.values():
            if song.is_collaborative:
                collab_counts[len(song.artist_ids)] += 1

        collaboration_stats['collaboration_distribution'] = dict(collab_counts)

        # Find most collaborative artists
        artist_collab_counts = []
        for artist in self.reasoner.artists.values():
            collab_count = len(artist.collaboration_partners)
            if collab_count > 0:
                artist_collab_counts.append({
                    'artist_id': artist.id,
                    'artist_name': artist.name,
                    'collaboration_count': collab_count,
                    'total_collaboration_strength': sum(artist.collaboration_strength.values())
                })

        # Sort by collaboration count and take top 10
        artist_collab_counts.sort(
            key=lambda x: x['collaboration_count'], reverse=True)
        collaboration_stats['most_collaborative_artists'] = artist_collab_counts[:10]

        # Calculate network density
        total_artists = len(self.reasoner.artists)
        if total_artists > 1:
            max_possible_collaborations = total_artists * \
                (total_artists - 1) // 2
            actual_collaborations = sum(
                len(partners) for partners in self.reasoner.collaboration_network.values()) // 2
            if max_possible_collaborations > 0:
                collaboration_stats['collaboration_network_density'] = actual_collaborations / \
                    max_possible_collaborations
                collaboration_stats['average_collaborations_per_artist'] = (
                    actual_collaborations * 2) / total_artists
            else:
                collaboration_stats['collaboration_network_density'] = 0.0
                collaboration_stats['average_collaborations_per_artist'] = 0.0
        else:
            collaboration_stats['collaboration_network_density'] = 0.0
            collaboration_stats['average_collaborations_per_artist'] = 0.0

        return collaboration_stats

    def _analyze_genres(self) -> Dict[str, Any]:
        """Analyze genre distribution and relationships."""
        genre_stats = {
            'total_genres': len(self.reasoner.genres),
            'genre_popularity': [],
            'genre_diversity_by_artist': {},
            'genre_similarities': len(self.reasoner.genre_similarity_map),
            'cross_genre_collaborations': 0
        }

        # Calculate genre popularity based on song and album associations
        genre_popularity = Counter()
        for song in self.reasoner.songs.values():
            for genre_id in song.genre_ids:
                genre_popularity[genre_id] += 1

        for album in self.reasoner.albums.values():
            for genre_id in album.genre_ids:
                # Weight albums less than individual songs
                genre_popularity[genre_id] += 0.5

        # Create genre popularity list with names
        genre_pop_list = []
        for genre_id, count in genre_popularity.most_common(10):
            if genre_id in self.reasoner.genres:
                genre_pop_list.append({
                    'genre_id': genre_id,
                    'genre_name': self.reasoner.genres[genre_id].genre_name,
                    'popularity_score': count
                })

        genre_stats['genre_popularity'] = genre_pop_list

        # Analyze genre diversity by artist
        for artist in self.reasoner.artists.values():
            artist_genres = set()
            for song in self.reasoner.songs.values():
                if artist.id in song.artist_ids:
                    artist_genres.update(song.genre_ids)

            if artist_genres:
                genre_stats['genre_diversity_by_artist'][artist.id] = {
                    'artist_name': artist.name,
                    'genre_count': len(artist_genres),
                    'genres': [self.reasoner.genres[g].genre_name for g in artist_genres if g in self.reasoner.genres]
                }

        # Count cross-genre collaborations
        cross_genre_collabs = 0
        for song in self.reasoner.songs.values():
            if song.is_collaborative and len(song.genre_ids) > 1:
                cross_genre_collabs += 1

        genre_stats['cross_genre_collaborations'] = cross_genre_collabs

        return genre_stats

    def _analyze_artists(self) -> Dict[str, Any]:
        """Analyze artist statistics and achievements."""
        artist_stats = {
            'total_artists': len(self.reasoner.artists),
            'established_artists': len(self.reasoner.established_artists),
            'top_artists_by_popularity': [],
            'artist_career_stages': {},
            'nationality_distribution': Counter(),
            'label_distribution': Counter()
        }

        # Analyze top artists by popularity score
        artist_popularity = []
        for artist in self.reasoner.artists.values():
            if artist.popularity_score > 0:
                artist_popularity.append({
                    'artist_id': artist.id,
                    'artist_name': artist.name,
                    'popularity_score': artist.popularity_score,
                    'award_count': artist.award_count,
                    'collaboration_count': len(artist.collaboration_partners),
                    'album_count': artist.album_count,
                    'is_established': artist.is_established
                })

        artist_popularity.sort(
            key=lambda x: x['popularity_score'], reverse=True)
        artist_stats['top_artists_by_popularity'] = artist_popularity[:15]

        # Analyze career stages
        career_stages = {'emerging': 0, 'developing': 0,
                         'established': 0, 'veteran': 0}
        for artist in self.reasoner.artists.values():
            if artist.is_established:
                if artist.album_count >= 5:
                    career_stages['veteran'] += 1
                else:
                    career_stages['established'] += 1
            elif artist.album_count >= 2:
                career_stages['developing'] += 1
            else:
                career_stages['emerging'] += 1

        artist_stats['artist_career_stages'] = career_stages

        # Nationality and label distribution
        for artist in self.reasoner.artists.values():
            if artist.nationality:
                artist_stats['nationality_distribution'][artist.nationality] += 1
            if artist.label_id and artist.label_id in self.reasoner.record_labels:
                label_name = self.reasoner.record_labels[artist.label_id].label_name
                artist_stats['label_distribution'][label_name] += 1

        return artist_stats

    def _analyze_albums(self) -> Dict[str, Any]:
        """Analyze album statistics and trends."""
        album_stats = {
            'total_albums': len(self.reasoner.albums),
            'albums_by_decade': Counter(),
            'average_album_length': 0.0,
            'collaborative_albums': 0,
            'top_albums_by_track_count': [],
            'genre_inheritance_success': 0
        }

        total_tracks = 0
        total_duration = 0
        collaborative_albums = 0
        albums_with_inherited_genres = 0

        track_count_list = []

        for album in self.reasoner.albums.values():
            # Decade analysis
            if album.release_year > 0:
                decade = (album.release_year // 10) * 10
                album_stats['albums_by_decade'][f"{decade}s"] += 1

            # Track and duration analysis
            track_count = len(album.song_ids)
            total_tracks += track_count

            # Calculate album duration from constituent songs
            album_duration = 0
            for song_id in album.song_ids:
                if song_id in self.reasoner.songs:
                    album_duration += self.reasoner.songs[song_id].duration

            album.total_duration = album_duration
            total_duration += album_duration

            # Collaborative album analysis
            if len(album.artist_ids) > 1:
                collaborative_albums += 1

            # Genre inheritance analysis
            if album.inherited_genres:
                albums_with_inherited_genres += 1

            # Track count analysis
            if track_count > 0:
                track_count_list.append({
                    'album_id': album.id,
                    'album_title': album.album_title,
                    'track_count': track_count,
                    'total_duration_minutes': album_duration // 60,
                    'artist_names': [self.reasoner.artists[aid].name for aid in album.artist_ids if aid in self.reasoner.artists]
                })

        # Calculate averages
        if len(self.reasoner.albums) > 0:
            album_stats['average_tracks_per_album'] = total_tracks / \
                len(self.reasoner.albums)
            album_stats['average_album_duration_minutes'] = (
                total_duration // 60) / len(self.reasoner.albums)
        else:
            album_stats['average_tracks_per_album'] = 0.0
            album_stats['average_album_duration_minutes'] = 0.0

        album_stats['collaborative_albums'] = collaborative_albums
        album_stats['genre_inheritance_success'] = albums_with_inherited_genres

        # Top albums by track count
        track_count_list.sort(key=lambda x: x['track_count'], reverse=True)
        album_stats['top_albums_by_track_count'] = track_count_list[:10]

        return album_stats

    def _analyze_labels(self) -> Dict[str, Any]:
        """Analyze record label performance and success metrics."""
        label_stats = {
            'total_labels': len(self.reasoner.record_labels),
            'successful_labels': len(self.reasoner.successful_labels),
            'top_labels_by_success_rating': [],
            'label_artist_distribution': {},
            'average_artists_per_label': 0.0
        }

        # Analyze top labels by success rating
        label_success_list = []
        total_signed_artists = 0

        for label in self.reasoner.record_labels.values():
            artist_count = len(label.signed_artists)
            total_signed_artists += artist_count

            if label.success_rating > 0 or artist_count > 0:
                label_success_list.append({
                    'label_id': label.id,
                    'label_name': label.label_name,
                    'success_rating': label.success_rating,
                    'signed_artists_count': artist_count,
                    'award_winning_artists_count': len(label.award_winning_artists),
                    'is_successful': label.is_successful,
                    'location': label.location
                })

        label_success_list.sort(
            key=lambda x: x['success_rating'], reverse=True)
        label_stats['top_labels_by_success_rating'] = label_success_list[:10]

        # Calculate average artists per label
        if len(self.reasoner.record_labels) > 0:
            label_stats['average_artists_per_label'] = total_signed_artists / \
                len(self.reasoner.record_labels)
        else:
            label_stats['average_artists_per_label'] = 0.0

        # Label size distribution
        size_distribution = Counter()
        for label in self.reasoner.record_labels.values():
            artist_count = len(label.signed_artists)
            if artist_count == 0:
                size_distribution['no_artists'] += 1
            elif artist_count <= 2:
                size_distribution['small_1_2_artists'] += 1
            elif artist_count <= 5:
                size_distribution['medium_3_5_artists'] += 1
            else:
                size_distribution['large_6plus_artists'] += 1

        label_stats['label_size_distribution'] = dict(size_distribution)

        return label_stats

    def _analyze_awards(self) -> Dict[str, Any]:
        """Analyze award distribution and patterns."""
        award_stats = {
            'total_awards': len(self.reasoner.awards),
            'awards_by_year': Counter(),
            'awards_by_body': Counter(),
            'most_awarded_artists': [],
            'most_awarded_songs': [],
            'award_distribution': {}
        }

        # Year and awarding body analysis
        for award in self.reasoner.awards.values():
            if award.year > 0:
                award_stats['awards_by_year'][award.year] += 1
            if award.awarding_body:
                award_stats['awards_by_body'][award.awarding_body] += 1

        # Most awarded artists
        artist_award_counts = Counter()
        for award in self.reasoner.awards.values():
            for artist_id in award.artist_ids:
                if artist_id in self.reasoner.artists:
                    artist_award_counts[artist_id] += 1

        most_awarded_artists = []
        for artist_id, count in artist_award_counts.most_common(10):
            most_awarded_artists.append({
                'artist_id': artist_id,
                'artist_name': self.reasoner.artists[artist_id].name,
                'award_count': count
            })

        award_stats['most_awarded_artists'] = most_awarded_artists

        # Most awarded songs
        song_award_counts = Counter()
        for award in self.reasoner.awards.values():
            for song_id in award.song_ids:
                if song_id in self.reasoner.songs:
                    song_award_counts[song_id] += 1

        most_awarded_songs = []
        for song_id, count in song_award_counts.most_common(10):
            most_awarded_songs.append({
                'song_id': song_id,
                'song_title': self.reasoner.songs[song_id].title,
                'award_count': count
            })

        award_stats['most_awarded_songs'] = most_awarded_songs

        return award_stats

    def _analyze_influence_network(self) -> Dict[str, Any]:
        """Analyze the influence network structure and patterns."""
        influence_stats = {
            'total_influence_relationships': 0,
            'most_influential_artists': [],
            'most_influenced_artists': [],
            'influence_network_density': 0.0,
            'influence_clusters': []
        }

        # Calculate total influence relationships
        total_influences = sum(
            len(influences) for influences in self.reasoner.influence_network.values())
        influence_stats['total_influence_relationships'] = total_influences

        # Most influential artists (those who influence many others)
        influential_artists = []
        for artist in self.reasoner.artists.values():
            influence_count = len(artist.influences)
            if influence_count > 0:
                influential_artists.append({
                    'artist_id': artist.id,
                    'artist_name': artist.name,
                    'influences_count': influence_count,
                    'influenced_by_count': len(artist.influenced_by)
                })

        influential_artists.sort(
            key=lambda x: x['influences_count'], reverse=True)
        influence_stats['most_influential_artists'] = influential_artists[:10]

        # Most influenced artists (those influenced by many others)
        influenced_artists = influential_artists.copy()
        influenced_artists.sort(
            key=lambda x: x['influenced_by_count'], reverse=True)
        influence_stats['most_influenced_artists'] = influenced_artists[:10]

        # Calculate network density
        total_artists = len(self.reasoner.artists)
        if total_artists > 1:
            max_possible_influences = total_artists * (total_artists - 1)
            if max_possible_influences > 0:
                influence_stats['influence_network_density'] = total_influences / \
                    max_possible_influences
            else:
                influence_stats['influence_network_density'] = 0.0
        else:
            influence_stats['influence_network_density'] = 0.0

        return influence_stats

    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in the music data."""
        temporal_stats = {
            'release_timeline': {},
            'contemporary_artist_clusters': {},
            'career_span_analysis': {},
            'decade_popularity': {}
        }

        # Release timeline analysis
        release_years = Counter()
        for album in self.reasoner.albums.values():
            if album.release_year > 0:
                release_years[album.release_year] += 1

        for song in self.reasoner.songs.values():
            if song.release_date:
                # Weight songs less than albums
                release_years[song.release_date.year] += 0.5

        temporal_stats['release_timeline'] = dict(release_years.most_common())

        # Contemporary artist analysis
        contemporary_clusters = defaultdict(int)
        for artist in self.reasoner.artists.values():
            cluster_size = len(artist.contemporary_artists)
            if cluster_size > 0:
                contemporary_clusters[cluster_size] += 1

        temporal_stats['contemporary_artist_clusters'] = dict(
            contemporary_clusters)

        # Decade popularity analysis
        decade_activity = Counter()
        for album in self.reasoner.albums.values():
            if album.release_year > 0:
                decade = (album.release_year // 10) * 10
                decade_activity[f"{decade}s"] += len(album.artist_ids)

        temporal_stats['decade_popularity'] = dict(
            decade_activity.most_common())

        return temporal_stats

    def _calculate_quality_metrics(self) -> Dict[str, Any]:
        """Calculate data quality and completeness metrics."""
        quality_metrics = {
            'completeness_scores': {},
            'relationship_integrity': {},
            'data_consistency': {}
        }

        # Completeness scores
        songs_with_complete_data = sum(1 for song in self.reasoner.songs.values()
                                       if song.artist_ids and song.genre_ids and song.duration > 0)

        artists_with_complete_data = sum(1 for artist in self.reasoner.artists.values()
                                         if artist.name and artist.nationality and artist.birth_date)

        albums_with_complete_data = sum(1 for album in self.reasoner.albums.values()
                                        if album.artist_ids and album.release_year > 0 and album.song_ids)

        quality_metrics['completeness_scores'] = {
            'songs_complete_percentage': (songs_with_complete_data / len(self.reasoner.songs)) * 100 if self.reasoner.songs else 0,
            'artists_complete_percentage': (artists_with_complete_data / len(self.reasoner.artists)) * 100 if self.reasoner.artists else 0,
            'albums_complete_percentage': (albums_with_complete_data / len(self.reasoner.albums)) * 100 if self.reasoner.albums else 0
        }

        # Relationship integrity
        orphaned_songs = sum(
            1 for song in self.reasoner.songs.values() if not song.artist_ids)
        orphaned_albums = sum(
            1 for album in self.reasoner.albums.values() if not album.artist_ids)
        unsigned_artists = sum(
            1 for artist in self.reasoner.artists.values() if not artist.label_id)

        total_entities = len(self.reasoner.songs) + len(self.reasoner.albums)
        orphaned_entities = orphaned_songs + orphaned_albums

        quality_metrics['relationship_integrity'] = {
            'orphaned_songs': orphaned_songs,
            'orphaned_albums': orphaned_albums,
            'unsigned_artists': unsigned_artists,
            'relationship_completeness_score': ((total_entities - orphaned_entities) / total_entities) * 100 if total_entities > 0 else 100
        }

        return quality_metrics

    def _extract_business_insights(self) -> Dict[str, Any]:
        """Extract actionable business insights from the analysis."""
        insights = {
            'collaboration_opportunities': [],
            'emerging_genres': [],
            'label_performance_insights': [],
            'artist_development_recommendations': [],
            'market_trends': []
        }

        # Collaboration opportunities - artists in similar genres who haven't collaborated
        genre_artist_map = defaultdict(set)
        for song in self.reasoner.songs.values():
            for genre_id in song.genre_ids:
                for artist_id in song.artist_ids:
                    genre_artist_map[genre_id].add(artist_id)

        collaboration_opportunities = []
        for genre_id, artist_ids in genre_artist_map.items():
            if len(artist_ids) >= 2:
                artist_list = list(artist_ids)
                for i in range(len(artist_list)):
                    for j in range(i + 1, len(artist_list)):
                        artist1_id, artist2_id = artist_list[i], artist_list[j]
                        if (artist1_id in self.reasoner.artists and artist2_id in self.reasoner.artists and
                                artist2_id not in self.reasoner.artists[artist1_id].collaboration_partners):
                            collaboration_opportunities.append({
                                'artist1': self.reasoner.artists[artist1_id].name,
                                'artist2': self.reasoner.artists[artist2_id].name,
                                'shared_genre': self.reasoner.genres[genre_id].genre_name if genre_id in self.reasoner.genres else genre_id,
                                'potential_score': self.reasoner.artists[artist1_id].popularity_score + self.reasoner.artists[artist2_id].popularity_score
                            })

        # Sort by potential score and take top opportunities
        collaboration_opportunities.sort(
            key=lambda x: x['potential_score'], reverse=True)
        insights['collaboration_opportunities'] = collaboration_opportunities[:5]

        # Emerging genres - genres with high growth in collaborations
        genre_collaboration_count = Counter()
        for song in self.reasoner.songs.values():
            if song.is_collaborative:
                for genre_id in song.genre_ids:
                    genre_collaboration_count[genre_id] += 1

        emerging_genres = []
        for genre_id, collab_count in genre_collaboration_count.most_common(5):
            if genre_id in self.reasoner.genres:
                emerging_genres.append({
                    'genre_name': self.reasoner.genres[genre_id].genre_name,
                    'collaboration_count': collab_count,
                    'growth_indicator': 'high' if collab_count > 3 else 'moderate'
                })

        insights['emerging_genres'] = emerging_genres

        # Label performance insights
        label_insights = []
        for label in self.reasoner.record_labels.values():
            if label.signed_artists:
                signed_artist_scores = [self.reasoner.artists[aid].popularity_score
                                        for aid in label.signed_artists if aid in self.reasoner.artists]
                avg_artist_popularity = sum(
                    signed_artist_scores) / len(signed_artist_scores) if signed_artist_scores else 0

                label_insights.append({
                    'label_name': label.label_name,
                    'performance_rating': 'excellent' if label.is_successful else 'developing',
                    'artist_count': len(label.signed_artists),
                    'average_artist_popularity': avg_artist_popularity,
                    'recommendation': 'Focus on artist development' if avg_artist_popularity < 5 else 'Maintain current strategy'
                })

        label_insights.sort(
            key=lambda x: x['average_artist_popularity'], reverse=True)
        insights['label_performance_insights'] = label_insights[:5]

        # Artist development recommendations
        development_recommendations = []
        for artist in self.reasoner.artists.values():
            if not artist.is_established and artist.popularity_score > 0:
                potential_score = artist.popularity_score + \
                    len(artist.collaboration_partners)
                development_recommendations.append({
                    'artist_name': artist.name,
                    'current_stage': 'developing' if artist.album_count >= 1 else 'emerging',
                    'recommendation': self._get_artist_recommendation(artist),
                    'potential_score': potential_score
                })

        development_recommendations.sort(
            key=lambda x: x['potential_score'], reverse=True)
        insights['artist_development_recommendations'] = development_recommendations[:5]

        return insights

    def _get_artist_recommendation(self, artist) -> str:
        """Generate specific recommendation for an artist based on their profile."""
        if artist.album_count == 0:
            return "Release debut album to establish presence"
        elif artist.album_count == 1 and not artist.collaboration_partners:
            return "Explore collaborations to expand audience"
        elif len(artist.collaboration_partners) > 0 and artist.award_count == 0:
            return "Focus on award-worthy quality in next release"
        elif artist.album_count >= 2 and artist.award_count == 0:
            return "Target award submissions and industry recognition"
        else:
            return "Continue current trajectory toward establishment"

    def generate_json_report(self, output_path: str) -> None:
        """Generate comprehensive JSON report with all analysis results."""
        logger.info(f"Generating JSON report at {output_path}")

        # Generate comprehensive statistics
        stats = self.generate_comprehensive_statistics()

        # Add entity data
        report = {
            'metadata': {
                'report_type': 'Music Industry Ontology Analysis',
                'generated_at': self.analysis_timestamp.isoformat(),
                'data_source': 'CSV files processed through N3 ontology reasoning',
                'version': '1.0'
            },
            'statistics': stats,
            'entities': {
                'songs': {song.id: self._serialize_song(song) for song in self.reasoner.songs.values()},
                'artists': {artist.id: self._serialize_artist(artist) for artist in self.reasoner.artists.values()},
                'albums': {album.id: self._serialize_album(album) for album in self.reasoner.albums.values()},
                'record_labels': {label.id: self._serialize_label(label) for label in self.reasoner.record_labels.values()},
                'genres': {genre.id: self._serialize_genre(genre) for genre in self.reasoner.genres.values()},
                'awards': {award.id: self._serialize_award(award) for award in self.reasoner.awards.values()}
            },
            'reasoning_results': {
                'collaborative_songs': list(self.reasoner.collaborative_songs),
                'successful_labels': list(self.reasoner.successful_labels),
                'established_artists': list(self.reasoner.established_artists),
                'collaboration_network': {k: dict(v) for k, v in self.reasoner.collaboration_network.items()},
                'influence_network': {k: list(v) for k, v in self.reasoner.influence_network.items()},
                'genre_similarity_map': {k: list(v) for k, v in self.reasoner.genre_similarity_map.items()}
            }
        }

        # Save JSON report
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str, ensure_ascii=False)

        logger.info(f"JSON report saved successfully to {output_path}")

    def _serialize_song(self, song) -> Dict:
        """Serialize song entity for JSON export."""
        return {
            'id': song.id,
            'title': song.title,
            'duration': song.duration,
            'release_date': song.release_date.isoformat() if song.release_date else None,
            'artist_ids': list(song.artist_ids),
            'album_ids': list(song.album_ids),
            'genre_ids': list(song.genre_ids),
            'award_ids': list(song.award_ids),
            'is_collaborative': song.is_collaborative,
            'collaboration_count': song.collaboration_count,
            'primary_genre': song.primary_genre
        }

    def _serialize_artist(self, artist) -> Dict:
        """Serialize artist entity for JSON export."""
        return {
            'id': artist.id,
            'name': artist.name,
            'birth_date': artist.birth_date.isoformat() if artist.birth_date else None,
            'nationality': artist.nationality,
            'label_id': artist.label_id,
            'is_established': artist.is_established,
            'collaboration_partners': list(artist.collaboration_partners),
            'collaboration_strength': dict(artist.collaboration_strength),
            'influenced_by': list(artist.influenced_by),
            'influences': list(artist.influences),
            'popularity_score': artist.popularity_score,
            'award_count': artist.award_count,
            'album_count': artist.album_count,
            'contemporary_artists': list(artist.contemporary_artists)
        }

    def _serialize_album(self, album) -> Dict:
        """Serialize album entity for JSON export."""
        return {
            'id': album.id,
            'album_title': album.album_title,
            'release_year': album.release_year,
            'artist_ids': list(album.artist_ids),
            'label_id': album.label_id,
            'genre_ids': list(album.genre_ids),
            'song_ids': list(album.song_ids),
            'inherited_genres': list(album.inherited_genres),
            'total_duration': album.total_duration,
            'track_count': album.track_count,
            'contributors': list(album.contributors)
        }

    def _serialize_label(self, label) -> Dict:
        """Serialize record label entity for JSON export."""
        return {
            'id': label.id,
            'label_name': label.label_name,
            'location': label.location,
            'is_successful': label.is_successful,
            'signed_artists': list(label.signed_artists),
            'success_rating': label.success_rating,
            'award_winning_artists': list(label.award_winning_artists)
        }

    def _serialize_genre(self, genre) -> Dict:
        """Serialize genre entity for JSON export."""
        return {
            'id': genre.id,
            'genre_name': genre.genre_name,
            'description': genre.description,
            'related_genres': list(genre.related_genres),
            'artist_count': genre.artist_count,
            'song_count': genre.song_count,
            'album_count': genre.album_count
        }

    def _serialize_award(self, award) -> Dict:
        """Serialize award entity for JSON export."""
        return {
            'id': award.id,
            'award_name': award.award_name,
            'year': award.year,
            'awarding_body': award.awarding_body,
            'artist_ids': list(award.artist_ids),
            'song_ids': list(award.song_ids)
        }

    def generate_markdown_report(self, output_path: str) -> None:
        """Generate comprehensive markdown report with formatted analysis."""
        logger.info(f"Generating Markdown report at {output_path}")

        stats = self.generate_comprehensive_statistics()

        markdown_content = self._build_markdown_report(stats)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        logger.info(f"Markdown report saved successfully to {output_path}")

    def _build_markdown_report(self, stats: Dict[str, Any]) -> str:
        """Build formatted markdown report content."""
        md = []

        # Header
        md.append("# Music Industry Ontology Analysis Report\n")
        # md.append(
        #     f"**Generated:** {self.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
        md.append(
            f"**Processing Time:** {stats['overview']['processing_info']['processing_time_seconds']:.2f} seconds\n")
        md.append(
            f"**Total Inferences:** {stats['overview']['reasoning_results']['total_inferences']}\n\n")

        # Executive Summary
        md.append("## Executive Summary\n")
        overview = stats['overview']
        md.append(
            f"This analysis covers **{overview['total_entities']['songs']} songs**, ")
        md.append(f"**{overview['total_entities']['artists']} artists**, ")
        md.append(f"**{overview['total_entities']['albums']} albums**, ")
        md.append(
            f"**{overview['total_entities']['record_labels']} record labels**, ")
        md.append(f"**{overview['total_entities']['genres']} genres**, and ")
        md.append(f"**{overview['total_entities']['awards']} awards** ")
        md.append("in the music industry dataset.\n\n")

        md.append("### Key Findings\n")
        md.append(
            f"- **{overview['reasoning_results']['collaborative_songs']} collaborative songs** identified through reasoning\n")
        md.append(
            f"- **{overview['reasoning_results']['established_artists']} established artists** with multiple albums and awards\n")
        md.append(
            f"- **{overview['reasoning_results']['successful_labels']} successful record labels** with award-winning artists\n")

        # Safely calculate and display collaboration network density
        collab_density = stats['collaboration_analysis'].get(
            'collaboration_network_density', 0.0)
        md.append(
            f"- **{collab_density:.4f}** collaboration network density\n\n")

        # Collaboration Analysis
        md.append("## Collaboration Analysis\n")
        collab_stats = stats['collaboration_analysis']
        md.append(
            f"The music industry shows **{collab_stats['total_collaborative_songs']} collaborative songs** ")
        avg_collabs = collab_stats.get(
            'average_collaborations_per_artist', 0.0)
        md.append(
            f"with an average of **{avg_collabs:.1f} collaborations per artist**.\n\n")

        if collab_stats['most_collaborative_artists']:
            md.append("### Most Collaborative Artists\n")
            md.append("| Rank | Artist | Collaborations | Total Strength |\n")
            md.append("|------|--------|----------------|----------------|\n")
            for i, artist in enumerate(collab_stats['most_collaborative_artists'][:5], 1):
                md.append(
                    f"| {i} | {artist['artist_name']} | {artist['collaboration_count']} | {artist['total_collaboration_strength']} |\n")
            md.append("\n")

        # Genre Analysis
        md.append("## Genre Analysis\n")
        genre_stats = stats['genre_analysis']
        md.append(
            f"Analysis reveals **{genre_stats['total_genres']} distinct genres** ")
        md.append(
            f"with **{genre_stats['cross_genre_collaborations']} cross-genre collaborations**.\n\n")

        if genre_stats['genre_popularity']:
            md.append("### Most Popular Genres\n")
            md.append("| Rank | Genre | Popularity Score |\n")
            md.append("|------|-------|------------------|\n")
            for i, genre in enumerate(genre_stats['genre_popularity'][:5], 1):
                md.append(
                    f"| {i} | {genre['genre_name']} | {genre['popularity_score']:.1f} |\n")
            md.append("\n")

        # Artist Analysis
        md.append("## Artist Analysis\n")
        artist_stats = stats['artist_analysis']
        md.append(
            f"The dataset includes **{artist_stats['total_artists']} artists** ")
        established_percentage = (
            artist_stats['established_artists'] / artist_stats['total_artists'] * 100) if artist_stats['total_artists'] > 0 else 0
        md.append(
            f"with **{artist_stats['established_artists']} ({established_percentage:.1f}%) established artists**.\n\n")

        # Career stage distribution
        stages = artist_stats['artist_career_stages']
        md.append("### Artist Career Stage Distribution\n")
        md.append("| Stage | Count | Percentage |\n")
        md.append("|-------|-------|------------|\n")
        total_artists = sum(stages.values())
        for stage, count in stages.items():
            percentage = (count / total_artists *
                          100) if total_artists > 0 else 0
            md.append(f"| {stage.title()} | {count} | {percentage:.1f}% |\n")
        md.append("\n")

        # Top artists by popularity
        if artist_stats['top_artists_by_popularity']:
            md.append("### Top Artists by Popularity Score\n")
            md.append(
                "| Rank | Artist | Popularity | Awards | Collaborations | Albums | Status |\n")
            md.append(
                "|------|--------|------------|--------|----------------|--------|---------|\n")
            for i, artist in enumerate(artist_stats['top_artists_by_popularity'][:10], 1):
                status = "Established" if artist['is_established'] else "Developing"
                md.append(
                    f"| {i} | {artist['artist_name']} | {artist['popularity_score']} | ")
                md.append(
                    f"{artist['award_count']} | {artist['collaboration_count']} | ")
                md.append(f"{artist['album_count']} | {status} |\n")
            md.append("\n")

        # Album Analysis
        md.append("## Album Analysis\n")
        album_stats = stats['album_analysis']
        avg_tracks = album_stats.get('average_tracks_per_album', 0.0)
        avg_duration = album_stats.get('average_album_duration_minutes', 0.0)
        md.append(f"Analysis covers **{album_stats['total_albums']} albums** ")
        md.append(f"with an average of **{avg_tracks:.1f} tracks per album** ")
        md.append(f"and **{avg_duration:.1f} minutes average duration**.\n\n")

        # Release timeline
        if album_stats['albums_by_decade']:
            md.append("### Albums by Decade\n")
            md.append("| Decade | Album Count |\n")
            md.append("|--------|-------------|\n")
            for decade, count in sorted(album_stats['albums_by_decade'].items()):
                md.append(f"| {decade} | {count} |\n")
            md.append("\n")

        # Label Analysis
        md.append("## Record Label Analysis\n")
        label_stats = stats['label_analysis']
        md.append(
            f"The industry analysis covers **{label_stats['total_labels']} record labels** ")
        successful_percentage = (
            label_stats['successful_labels'] / label_stats['total_labels'] * 100) if label_stats['total_labels'] > 0 else 0
        md.append(
            f"with **{label_stats['successful_labels']} ({successful_percentage:.1f}%) successful labels**.\n\n")

        if label_stats['top_labels_by_success_rating']:
            md.append("### Top Record Labels by Success Rating\n")
            md.append(
                "| Rank | Label | Success Rating | Artists | Award Winners | Status |\n")
            md.append(
                "|------|-------|----------------|---------|---------------|--------|\n")
            for i, label in enumerate(label_stats['top_labels_by_success_rating'][:8], 1):
                status = "Successful" if label['is_successful'] else "Developing"
                md.append(
                    f"| {i} | {label['label_name']} | {label['success_rating']} | ")
                md.append(
                    f"{label['signed_artists_count']} | {label['award_winning_artists_count']} | {status} |\n")
            md.append("\n")

        # Business Insights
        md.append("## Business Insights & Recommendations\n")
        insights = stats['business_insights']

        # Collaboration opportunities
        if insights['collaboration_opportunities']:
            md.append("### Top Collaboration Opportunities\n")
            md.append(
                "These artists share genres but haven't collaborated yet:\n\n")
            md.append(
                "| Artist 1 | Artist 2 | Shared Genre | Potential Score |\n")
            md.append("|----------|----------|--------------|----------------|\n")
            for opp in insights['collaboration_opportunities']:
                md.append(
                    f"| {opp['artist1']} | {opp['artist2']} | {opp['shared_genre']} | {opp['potential_score']} |\n")
            md.append("\n")

        # Emerging genres
        if insights['emerging_genres']:
            md.append("### Emerging Genres\n")
            md.append("Genres showing high collaboration activity:\n\n")
            for genre in insights['emerging_genres']:
                md.append(
                    f"- **{genre['genre_name']}**: {genre['collaboration_count']} collaborations ({genre['growth_indicator']} growth)\n")
            md.append("\n")

        # Label performance insights
        if insights['label_performance_insights']:
            md.append("### Label Performance Insights\n")
            for label in insights['label_performance_insights']:
                md.append(
                    f"- **{label['label_name']}** ({label['performance_rating']}): ")
                md.append(
                    f"{label['artist_count']} artists, avg popularity {label['average_artist_popularity']:.1f} - ")
                md.append(f"*{label['recommendation']}*\n")
            md.append("\n")

        # Data Quality Assessment
        md.append("## Data Quality Assessment\n")
        quality = stats['quality_metrics']
        completeness = quality['completeness_scores']
        integrity = quality['relationship_integrity']

        md.append("### Completeness Scores\n")
        md.append("| Entity Type | Completeness Percentage |\n")
        md.append("|-------------|------------------------|\n")
        md.append(
            f"| Songs | {completeness['songs_complete_percentage']:.1f}% |\n")
        md.append(
            f"| Artists | {completeness['artists_complete_percentage']:.1f}% |\n")
        md.append(
            f"| Albums | {completeness['albums_complete_percentage']:.1f}% |\n")
        md.append("\n")

        md.append("### Relationship Integrity\n")
        md.append(f"- **Orphaned Songs**: {integrity['orphaned_songs']}\n")
        md.append(f"- **Orphaned Albums**: {integrity['orphaned_albums']}\n")
        md.append(f"- **Unsigned Artists**: {integrity['unsigned_artists']}\n")
        md.append(
            f"- **Overall Relationship Completeness**: {integrity['relationship_completeness_score']:.1f}%\n\n")

        # Technical Details
        md.append("## Technical Processing Details\n")
        md.append(
            f"- **Entities Loaded**: {overview['processing_info']['entities_loaded']}\n")
        md.append(
            f"- **Processing Time**: {overview['processing_info']['processing_time_seconds']:.2f} seconds\n")
        md.append(
            f"- **Total Inferences Made**: {overview['reasoning_results']['total_inferences']}\n")
        # md.append(
        #     f"- **Report Generated**: {overview['processing_info']['analysis_timestamp']}\n\n")

        md.append("---\n")
        md.append(
            "...")

        return "".join(md)


class MusicReasonerUsage:
    """
    Main usage interface for the Music Ontology Reasoner.
    Provides high-level methods for loading data, applying reasoning, and generating reports.
    """

    def __init__(self, data_directory: str = "./data"):
        """Initialize the music reasoner usage interface."""
        self.data_directory = data_directory
        self.reasoner = MusicReasonerEngine()
        self.analytics = None

    def run_complete_analysis(self, output_dir: str = "./") -> Dict[str, Any]:
        """
        Run complete music industry analysis pipeline.
        Loads data, applies reasoning, generates reports, and returns summary statistics.
        """
        logger.info("Starting complete music industry analysis...")

        try:
            # Ensure output directory exists
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Load CSV data
            logger.info("Loading CSV data...")
            self.reasoner.load_csv_data(self.data_directory)

            # Apply reasoning rules
            logger.info("Applying N3 reasoning rules...")
            self.reasoner.apply_reasoning_rules()

            # Initialize analytics
            self.analytics = MusicAnalytics(self.reasoner)

            # Generate reports
            logger.info("Generating comprehensive reports...")
            json_path = Path(output_dir) / "music_analysis_report.json"
            markdown_path = Path(output_dir) / "music_analysis_report.md"

            self.analytics.generate_json_report(str(json_path))
            self.analytics.generate_markdown_report(str(markdown_path))

            # Get summary statistics
            summary_stats = self.analytics.generate_comprehensive_statistics()

            logger.info("Complete analysis finished successfully!")
            logger.info(f"Reports saved to: {output_dir}")

            return {
                'status': 'success',
                'summary_statistics': summary_stats,
                'output_files': {
                    'json_report': str(json_path),
                    'markdown_report': str(markdown_path)
                },
                'diagnostics': self.reasoner.get_diagnostics()
            }

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                'status': 'error',
                'error_message': str(e),
                'diagnostics': self.reasoner.get_diagnostics() if hasattr(self, 'reasoner') else {}
            }

    def get_quick_insights(self) -> Dict[str, Any]:
        """Generate quick insights without full report generation."""
        if not self.analytics:
            self.analytics = MusicAnalytics(self.reasoner)

        return {
            'total_entities': len(self.reasoner.songs) + len(self.reasoner.artists) + len(self.reasoner.albums),
            'collaborative_songs': len(self.reasoner.collaborative_songs),
            'established_artists': len(self.reasoner.established_artists),
            'successful_labels': len(self.reasoner.successful_labels),
            'total_inferences': self.reasoner.stats['inferences_made']  # ,
            # 'processing_time': self.reasoner.stats['processing_time']
        }


def main():
    """Example usage of the Music Reasoner Usage interface."""
    # Initialize the usage interface
    usage = MusicReasonerUsage(data_directory="./data")

    # Run complete analysis
    result = usage.run_complete_analysis(output_dir="./")

    if result['status'] == 'success':
        print("Analysis completed successfully!")
        print(f"JSON Report: {result['output_files']['json_report']}")
        print(f"Markdown Report: {result['output_files']['markdown_report']}")

        # Print quick insights
        insights = usage.get_quick_insights()
        print(f"\nQuick Insights:")
        print(f"- Total Entities: {insights['total_entities']}")
        print(f"- Collaborative Songs: {insights['collaborative_songs']}")
        print(f"- Established Artists: {insights['established_artists']}")
        print(f"- Successful Labels: {insights['successful_labels']}")
        # print(f"- Processing Time: {insights['processing_time']:.2f}s")
    else:
        print(f"Analysis failed: {result['error_message']}")


if __name__ == "__main__":
    main()
