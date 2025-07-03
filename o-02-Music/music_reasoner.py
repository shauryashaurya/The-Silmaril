#!/usr/bin/env python3
"""
Music Ontology Reasoner
A comprehensive N3 ontology reasoning system for music industry data.
Implements sophisticated reasoning rules for collaboration detection, influence networks,
and success metrics across songs, artists, albums, labels, genres, and awards.
"""

import pandas as pd
import numpy as np
import logging
import json
import re
from datetime import datetime, date
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def normalize_id(value: Any) -> str:
    """
    Normalize ID values to prevent foreign key mismatches.
    Converts various numeric representations to consistent string format.
    """
    try:
        if pd.isna(value):
            return ""
        return str(int(float(value)))
    except (ValueError, TypeError):
        return str(value).strip()


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to integer with fallback."""
    try:
        if pd.isna(value):
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default


def safe_date(value: Any) -> Optional[date]:
    """Safely convert value to date object."""
    try:
        if pd.isna(value) or value == "":
            return None
        if isinstance(value, str):
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y"]:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return None
    except Exception:
        return None

# ===== ENTITY DATA MODELS =====


@dataclass
class Song:
    """Represents a musical composition with computed collaboration properties."""
    id: str
    title: str
    duration: int = 0  # seconds
    release_date: Optional[date] = None
    artist_ids: Set[str] = field(default_factory=set)
    album_ids: Set[str] = field(default_factory=set)
    genre_ids: Set[str] = field(default_factory=set)
    award_ids: Set[str] = field(default_factory=set)

    # Computed properties from reasoning
    is_collaborative: bool = False
    collaboration_count: int = 0
    primary_genre: Optional[str] = None


@dataclass
class Artist:
    """Represents a music artist with computed success and relationship metrics."""
    id: str
    name: str
    birth_date: Optional[date] = None
    nationality: str = ""
    label_id: str = ""

    # Computed properties from reasoning
    is_established: bool = False
    collaboration_partners: Set[str] = field(default_factory=set)
    collaboration_strength: Dict[str, int] = field(default_factory=dict)
    influenced_by: Set[str] = field(default_factory=set)
    influences: Set[str] = field(default_factory=set)
    popularity_score: int = 0
    award_count: int = 0
    album_count: int = 0
    contemporary_artists: Set[str] = field(default_factory=set)


@dataclass
class Album:
    """Represents a music album with inherited and computed properties."""
    id: str
    album_title: str
    release_year: int = 0
    artist_ids: Set[str] = field(default_factory=set)
    label_id: str = ""
    genre_ids: Set[str] = field(default_factory=set)
    song_ids: Set[str] = field(default_factory=set)

    # Computed properties from reasoning
    inherited_genres: Set[str] = field(default_factory=set)
    total_duration: int = 0
    track_count: int = 0
    contributors: Set[str] = field(default_factory=set)


@dataclass
class RecordLabel:
    """Represents a record label with computed success metrics."""
    id: str
    label_name: str
    location: str = ""

    # Computed properties from reasoning
    is_successful: bool = False
    signed_artists: Set[str] = field(default_factory=set)
    success_rating: int = 0
    award_winning_artists: Set[str] = field(default_factory=set)


@dataclass
class Genre:
    """Represents a music genre with relationship properties."""
    id: str
    genre_name: str
    description: str = ""

    # Computed properties from reasoning
    related_genres: Set[str] = field(default_factory=set)
    artist_count: int = 0
    song_count: int = 0
    album_count: int = 0


@dataclass
class Award:
    """Represents a music industry award."""
    id: str
    award_name: str
    year: int = 0
    awarding_body: str = ""
    artist_ids: Set[str] = field(default_factory=set)
    song_ids: Set[str] = field(default_factory=set)


class MusicReasonerEngine:
    """
    Core reasoning engine for music industry ontology.
    Implements N3 reasoning rules for collaboration detection, influence networks,
    success metrics, and temporal relationships.
    """

    def __init__(self):
        """Initialize the reasoning engine with empty knowledge base."""
        # Core entity stores
        self.songs: Dict[str, Song] = {}
        self.artists: Dict[str, Artist] = {}
        self.albums: Dict[str, Album] = {}
        self.record_labels: Dict[str, RecordLabel] = {}
        self.genres: Dict[str, Genre] = {}
        self.awards: Dict[str, Award] = {}

        # Derived knowledge structures (populated by reasoning)
        self.collaborative_songs: Set[str] = set()
        self.successful_labels: Set[str] = set()
        self.established_artists: Set[str] = set()
        self.collaboration_network: Dict[str,
                                         Dict[str, int]] = defaultdict(dict)
        self.influence_network: Dict[str, Set[str]] = defaultdict(set)
        self.genre_similarity_map: Dict[str, Set[str]] = defaultdict(set)

        # Processing statistics
        self.stats = {
            'entities_loaded': 0,
            'rules_executed': 0,
            'inferences_made': 0,
            'processing_time': 0.0
        }

    def load_csv_data(self, data_dir: str) -> None:
        """
        Load music industry data from CSV files with robust ID normalization.
        Expected files: songs.csv, artists.csv, albums.csv, record_labels.csv, 
        genres.csv, awards.csv, and relationship junction tables.
        """
        data_path = Path(data_dir)
        logger.info(f"Loading CSV data from {data_path}")

        try:
            # Load core entities
            self._load_songs(data_path)
            self._load_artists(data_path)
            self._load_albums(data_path)
            self._load_record_labels(data_path)
            self._load_genres(data_path)
            self._load_awards(data_path)

            # Load relationships
            self._load_relationships(data_path)

            # Validate data integrity
            self._validate_data_integrity()

            logger.info(
                f"Successfully loaded {self.stats['entities_loaded']} entities")

        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            raise

    def _load_songs(self, data_path: Path) -> None:
        """Load songs from CSV with ID normalization."""
        songs_file = data_path / "songs.csv"
        if not songs_file.exists():
            logger.warning(f"Songs file not found: {songs_file}")
            return

        df = pd.read_csv(songs_file)
        logger.info(f"Loading {len(df)} songs from {songs_file}")

        # Normalize ID column
        df['id'] = df['id'].apply(normalize_id)

        for row in df.itertuples(index=False, name=None):
            song_id = normalize_id(row[0])  # id
            if not song_id:
                continue

            song = Song(
                id=song_id,
                title=str(row[1]) if pd.notna(row[1]) else "",  # title
                duration=safe_int(row[2]) if len(row) > 2 else 0,  # duration
                release_date=safe_date(row[3]) if len(
                    row) > 3 else None  # release_date
            )

            self.songs[song_id] = song
            self.stats['entities_loaded'] += 1

    def _load_artists(self, data_path: Path) -> None:
        """Load artists from CSV with ID normalization."""
        artists_file = data_path / "artists.csv"
        if not artists_file.exists():
            logger.warning(f"Artists file not found: {artists_file}")
            return

        df = pd.read_csv(artists_file)
        logger.info(f"Loading {len(df)} artists from {artists_file}")

        # Normalize ID columns
        df['id'] = df['id'].apply(normalize_id)
        if 'label_id' in df.columns:
            df['label_id'] = df['label_id'].apply(normalize_id)

        for row in df.itertuples(index=False, name=None):
            artist_id = normalize_id(row[0])  # id
            if not artist_id:
                continue

            artist = Artist(
                id=artist_id,
                name=str(row[1]) if pd.notna(row[1]) else "",  # name
                birth_date=safe_date(row[2]) if len(
                    row) > 2 else None,  # birth_date
                nationality=str(row[3]) if len(row) > 3 and pd.notna(
                    row[3]) else "",  # nationality
                label_id=normalize_id(row[4]) if len(
                    row) > 4 else ""  # label_id
            )

            self.artists[artist_id] = artist
            self.stats['entities_loaded'] += 1

    def _load_albums(self, data_path: Path) -> None:
        """Load albums from CSV with ID normalization."""
        albums_file = data_path / "albums.csv"
        if not albums_file.exists():
            logger.warning(f"Albums file not found: {albums_file}")
            return

        df = pd.read_csv(albums_file)
        logger.info(f"Loading {len(df)} albums from {albums_file}")

        # Normalize ID columns
        df['id'] = df['id'].apply(normalize_id)
        if 'label_id' in df.columns:
            df['label_id'] = df['label_id'].apply(normalize_id)

        for row in df.itertuples(index=False, name=None):
            album_id = normalize_id(row[0])  # id
            if not album_id:
                continue

            album = Album(
                id=album_id,
                album_title=str(row[1]) if pd.notna(
                    row[1]) else "",  # album_title
                release_year=safe_int(row[2]) if len(
                    row) > 2 else 0,  # release_year
                label_id=normalize_id(row[3]) if len(
                    row) > 3 else ""  # label_id
            )

            self.albums[album_id] = album
            self.stats['entities_loaded'] += 1

    def _load_record_labels(self, data_path: Path) -> None:
        """Load record labels from CSV with ID normalization."""
        labels_file = data_path / "record_labels.csv"
        if not labels_file.exists():
            logger.warning(f"Record labels file not found: {labels_file}")
            return

        df = pd.read_csv(labels_file)
        logger.info(f"Loading {len(df)} record labels from {labels_file}")

        df['id'] = df['id'].apply(normalize_id)

        for row in df.itertuples(index=False, name=None):
            label_id = normalize_id(row[0])  # id
            if not label_id:
                continue

            label = RecordLabel(
                id=label_id,
                label_name=str(row[1]) if pd.notna(
                    row[1]) else "",  # label_name
                location=str(row[2]) if len(row) > 2 and pd.notna(
                    row[2]) else ""  # location
            )

            self.record_labels[label_id] = label
            self.stats['entities_loaded'] += 1

    def _load_genres(self, data_path: Path) -> None:
        """Load genres from CSV with ID normalization."""
        genres_file = data_path / "genres.csv"
        if not genres_file.exists():
            logger.warning(f"Genres file not found: {genres_file}")
            return

        df = pd.read_csv(genres_file)
        logger.info(f"Loading {len(df)} genres from {genres_file}")

        df['id'] = df['id'].apply(normalize_id)

        for row in df.itertuples(index=False, name=None):
            genre_id = normalize_id(row[0])  # id
            if not genre_id:
                continue

            genre = Genre(
                id=genre_id,
                genre_name=str(row[1]) if pd.notna(
                    row[1]) else "",  # genre_name
                description=str(row[2]) if len(row) > 2 and pd.notna(
                    row[2]) else ""  # description
            )

            self.genres[genre_id] = genre
            self.stats['entities_loaded'] += 1

    def _load_awards(self, data_path: Path) -> None:
        """Load awards from CSV with ID normalization."""
        awards_file = data_path / "awards.csv"
        if not awards_file.exists():
            logger.warning(f"Awards file not found: {awards_file}")
            return

        df = pd.read_csv(awards_file)
        logger.info(f"Loading {len(df)} awards from {awards_file}")

        df['id'] = df['id'].apply(normalize_id)

        for row in df.itertuples(index=False, name=None):
            award_id = normalize_id(row[0])  # id
            if not award_id:
                continue

            award = Award(
                id=award_id,
                award_name=str(row[1]) if pd.notna(
                    row[1]) else "",  # award_name
                year=safe_int(row[2]) if len(row) > 2 else 0,  # year
                awarding_body=str(row[3]) if len(row) > 3 and pd.notna(
                    row[3]) else ""  # awarding_body
            )

            self.awards[award_id] = award
            self.stats['entities_loaded'] += 1

    def _load_relationships(self, data_path: Path) -> None:
        """Load relationship data from junction tables."""
        logger.info("Loading relationship data from junction tables")

        # Song-Artist relationships
        self._load_song_artists(data_path)

        # Song-Genre relationships
        self._load_song_genres(data_path)

        # Song-Album relationships
        self._load_song_albums(data_path)

        # Album-Artist relationships
        self._load_album_artists(data_path)

        # Album-Genre relationships
        self._load_album_genres(data_path)

        # Artist-Award relationships
        self._load_artist_awards(data_path)

        # Song-Award relationships
        self._load_song_awards(data_path)

        # Update label relationships based on artist associations
        self._update_label_relationships()

    def _load_song_artists(self, data_path: Path) -> None:
        """Load song-artist relationships."""
        file_path = data_path / "song_artists.csv"
        if not file_path.exists():
            logger.warning(f"Song-artists file not found: {file_path}")
            return

        df = pd.read_csv(file_path)
        df['song_id'] = df['song_id'].apply(normalize_id)
        df['artist_id'] = df['artist_id'].apply(normalize_id)

        for _, row in df.iterrows():
            song_id = normalize_id(row['song_id'])
            artist_id = normalize_id(row['artist_id'])

            if song_id in self.songs and artist_id in self.artists:
                self.songs[song_id].artist_ids.add(artist_id)

    def _load_song_genres(self, data_path: Path) -> None:
        """Load song-genre relationships."""
        file_path = data_path / "song_genres.csv"
        if not file_path.exists():
            logger.warning(f"Song-genres file not found: {file_path}")
            return

        df = pd.read_csv(file_path)
        df['song_id'] = df['song_id'].apply(normalize_id)
        df['genre_id'] = df['genre_id'].apply(normalize_id)

        for _, row in df.iterrows():
            song_id = normalize_id(row['song_id'])
            genre_id = normalize_id(row['genre_id'])

            if song_id in self.songs and genre_id in self.genres:
                self.songs[song_id].genre_ids.add(genre_id)

    def _load_song_albums(self, data_path: Path) -> None:
        """Load song-album relationships."""
        file_path = data_path / "song_albums.csv"
        if not file_path.exists():
            logger.warning(f"Song-albums file not found: {file_path}")
            return

        df = pd.read_csv(file_path)
        df['song_id'] = df['song_id'].apply(normalize_id)
        df['album_id'] = df['album_id'].apply(normalize_id)

        for _, row in df.iterrows():
            song_id = normalize_id(row['song_id'])
            album_id = normalize_id(row['album_id'])

            if song_id in self.songs and album_id in self.albums:
                self.songs[song_id].album_ids.add(album_id)
                self.albums[album_id].song_ids.add(song_id)

    def _load_album_artists(self, data_path: Path) -> None:
        """Load album-artist relationships."""
        file_path = data_path / "album_artists.csv"
        if not file_path.exists():
            logger.warning(f"Album-artists file not found: {file_path}")
            return

        df = pd.read_csv(file_path)
        df['album_id'] = df['album_id'].apply(normalize_id)
        df['artist_id'] = df['artist_id'].apply(normalize_id)

        for _, row in df.iterrows():
            album_id = normalize_id(row['album_id'])
            artist_id = normalize_id(row['artist_id'])

            if album_id in self.albums and artist_id in self.artists:
                self.albums[album_id].artist_ids.add(artist_id)

    def _load_album_genres(self, data_path: Path) -> None:
        """Load album-genre relationships."""
        file_path = data_path / "album_genres.csv"
        if not file_path.exists():
            logger.warning(f"Album-genres file not found: {file_path}")
            return

        df = pd.read_csv(file_path)
        df['album_id'] = df['album_id'].apply(normalize_id)
        df['genre_id'] = df['genre_id'].apply(normalize_id)

        for _, row in df.iterrows():
            album_id = normalize_id(row['album_id'])
            genre_id = normalize_id(row['genre_id'])

            if album_id in self.albums and genre_id in self.genres:
                self.albums[album_id].genre_ids.add(genre_id)

    def _load_artist_awards(self, data_path: Path) -> None:
        """Load artist-award relationships."""
        file_path = data_path / "artist_awards.csv"
        if not file_path.exists():
            logger.warning(f"Artist-awards file not found: {file_path}")
            return

        df = pd.read_csv(file_path)
        df['artist_id'] = df['artist_id'].apply(normalize_id)
        df['award_id'] = df['award_id'].apply(normalize_id)

        for _, row in df.iterrows():
            artist_id = normalize_id(row['artist_id'])
            award_id = normalize_id(row['award_id'])

            if artist_id in self.artists and award_id in self.awards:
                self.awards[award_id].artist_ids.add(artist_id)

    def _load_song_awards(self, data_path: Path) -> None:
        """Load song-award relationships."""
        file_path = data_path / "song_awards.csv"
        if not file_path.exists():
            logger.warning(f"Song-awards file not found: {file_path}")
            return

        df = pd.read_csv(file_path)
        df['song_id'] = df['song_id'].apply(normalize_id)
        df['award_id'] = df['award_id'].apply(normalize_id)

        for _, row in df.iterrows():
            song_id = normalize_id(row['song_id'])
            award_id = normalize_id(row['award_id'])

            if song_id in self.songs and award_id in self.awards:
                self.awards[award_id].song_ids.add(song_id)
                self.songs[song_id].award_ids.add(award_id)

    def _update_label_relationships(self) -> None:
        """Update record label relationships based on artist associations."""
        for artist in self.artists.values():
            if artist.label_id and artist.label_id in self.record_labels:
                self.record_labels[artist.label_id].signed_artists.add(
                    artist.id)

    def _validate_data_integrity(self) -> None:
        """Comprehensive validation of loaded data integrity."""
        logger.info("Validating data integrity...")

        issues = []

        # Check song-artist relationships
        orphaned_songs = 0
        for song in self.songs.values():
            if not song.artist_ids:
                orphaned_songs += 1
            for artist_id in song.artist_ids:
                if artist_id not in self.artists:
                    issues.append(
                        f"Song {song.id} references missing artist {artist_id}")

        if orphaned_songs > 0:
            logger.warning(f"Found {orphaned_songs} songs without artists")

        # Check album relationships
        for album in self.albums.values():
            for artist_id in album.artist_ids:
                if artist_id not in self.artists:
                    issues.append(
                        f"Album {album.id} references missing artist {artist_id}")
            for song_id in album.song_ids:
                if song_id not in self.songs:
                    issues.append(
                        f"Album {album.id} references missing song {song_id}")

        # Check genre relationships
        for song in self.songs.values():
            for genre_id in song.genre_ids:
                if genre_id not in self.genres:
                    issues.append(
                        f"Song {song.id} references missing genre {genre_id}")

        for album in self.albums.values():
            for genre_id in album.genre_ids:
                if genre_id not in self.genres:
                    issues.append(
                        f"Album {album.id} references missing genre {genre_id}")

        # Check label relationships
        for artist in self.artists.values():
            if artist.label_id and artist.label_id not in self.record_labels:
                issues.append(
                    f"Artist {artist.id} references missing label {artist.label_id}")

        # Report validation results
        if issues:
            logger.error(f"Found {len(issues)} data integrity issues:")
            for issue in issues[:10]:  # Show first 10 issues
                logger.error(f"  {issue}")
            if len(issues) > 10:
                logger.error(f"  ... and {len(issues) - 10} more issues")
        else:
            logger.info("Data integrity validation passed - no issues found")

    def apply_reasoning_rules(self) -> None:
        """
        Apply all N3 reasoning rules in logical sequence.
        Rules are executed in categories for optimal performance and dependency management.
        """
        start_time = datetime.now()
        logger.info("Starting reasoning rule application...")

        try:
            # Category 1: Basic classification rules
            self._rule_01_collaboration_detection()
            self._rule_02_genre_inheritance()
            self._rule_07_contribution_inference()

            # Category 2: Success and establishment rules
            self._rule_03_label_success_inference()
            self._rule_04_artist_establishment()

            # Category 3: Relationship and influence rules
            self._rule_05_transitivity_influence()
            self._rule_06_genre_based_influence()

            # Category 4: Quantitative analysis rules
            self._rule_08_collaboration_strength()
            self._rule_09_popularity_score()
            self._rule_10_label_success_rating()

            # Category 5: String and temporal analysis
            self._rule_11_genre_similarity()
            self._rule_12_contemporary_artists()

            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.stats['processing_time'] = processing_time

            logger.info(
                f"Reasoning completed in {processing_time:.2f} seconds")
            logger.info(
                f"Total inferences made: {self.stats['inferences_made']}")

        except Exception as e:
            logger.error(f"Error during reasoning: {e}")
            raise

    def _rule_01_collaboration_detection(self) -> None:
        """
        N3 Rule: Collaboration Detection
        If two different artists perform the same song, they collaborate.
        This creates implicit collaboration relationships and identifies collaborative songs.
        """
        logger.info("Applying Rule 01: Collaboration Detection")
        collaborations_found = 0

        for song in self.songs.values():
            if len(song.artist_ids) > 1:
                # Mark song as collaborative
                song.is_collaborative = True
                song.collaboration_count = len(song.artist_ids)
                self.collaborative_songs.add(song.id)

                # Create collaboration relationships between all artist pairs
                artist_list = list(song.artist_ids)
                for i in range(len(artist_list)):
                    for j in range(i + 1, len(artist_list)):
                        artist1_id = artist_list[i]
                        artist2_id = artist_list[j]

                        if artist1_id in self.artists and artist2_id in self.artists:
                            # Add bidirectional collaboration
                            self.artists[artist1_id].collaboration_partners.add(
                                artist2_id)
                            self.artists[artist2_id].collaboration_partners.add(
                                artist1_id)

                            # Initialize collaboration network
                            if artist1_id not in self.collaboration_network:
                                self.collaboration_network[artist1_id] = {}
                            if artist2_id not in self.collaboration_network:
                                self.collaboration_network[artist2_id] = {}

                            # Count collaborations
                            self.collaboration_network[artist1_id][artist2_id] = \
                                self.collaboration_network[artist1_id].get(
                                    artist2_id, 0) + 1
                            self.collaboration_network[artist2_id][artist1_id] = \
                                self.collaboration_network[artist2_id].get(
                                    artist1_id, 0) + 1

                            collaborations_found += 1

        self.stats['inferences_made'] += collaborations_found
        logger.info(
            f"Found {collaborations_found} collaboration relationships")
        logger.info(
            f"Identified {len(self.collaborative_songs)} collaborative songs")

    def _rule_02_genre_inheritance(self) -> None:
        """
        N3 Rule: Genre Inheritance
        Albums inherit genres from their constituent songs when there's consensus.
        This propagates song-level genre data to album-level classification.
        """
        logger.info("Applying Rule 02: Genre Inheritance")
        inheritances_made = 0

        for album in self.albums.values():
            if not album.song_ids:
                continue

            # Count genre occurrences across album songs
            genre_counts = Counter()
            for song_id in album.song_ids:
                if song_id in self.songs:
                    song = self.songs[song_id]
                    for genre_id in song.genre_ids:
                        genre_counts[genre_id] += 1

            # Inherit genres that appear in multiple songs (consensus rule)
            song_count = len(album.song_ids)
            # At least 2 songs or 1/3 of songs
            consensus_threshold = max(2, song_count // 3)

            for genre_id, count in genre_counts.items():
                if count >= consensus_threshold and genre_id not in album.genre_ids:
                    album.inherited_genres.add(genre_id)
                    album.genre_ids.add(genre_id)
                    inheritances_made += 1

        self.stats['inferences_made'] += inheritances_made
        logger.info(f"Made {inheritances_made} genre inheritance inferences")

    def _rule_03_label_success_inference(self) -> None:
        """
        N3 Rule: Label Success Inference
        Labels with multiple award-winning artists are classified as successful.
        This automatically categorizes labels based on artist achievements.
        """
        logger.info("Applying Rule 03: Label Success Inference")
        successful_labels_found = 0

        for label in self.record_labels.values():
            award_winning_artists = set()

            # Find artists with awards signed to this label
            for artist in self.artists.values():
                if artist.label_id == label.id:
                    # Check if artist has any awards
                    artist_has_awards = any(
                        artist.id in award.artist_ids for award in self.awards.values()
                    )
                    if artist_has_awards:
                        award_winning_artists.add(artist.id)

            # Label is successful if it has multiple award-winning artists
            if len(award_winning_artists) >= 2:
                label.is_successful = True
                label.award_winning_artists = award_winning_artists
                self.successful_labels.add(label.id)
                successful_labels_found += 1

        self.stats['inferences_made'] += successful_labels_found
        logger.info(f"Identified {successful_labels_found} successful labels")

    def _rule_04_artist_establishment(self) -> None:
        """
        N3 Rule: Artist Establishment
        Artists with multiple albums and awards are established.
        This models career progression and artist maturity automatically.
        """
        logger.info("Applying Rule 04: Artist Establishment")
        established_artists_found = 0

        for artist in self.artists.values():
            # Count albums by this artist
            album_count = sum(1 for album in self.albums.values()
                              if artist.id in album.artist_ids)
            artist.album_count = album_count

            # Count awards won by this artist
            award_count = sum(1 for award in self.awards.values()
                              if artist.id in award.artist_ids)
            artist.award_count = award_count

            # Artist is established if they have multiple albums AND at least one award
            if album_count >= 2 and award_count >= 1:
                artist.is_established = True
                self.established_artists.add(artist.id)
                established_artists_found += 1

        self.stats['inferences_made'] += established_artists_found
        logger.info(
            f"Identified {established_artists_found} established artists")

    def _rule_05_transitivity_influence(self) -> None:
        """
        N3 Rule: Transitivity for Influence
        If Artist A influences B and B influences C, then A influences C.
        This creates transitive influence chains through the collaboration network.
        """
        logger.info("Applying Rule 05: Transitivity for Influence")
        transitive_influences = 0

        # Apply transitive closure on influence relationships
        # Use Floyd-Warshall-like algorithm for transitive closure
        all_artists = list(self.artists.keys())

        # Initialize direct influence relationships
        for artist_id in all_artists:
            if artist_id not in self.influence_network:
                self.influence_network[artist_id] = set()

        # Apply transitivity (limit iterations to prevent infinite loops)
        max_iterations = 3
        for iteration in range(max_iterations):
            new_influences = 0

            for artist1 in all_artists:
                for artist2 in list(self.influence_network[artist1]):
                    for artist3 in list(self.influence_network[artist2]):
                        if (artist3 != artist1 and
                                artist3 not in self.influence_network[artist1]):
                            self.influence_network[artist1].add(artist3)
                            self.artists[artist1].influenced_by.add(artist3)
                            self.artists[artist3].influences.add(artist1)
                            new_influences += 1
                            transitive_influences += 1

            if new_influences == 0:
                break

        self.stats['inferences_made'] += transitive_influences
        logger.info(
            f"Created {transitive_influences} transitive influence relationships")

    def _rule_06_genre_based_influence(self) -> None:
        """
        N3 Rule: Genre-based Influence
        Artists sharing genres and collaborating are mutually influential.
        This creates influence relationships based on musical collaboration and genre similarity.
        """
        logger.info("Applying Rule 06: Genre-based Influence")
        genre_influences = 0

        for artist1 in self.artists.values():
            for artist2_id in artist1.collaboration_partners:
                if artist2_id in self.artists:
                    artist2 = self.artists[artist2_id]

                    # Find shared genres through songs
                    artist1_genres = set()
                    artist2_genres = set()

                    # Collect genres from songs performed by each artist
                    for song in self.songs.values():
                        if artist1.id in song.artist_ids:
                            artist1_genres.update(song.genre_ids)
                        if artist2.id in song.artist_ids:
                            artist2_genres.update(song.genre_ids)

                    # If they share genres, they influence each other
                    shared_genres = artist1_genres & artist2_genres
                    if shared_genres:
                        # Bidirectional influence
                        if artist2.id not in artist1.influenced_by:
                            artist1.influenced_by.add(artist2.id)
                            artist2.influences.add(artist1.id)
                            self.influence_network[artist1.id].add(artist2.id)
                            genre_influences += 1

                        if artist1.id not in artist2.influenced_by:
                            artist2.influenced_by.add(artist1.id)
                            artist1.influences.add(artist2.id)
                            self.influence_network[artist2.id].add(artist1.id)
                            genre_influences += 1

        self.stats['inferences_made'] += genre_influences
        logger.info(
            f"Created {genre_influences} genre-based influence relationships")

    def _rule_07_contribution_inference(self) -> None:
        """
        N3 Rule: Contribution Inference
        Any entity (artist, label) connected to an album is a contributor.
        This creates a unified view of album contributors regardless of their role.
        """
        logger.info("Applying Rule 07: Contribution Inference")
        contributions_found = 0

        for album in self.albums.values():
            # Artists are contributors
            for artist_id in album.artist_ids:
                if artist_id in self.artists:
                    album.contributors.add(artist_id)
                    contributions_found += 1

            # Label is contributor
            if album.label_id and album.label_id in self.record_labels:
                album.contributors.add(album.label_id)
                contributions_found += 1

        self.stats['inferences_made'] += contributions_found
        logger.info(
            f"Identified {contributions_found} contribution relationships")

    def _rule_08_collaboration_strength(self) -> None:
        """
        N3 Rule: Collaboration Strength Calculation
        Count how many songs two artists have performed together.
        This quantifies the strength of collaboration relationships.
        """
        logger.info("Applying Rule 08: Collaboration Strength Calculation")

        for artist in self.artists.values():
            for partner_id, strength in self.collaboration_network.get(artist.id, {}).items():
                artist.collaboration_strength[partner_id] = strength

        logger.info("Collaboration strength calculations completed")

    def _rule_09_popularity_score(self) -> None:
        """
        N3 Rule: Popularity Score Calculation
        Combine award count and collaboration count for popularity metric.
        Formula: (award_count * 5) + (collaboration_count * 2)
        """
        logger.info("Applying Rule 09: Popularity Score Calculation")

        for artist in self.artists.values():
            collaboration_count = len(artist.collaboration_partners)
            award_count = artist.award_count

            # Weight awards more heavily than collaborations
            popularity_score = (award_count * 5) + (collaboration_count * 2)
            artist.popularity_score = popularity_score

        logger.info("Popularity score calculations completed")

    def _rule_10_label_success_rating(self) -> None:
        """
        N3 Rule: Label Success Rating
        Calculate success rating based on signed artists' achievements.
        Aggregates popularity scores of all signed artists.
        """
        logger.info("Applying Rule 10: Label Success Rating")

        for label in self.record_labels.values():
            total_score = 0
            artist_count = 0

            for artist_id in label.signed_artists:
                if artist_id in self.artists:
                    total_score += self.artists[artist_id].popularity_score
                    artist_count += 1

            # Average popularity score of signed artists
            label.success_rating = total_score // max(
                1, artist_count) if artist_count > 0 else 0

        logger.info("Label success rating calculations completed")

    def _rule_11_genre_similarity(self) -> None:
        """
        N3 Rule: Genre Similarity Detection
        Find genres with similar names using string matching.
        This identifies related genres like "Rock" and "Folk Rock".
        """
        logger.info("Applying Rule 11: Genre Similarity Detection")
        similarities_found = 0

        genre_names = {genre.id: genre.genre_name.lower()
                       for genre in self.genres.values()}

        for genre1_id, name1 in genre_names.items():
            for genre2_id, name2 in genre_names.items():
                if genre1_id != genre2_id:
                    # Check if one name contains the other
                    if name1 in name2 or name2 in name1:
                        self.genre_similarity_map[genre1_id].add(genre2_id)
                        self.genres[genre1_id].related_genres.add(genre2_id)
                        similarities_found += 1

        self.stats['inferences_made'] += similarities_found
        logger.info(f"Found {similarities_found} genre similarities")

    def _rule_12_contemporary_artists(self) -> None:
        """
        N3 Rule: Contemporary Artists
        Artists releasing albums in the same decade are contemporaries.
        This creates temporal clusters of artists based on release patterns.
        """
        logger.info("Applying Rule 12: Contemporary Artists")
        contemporary_pairs = 0

        # Group artists by decade of album releases
        artist_decades = defaultdict(set)

        for album in self.albums.values():
            if album.release_year > 0:
                decade = album.release_year // 10
                for artist_id in album.artist_ids:
                    artist_decades[decade].add(artist_id)

        # Create contemporary relationships within each decade
        for decade, artist_ids in artist_decades.items():
            artist_list = list(artist_ids)
            for i in range(len(artist_list)):
                for j in range(i + 1, len(artist_list)):
                    artist1_id = artist_list[i]
                    artist2_id = artist_list[j]

                    if artist1_id in self.artists and artist2_id in self.artists:
                        self.artists[artist1_id].contemporary_artists.add(
                            artist2_id)
                        self.artists[artist2_id].contemporary_artists.add(
                            artist1_id)
                        contemporary_pairs += 1

        self.stats['inferences_made'] += contemporary_pairs
        logger.info(
            f"Identified {contemporary_pairs} contemporary artist relationships")

    def get_diagnostics(self) -> Dict[str, Any]:
        """Generate comprehensive diagnostic information about the knowledge base."""
        diagnostics = {
            'entity_counts': {
                'songs': len(self.songs),
                'artists': len(self.artists),
                'albums': len(self.albums),
                'record_labels': len(self.record_labels),
                'genres': len(self.genres),
                'awards': len(self.awards)
            },
            'reasoning_results': {
                'collaborative_songs': len(self.collaborative_songs),
                'successful_labels': len(self.successful_labels),
                'established_artists': len(self.established_artists),
                'total_collaborations': sum(len(partners) for partners in self.collaboration_network.values()) // 2,
                'total_influences': sum(len(influences) for influences in self.influence_network.values()),
                'genre_similarities': sum(len(similar) for similar in self.genre_similarity_map.values())
            },
            'statistics': self.stats.copy(),
            'data_quality': self._get_data_quality_metrics()
        }

        return diagnostics

    def _get_data_quality_metrics(self) -> Dict[str, Any]:
        """Calculate data quality metrics for validation."""
        metrics = {}

        # Song quality metrics
        songs_with_artists = sum(
            1 for song in self.songs.values() if song.artist_ids)
        songs_with_genres = sum(
            1 for song in self.songs.values() if song.genre_ids)
        songs_with_duration = sum(
            1 for song in self.songs.values() if song.duration > 0)

        metrics['song_completeness'] = {
            'with_artists': f"{songs_with_artists}/{len(self.songs)}",
            'with_genres': f"{songs_with_genres}/{len(self.songs)}",
            'with_duration': f"{songs_with_duration}/{len(self.songs)}"
        }

        # Artist quality metrics
        artists_with_labels = sum(
            1 for artist in self.artists.values() if artist.label_id)
        artists_with_birth_dates = sum(
            1 for artist in self.artists.values() if artist.birth_date)

        metrics['artist_completeness'] = {
            'with_labels': f"{artists_with_labels}/{len(self.artists)}",
            'with_birth_dates': f"{artists_with_birth_dates}/{len(self.artists)}"
        }

        # Relationship density
        total_possible_collaborations = len(
            self.artists) * (len(self.artists) - 1) // 2
        actual_collaborations = sum(
            len(partners) for partners in self.collaboration_network.values()) // 2

        if total_possible_collaborations > 0:
            collaboration_density = actual_collaborations / total_possible_collaborations
            metrics['collaboration_density'] = f"{collaboration_density:.4f}"

        return metrics


def main():
    """Example usage of the Music Reasoner Engine."""
    # Initialize the reasoner
    reasoner = MusicReasonerEngine()

    # Load data (assuming CSV files exist in ./data directory)
    try:
        reasoner.load_csv_data("./data")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return

    # Apply reasoning rules
    try:
        reasoner.apply_reasoning_rules()
    except Exception as e:
        logger.error(f"Failed to apply reasoning: {e}")
        return

    # Get diagnostics
    diagnostics = reasoner.get_diagnostics()
    logger.info("Reasoning completed successfully")
    logger.info(
        f"Final diagnostics: {json.dumps(diagnostics, indent=2, default=str)}")


if __name__ == "__main__":
    main()
