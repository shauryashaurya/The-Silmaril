"""
Music Ontology Reasoner - Corrected Relationship Computation Order
A comprehensive N3 ontology reasoning system for music industry data.

CRITICAL DESIGN PRINCIPLE:
- INVERSE RELATIONSHIPS must be computed BEFORE derived relationships
- Songs are the central hub connecting all entities
- Two-phase relationship computation prevents dependency issues
"""

import pandas as pd
import numpy as np
import logging
import json
import re
import ast
from datetime import datetime, date
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from pathlib import Path

# Configure logging
logging.basicConfig(
    filename='./music_reasoner.log',
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


def parse_id_list(value: Any) -> Set[str]:
    """
    Parse string representation of ID list into set of normalized IDs.
    Handles formats like: "['artist_97', 'artist_91']", "[]", None, NaN
    """
    if pd.isna(value) or value == "" or value is None:
        return set()

    try:
        # Convert to string and clean up
        str_value = str(value).strip()

        # Handle empty list representations
        if str_value in ["[]", "['']", '[""]', "null", "None"]:
            return set()

        # Try to parse as Python literal (most common case)
        try:
            parsed_list = ast.literal_eval(str_value)
            if isinstance(parsed_list, list):
                # Normalize all IDs in the list
                return {normalize_id(item) for item in parsed_list if item and str(item).strip()}
            else:
                # Single value, not a list
                normalized = normalize_id(parsed_list)
                return {normalized} if normalized else set()
        except (ValueError, SyntaxError):
            pass

        # Try manual parsing for malformed strings
        # Remove brackets and quotes, split by comma
        cleaned = str_value.strip("[]\"'")
        if not cleaned:
            return set()

        # Split by comma and clean each item
        items = [item.strip().strip("\"'") for item in cleaned.split(",")]
        normalized_items = {normalize_id(item)
                            for item in items if item and item.strip()}
        return normalized_items

    except Exception as e:
        logger.warning(f"Failed to parse ID list '{value}': {e}")
        return set()

# ===== ENTITY DATA MODELS =====


@dataclass
class Song:
    """
    Represents a musical composition - the central hub connecting all other entities.
    Songs contain DIRECT relationships loaded from CSV embedded lists.
    """
    id: str
    title: str
    duration: int = 0  # seconds
    release_date: Optional[date] = None

    # DIRECT RELATIONSHIPS (loaded from embedded lists in songs CSV)
    artist_ids: Set[str] = field(default_factory=set)  # from artistIDs column
    album_ids: Set[str] = field(default_factory=set)   # from albumIDs column
    genre_ids: Set[str] = field(default_factory=set)   # from genreIDs column
    award_ids: Set[str] = field(default_factory=set)   # from awardIDs column

    # COMPUTED PROPERTIES (populated by reasoning rules)
    is_collaborative: bool = False
    collaboration_count: int = 0
    primary_genre: Optional[str] = None

    def validate_cardinality(self) -> List[str]:
        """Validate cardinality constraints for Song."""
        violations = []
        if len(self.artist_ids) == 0:
            violations.append(
                f"Song {self.id} '{self.title}' violates minCardinality 1 for performedBy")
        if len(self.genre_ids) == 0:
            violations.append(
                f"Song {self.id} '{self.title}' violates minCardinality 1 for hasGenre")
        return violations


@dataclass
class Artist:
    """
    Represents a music artist with computed success and relationship metrics.
    Artist relationships are DERIVED from songs (except label_id which is direct).
    """
    id: str
    name: str
    birth_date: Optional[date] = None
    nationality: str = ""

    # DIRECT RELATIONSHIP (from artists CSV)
    label_id: str = ""  # signedTo (maxCardinality 1) - from labelID column

    # INVERSE RELATIONSHIPS (computed from songs in PHASE 1)
    performed_song_ids: Set[str] = field(
        default_factory=set)      # inverse of song.performedBy

    # DERIVED RELATIONSHIPS (computed from inverse relationships in PHASE 2)
    released_album_ids: Set[str] = field(
        default_factory=set)      # computed from songs->albums
    # computed from songs->awards
    won_award_ids: Set[str] = field(default_factory=set)

    # COMPUTED PROPERTIES (populated by reasoning rules)
    is_established: bool = False
    collaboration_partners: Set[str] = field(default_factory=set)
    collaboration_strength: Dict[str, int] = field(default_factory=dict)
    influenced_by: Set[str] = field(default_factory=set)
    influences: Set[str] = field(default_factory=set)
    popularity_score: int = 0
    award_count: int = 0
    album_count: int = 0
    contemporary_artists: Set[str] = field(default_factory=set)

    def validate_cardinality(self) -> List[str]:
        """Validate cardinality constraints for Artist."""
        violations = []
        # Artist can have at most one label (maxCardinality 1)
        # This is automatically enforced by using a single string field
        return violations


@dataclass
class Album:
    """
    Represents a music album with inherited and computed properties.
    Album relationships are MOSTLY DERIVED from songs (except genreIDs which is direct).
    """
    id: str
    album_title: str
    release_year: int = 0

    # DIRECT RELATIONSHIPS (only genreIDs from albums CSV)
    # from genreIDs column in albums.csv
    genre_ids: Set[str] = field(default_factory=set)

    # INVERSE RELATIONSHIPS (computed from songs in PHASE 1)
    # inverse of song.featuredOn
    song_ids: Set[str] = field(default_factory=set)

    # DERIVED RELATIONSHIPS (computed from inverse relationships in PHASE 2)
    # computed from songs->artists
    artist_ids: Set[str] = field(default_factory=set)
    label_id: str = ""                                  # computed from artist labels

    # COMPUTED PROPERTIES (populated by reasoning rules)
    inherited_genres: Set[str] = field(default_factory=set)
    total_duration: int = 0
    track_count: int = 0
    contributors: Set[str] = field(default_factory=set)

    def validate_cardinality(self) -> List[str]:
        """Validate cardinality constraints for Album."""
        violations = []
        if len(self.artist_ids) == 0:
            violations.append(
                f"Album {self.id} '{self.album_title}' violates minCardinality 1 for releasedByArtist")
        if not self.label_id:
            violations.append(
                f"Album {self.id} '{self.album_title}' violates cardinality 1 for releasedByLabel")
        if len(self.genre_ids) == 0:
            violations.append(
                f"Album {self.id} '{self.album_title}' violates minCardinality 1 for hasGenre")
        return violations


@dataclass
class RecordLabel:
    """
    Represents a record label with computed success metrics.
    Label relationships are ALL DERIVED from artist associations.
    """
    id: str
    label_name: str
    location: str = ""

    # INVERSE RELATIONSHIPS (computed from artists in PHASE 1)
    # inverse of artist.signedTo
    signed_artists: Set[str] = field(default_factory=set)

    # DERIVED RELATIONSHIPS (computed from artist relationships in PHASE 2)
    published_albums: Set[str] = field(
        default_factory=set)    # computed from artist albums

    # COMPUTED PROPERTIES (populated by reasoning rules)
    is_successful: bool = False
    success_rating: int = 0
    award_winning_artists: Set[str] = field(default_factory=set)


@dataclass
class Genre:
    """
    Represents a music genre with relationship properties.
    Genre relationships are MOSTLY DERIVED from songs and albums.
    """
    id: str
    genre_name: str
    description: str = ""

    # INVERSE RELATIONSHIPS (computed from songs and albums in PHASE 1)
    # inverse of song.hasGenre
    song_ids: Set[str] = field(default_factory=set)
    # inverse of album.hasGenre
    album_ids: Set[str] = field(default_factory=set)

    # COMPUTED PROPERTIES (populated by reasoning rules)
    related_genres: Set[str] = field(default_factory=set)
    artist_count: int = 0
    song_count: int = 0
    album_count: int = 0


@dataclass
class Award:
    """
    Represents a music industry award - connected only through songs.
    Award relationships are ALL DERIVED from songs.
    """
    id: str
    award_name: str
    year: int = 0
    awarding_body: str = ""

    # INVERSE RELATIONSHIPS (computed from songs in PHASE 1)
    # inverse of song.hasWonAward
    song_ids: Set[str] = field(default_factory=set)

    # DERIVED RELATIONSHIPS (computed from songs->artists in PHASE 2)
    # computed from songs->artists
    artist_ids: Set[str] = field(default_factory=set)


class MusicReasonerEngine:
    """
    Core reasoning engine for music industry ontology.

    CRITICAL DESIGN PRINCIPLE: TWO-PHASE RELATIONSHIP COMPUTATION

    PHASE 1: INVERSE RELATIONSHIPS (Direct mappings from CSV data)
    - song.artist_ids → artist.performed_song_ids
    - song.album_ids → album.song_ids  
    - song.genre_ids → genre.song_ids
    - song.award_ids → award.song_ids
    - artist.label_id → label.signed_artists
    - album.genre_ids → genre.album_ids

    PHASE 2: DERIVED RELATIONSHIPS (Computed from inverse relationships)
    - album.artist_ids (from album.song_ids + song.artist_ids)
    - artist.released_album_ids (from artist.performed_song_ids + song.album_ids)
    - award.artist_ids (from award.song_ids + song.artist_ids)
    - artist.won_award_ids (from artist.performed_song_ids + song.award_ids)
    - label.published_albums (from label.signed_artists + artist.released_album_ids)

    This ordering prevents dependency issues and ensures all data is available
    when derived relationships are computed.
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
            'relationships_parsed': 0,
            'inverse_relationships_established': 0,
            'derived_relationships_computed': 0,
            'rules_executed': 0,
            'inferences_made': 0,
            'cardinality_violations': 0,
            'processing_time': 0.0
        }

        # Cardinality violation tracking
        self.cardinality_violations: List[str] = []

    def load_csv_data(self, data_dir: str) -> None:
        """
        Load music industry data from CSV files based on actual structure:

        DATA LOADING PHASES:
        1. Load base entities (no relationships)
        2. Load songs as central hub with embedded relationships  
        3. PHASE 1: Establish all inverse relationships from songs
        4. PHASE 2: Compute all derived relationships
        5. Validate cardinality constraints

        Expected CSV structure:
        - songs.csv: Central hub with embedded lists (artistIDs, albumIDs, genreIDs, awardIDs)
        - albums.csv: Only genreIDs is a list
        - awards.csv: No relationship columns
        - artists.csv: Simple structure with labelID
        - record_labels.csv, genres.csv: Simple structures
        """
        data_path = Path(data_dir)
        logger.info(f"Loading CSV data from {data_path}")

        try:
            # Phase 1: Load base entities (no relationships yet)
            self._load_base_entities(data_path)

            # Phase 2: Load songs with all their embedded relationships (central hub)
            self._load_songs_as_central_hub(data_path)

            # Phase 3: CRITICAL - Establish inverse relationships FIRST
            self._establish_inverse_relationships()

            # Phase 4: CRITICAL - Compute derived relationships SECOND
            self._compute_derived_relationships()

            # Phase 5: Validate cardinality constraints
            self._validate_all_cardinality_constraints()

            # Phase 6: Generate comprehensive diagnostics
            self._generate_loading_diagnostics()

            logger.info(
                f"Successfully loaded {self.stats['entities_loaded']} entities")
            logger.info(
                f"Parsed {self.stats['relationships_parsed']} direct relationships")
            logger.info(
                f"Established {self.stats['inverse_relationships_established']} inverse relationships")
            logger.info(
                f"Computed {self.stats['derived_relationships_computed']} derived relationships")

        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            raise

    def _load_base_entities(self, data_path: Path) -> None:
        """
        Load base entities without relationships first.
        This establishes the entity catalog before relationship computation.
        """
        logger.info("Loading base entities...")

        self._load_artists_base(data_path)
        self._load_albums_base(data_path)
        self._load_record_labels_base(data_path)
        self._load_genres_base(data_path)
        self._load_awards_base(data_path)

    def _load_artists_base(self, data_path: Path) -> None:
        """Load artists with basic properties including labelID."""
        artists_file = data_path / "artists.csv"
        if not artists_file.exists():
            logger.warning(f"Artists file not found: {artists_file}")
            return

        try:
            df = pd.read_csv(artists_file)
            logger.info(f"Loading {len(df)} artists from {artists_file}")
            logger.info(f"Artists CSV columns: {list(df.columns)}")

            # Normalize ID columns
            df['id'] = df['id'].apply(normalize_id)
            if 'labelID' in df.columns:
                df['labelID'] = df['labelID'].apply(
                    lambda x: normalize_id(x) if pd.notna(x) else "")
            elif 'label_id' in df.columns:
                df['label_id'] = df['label_id'].apply(
                    lambda x: normalize_id(x) if pd.notna(x) else "")

            for _, row in df.iterrows():
                artist_id = normalize_id(row['id'])
                if not artist_id:
                    continue

                # Get label ID from either column name variant
                label_id = ""
                if 'labelID' in row and pd.notna(row['labelID']):
                    label_id = normalize_id(row['labelID'])
                elif 'label_id' in row and pd.notna(row['label_id']):
                    label_id = normalize_id(row['label_id'])

                artist = Artist(
                    id=artist_id,
                    name=str(row['name']) if pd.notna(
                        row['name']) else f"Artist_{artist_id}",
                    birth_date=safe_date(row.get('birth_date')),
                    nationality=str(row['nationality']) if pd.notna(
                        row.get('nationality')) else "",
                    label_id=label_id
                )

                self.artists[artist_id] = artist
                self.stats['entities_loaded'] += 1

            logger.info(f"Loaded {len(self.artists)} artists")

        except Exception as e:
            logger.error(f"Error loading artists: {e}")
            raise

    def _load_albums_base(self, data_path: Path) -> None:
        """Load albums with genreIDs list only."""
        albums_file = data_path / "albums.csv"
        if not albums_file.exists():
            logger.warning(f"Albums file not found: {albums_file}")
            return

        try:
            df = pd.read_csv(albums_file)
            logger.info(f"Loading {len(df)} albums from {albums_file}")
            logger.info(f"Albums CSV columns: {list(df.columns)}")

            # Normalize ID column
            df['id'] = df['id'].apply(normalize_id)

            for _, row in df.iterrows():
                album_id = normalize_id(row['id'])
                if not album_id:
                    continue

                # Create album with basic properties
                album = Album(
                    id=album_id,
                    album_title=str(row['album_title']) if pd.notna(
                        row['album_title']) else f"Album_{album_id}",
                    release_year=safe_int(row.get('releaseYear', 0))
                )

                # Parse genreIDs list (only list column in albums.csv)
                if 'genreIDs' in row and pd.notna(row['genreIDs']):
                    album.genre_ids = parse_id_list(row['genreIDs'])
                    self.stats['relationships_parsed'] += len(album.genre_ids)
                    logger.debug(f"Album {album_id} genres: {album.genre_ids}")

                self.albums[album_id] = album
                self.stats['entities_loaded'] += 1

            logger.info(f"Loaded {len(self.albums)} albums")

        except Exception as e:
            logger.error(f"Error loading albums: {e}")
            raise

    def _load_record_labels_base(self, data_path: Path) -> None:
        """Load record labels with basic properties."""
        labels_file = data_path / "record_labels.csv"
        if not labels_file.exists():
            logger.warning(f"Record labels file not found: {labels_file}")
            return

        try:
            df = pd.read_csv(labels_file)
            logger.info(f"Loading {len(df)} record labels from {labels_file}")

            df['id'] = df['id'].apply(normalize_id)

            for _, row in df.iterrows():
                label_id = normalize_id(row['id'])
                if not label_id:
                    continue

                label = RecordLabel(
                    id=label_id,
                    label_name=str(row['label_name']) if pd.notna(
                        row['label_name']) else f"Label_{label_id}",
                    location=str(row['location']) if pd.notna(
                        row.get('location')) else ""
                )

                self.record_labels[label_id] = label
                self.stats['entities_loaded'] += 1

            logger.info(f"Loaded {len(self.record_labels)} record labels")

        except Exception as e:
            logger.error(f"Error loading record labels: {e}")
            raise

    def _load_genres_base(self, data_path: Path) -> None:
        """Load genres with basic properties."""
        genres_file = data_path / "genres.csv"
        if not genres_file.exists():
            logger.warning(f"Genres file not found: {genres_file}")
            return

        try:
            df = pd.read_csv(genres_file)
            logger.info(f"Loading {len(df)} genres from {genres_file}")

            df['id'] = df['id'].apply(normalize_id)

            for _, row in df.iterrows():
                genre_id = normalize_id(row['id'])
                if not genre_id:
                    continue

                genre = Genre(
                    id=genre_id,
                    genre_name=str(row['genre_name']) if pd.notna(
                        row['genre_name']) else f"Genre_{genre_id}",
                    description=str(row['description']) if pd.notna(
                        row.get('description')) else ""
                )

                self.genres[genre_id] = genre
                self.stats['entities_loaded'] += 1

            logger.info(f"Loaded {len(self.genres)} genres")

        except Exception as e:
            logger.error(f"Error loading genres: {e}")
            raise

    def _load_awards_base(self, data_path: Path) -> None:
        """Load awards with basic properties only (no relationship columns)."""
        awards_file = data_path / "awards.csv"
        if not awards_file.exists():
            logger.warning(f"Awards file not found: {awards_file}")
            return

        try:
            df = pd.read_csv(awards_file)
            logger.info(f"Loading {len(df)} awards from {awards_file}")
            logger.info(f"Awards CSV columns: {list(df.columns)}")

            df['id'] = df['id'].apply(normalize_id)

            for _, row in df.iterrows():
                award_id = normalize_id(row['id'])
                if not award_id:
                    continue

                # Awards only have basic properties - no relationship columns
                award = Award(
                    id=award_id,
                    award_name=str(row['award_name']) if pd.notna(
                        row['award_name']) else f"Award_{award_id}",
                    year=safe_int(row.get('year', 0)),
                    awarding_body=str(row['awarding_body']) if pd.notna(
                        row.get('awarding_body')) else ""
                )

                self.awards[award_id] = award
                self.stats['entities_loaded'] += 1

            logger.info(f"Loaded {len(self.awards)} awards")

        except Exception as e:
            logger.error(f"Error loading awards: {e}")
            raise

    def _load_songs_as_central_hub(self, data_path: Path) -> None:
        """
        Load songs with all embedded relationships - the central connection hub.
        Songs contain the DIRECT relationships that drive all other entity connections.
        """
        songs_file = data_path / "songs.csv"
        if not songs_file.exists():
            logger.error(
                f"Songs file not found: {songs_file} - this is required as the central hub")
            raise FileNotFoundError(f"Songs file is required: {songs_file}")

        try:
            df = pd.read_csv(songs_file)
            logger.info(f"Loading {len(df)} songs from {songs_file}")
            logger.info(f"Songs CSV columns: {list(df.columns)}")

            # Normalize ID column
            df['id'] = df['id'].apply(normalize_id)

            for _, row in df.iterrows():
                song_id = normalize_id(row['id'])
                if not song_id:
                    continue

                # Create song with basic properties
                song = Song(
                    id=song_id,
                    title=str(row['title']) if pd.notna(
                        row['title']) else f"Song_{song_id}",
                    duration=safe_int(row.get('duration', 0)),
                    release_date=safe_date(row.get('release_date'))
                )

                # Parse all embedded relationship lists from songs.csv
                # These are the DIRECT relationships that will drive all inverse/derived relationships

                if 'artistIDs' in row and pd.notna(row['artistIDs']):
                    song.artist_ids = parse_id_list(row['artistIDs'])
                    self.stats['relationships_parsed'] += len(song.artist_ids)
                    logger.debug(f"Song {song_id} artists: {song.artist_ids}")

                if 'genreIDs' in row and pd.notna(row['genreIDs']):
                    song.genre_ids = parse_id_list(row['genreIDs'])
                    self.stats['relationships_parsed'] += len(song.genre_ids)
                    logger.debug(f"Song {song_id} genres: {song.genre_ids}")

                if 'albumIDs' in row and pd.notna(row['albumIDs']):
                    song.album_ids = parse_id_list(row['albumIDs'])
                    self.stats['relationships_parsed'] += len(song.album_ids)
                    logger.debug(f"Song {song_id} albums: {song.album_ids}")
                    if not song.album_ids:
                        logger.warning(
                            f"Song {song_id} has albumIDs column but parsed to empty set: '{row['albumIDs']}'")
                else:
                    logger.debug(
                        f"Song {song_id} has no albumIDs or albumIDs is NaN")

                if 'awardIDs' in row and pd.notna(row['awardIDs']):
                    song.award_ids = parse_id_list(row['awardIDs'])
                    self.stats['relationships_parsed'] += len(song.award_ids)
                    logger.debug(f"Song {song_id} awards: {song.award_ids}")

                self.songs[song_id] = song
                self.stats['entities_loaded'] += 1

            logger.info(
                f"Loaded {len(self.songs)} songs as central relationship hub")

        except Exception as e:
            logger.error(f"Error loading songs: {e}")
            raise

    def _establish_inverse_relationships(self) -> None:
        """
        PHASE 1: ESTABLISH ALL INVERSE RELATIONSHIPS FIRST

        CRITICAL: Inverse relationships are direct mappings from CSV data.
        These must be computed BEFORE any derived relationships to ensure
        all dependency data is available.

        Inverse relationships established:
        - song.artist_ids → artist.performed_song_ids
        - song.album_ids → album.song_ids  
        - song.genre_ids → genre.song_ids
        - song.award_ids → award.song_ids
        - artist.label_id → label.signed_artists
        - album.genre_ids → genre.album_ids
        """
        logger.info(
            "PHASE 1: Establishing ALL inverse relationships from direct CSV data...")

        inverse_count = 0

        # 1. SONG → ARTIST inverse relationships
        for song in self.songs.values():
            for artist_id in song.artist_ids:
                if artist_id in self.artists:
                    self.artists[artist_id].performed_song_ids.add(song.id)
                    inverse_count += 1
                else:
                    logger.warning(
                        f"Song {song.id} references unknown artist {artist_id}")

        # 2. SONG → GENRE inverse relationships
        for song in self.songs.values():
            for genre_id in song.genre_ids:
                if genre_id in self.genres:
                    self.genres[genre_id].song_ids.add(song.id)
                    inverse_count += 1
                else:
                    logger.warning(
                        f"Song {song.id} references unknown genre {genre_id}")

        # 3. SONG → ALBUM inverse relationships
        for song in self.songs.values():
            for album_id in song.album_ids:
                if album_id in self.albums:
                    self.albums[album_id].song_ids.add(song.id)
                    inverse_count += 1
                else:
                    logger.warning(
                        f"Song {song.id} references unknown album {album_id}")

        # 4. SONG → AWARD inverse relationships
        for song in self.songs.values():
            for award_id in song.award_ids:
                if award_id in self.awards:
                    self.awards[award_id].song_ids.add(song.id)
                    inverse_count += 1
                else:
                    logger.warning(
                        f"Song {song.id} references unknown award {award_id}")

        # 5. ARTIST → LABEL inverse relationships
        for artist in self.artists.values():
            if artist.label_id and artist.label_id in self.record_labels:
                self.record_labels[artist.label_id].signed_artists.add(
                    artist.id)
                inverse_count += 1
            elif artist.label_id:
                logger.warning(
                    f"Artist {artist.id} references unknown label {artist.label_id}")

        # 6. ALBUM → GENRE inverse relationships (from albums.csv genreIDs)
        for album in self.albums.values():
            for genre_id in album.genre_ids:
                if genre_id in self.genres:
                    self.genres[genre_id].album_ids.add(album.id)
                    inverse_count += 1
                else:
                    logger.warning(
                        f"Album {album.id} references unknown genre {genre_id}")

        self.stats['inverse_relationships_established'] = inverse_count
        logger.info(
            f"PHASE 1 COMPLETE: Established {inverse_count} inverse relationships")

        # TODO - Implement this inverse relationship...
        # 7. RECORD LABEL → ARTISTS inverse relationship (from artists.csv labelIDs)
        # sample code below:
        # for artist in self.artists.values():
        #     if artist.label_id and artist.label_id in self.record_labels:
        #         self.record_labels[id].signed_artists.add(artist.id)

    def _compute_derived_relationships(self) -> None:
        """
        PHASE 2: COMPUTE ALL DERIVED RELATIONSHIPS SECOND

        CRITICAL: Derived relationships are computed FROM inverse relationships.
        This phase can only run AFTER all inverse relationships are established
        to ensure all dependency data is available.

        Derived relationships computed:
        - album.artist_ids (from album.song_ids + song.artist_ids)
        - artist.released_album_ids (from artist.performed_song_ids + song.album_ids)
        - award.artist_ids (from award.song_ids + song.artist_ids)
        - artist.won_award_ids (from artist.performed_song_ids + song.award_ids)
        - label.published_albums (from label.signed_artists + artist.released_album_ids)
        - album.label_id (from album.artist_ids + artist.label_id)
        """
        logger.info(
            "PHASE 2: Computing ALL derived relationships from inverse relationships...")

        derived_count = 0

        # 1. DERIVE album.artist_ids from album.song_ids + song.artist_ids
        logger.info("Computing album → artist derived relationships...")
        albums_with_artists = 0
        for album in self.albums.values():
            initial_artist_count = len(album.artist_ids)
            for song_id in album.song_ids:
                if song_id in self.songs:
                    song = self.songs[song_id]
                    album.artist_ids.update(song.artist_ids)
                    derived_count += len(song.artist_ids)

            if len(album.artist_ids) > initial_artist_count:
                albums_with_artists += 1
            elif len(album.song_ids) > 0 and len(album.artist_ids) == 0:
                logger.error(
                    f"Album {album.id} has {len(album.song_ids)} songs but no artists derived")
                for song_id in album.song_ids:
                    song = self.songs[song_id]
                    logger.error(
                        f"  Song {song_id} has artists: {song.artist_ids}")

        logger.info(f"Derived artists for {albums_with_artists} albums")

        # 2. DERIVE artist.released_album_ids from artist.performed_song_ids + song.album_ids
        logger.info("Computing artist → album derived relationships...")
        for artist in self.artists.values():
            for song_id in artist.performed_song_ids:
                if song_id in self.songs:
                    song = self.songs[song_id]
                    artist.released_album_ids.update(song.album_ids)
                    derived_count += len(song.album_ids)

        # 3. DERIVE award.artist_ids from award.song_ids + song.artist_ids
        logger.info("Computing award → artist derived relationships...")
        for award in self.awards.values():
            for song_id in award.song_ids:
                if song_id in self.songs:
                    song = self.songs[song_id]
                    award.artist_ids.update(song.artist_ids)
                    derived_count += len(song.artist_ids)

        # 4. DERIVE artist.won_award_ids from artist.performed_song_ids + song.award_ids
        logger.info("Computing artist → award derived relationships...")
        for artist in self.artists.values():
            for song_id in artist.performed_song_ids:
                if song_id in self.songs:
                    song = self.songs[song_id]
                    artist.won_award_ids.update(song.award_ids)
                    derived_count += len(song.award_ids)

        # 5. DERIVE label.published_albums from label.signed_artists + artist.released_album_ids
        logger.info("Computing label → album derived relationships...")
        for label in self.record_labels.values():
            for artist_id in label.signed_artists:
                if artist_id in self.artists:
                    artist = self.artists[artist_id]
                    label.published_albums.update(artist.released_album_ids)
                    derived_count += len(artist.released_album_ids)

        # 6. DERIVE album.label_id from album.artist_ids + artist.label_id
        logger.info("Computing album → label derived relationships...")
        for album in self.albums.values():
            if not album.label_id:  # Only if not already set
                label_counts = Counter()
                for artist_id in album.artist_ids:
                    if artist_id in self.artists:
                        artist = self.artists[artist_id]
                        if artist.label_id:
                            label_counts[artist.label_id] += 1

                # Set most common label as album label
                if label_counts:
                    most_common_label = label_counts.most_common(1)[0][0]
                    album.label_id = most_common_label
                    derived_count += 1

        self.stats['derived_relationships_computed'] = derived_count
        logger.info(
            f"PHASE 2 COMPLETE: Computed {derived_count} derived relationships")

        # Diagnostic logging for relationship chain verification
        logger.info("Relationship chain diagnostics:")
        logger.info(
            f"  Albums with songs: {sum(1 for a in self.albums.values() if a.song_ids)}/{len(self.albums)}")
        logger.info(
            f"  Albums with artists: {sum(1 for a in self.albums.values() if a.artist_ids)}/{len(self.albums)}")
        logger.info(
            f"  Artists with songs: {sum(1 for a in self.artists.values() if a.performed_song_ids)}/{len(self.artists)}")
        logger.info(
            f"  Artists with albums: {sum(1 for a in self.artists.values() if a.released_album_ids)}/{len(self.artists)}")

    def _validate_all_cardinality_constraints(self) -> None:
        """Validate cardinality constraints for all entities."""
        logger.info("Validating cardinality constraints...")

        total_violations = 0

        # Validate songs
        for song in self.songs.values():
            violations = song.validate_cardinality()
            self.cardinality_violations.extend(violations)
            total_violations += len(violations)

        # Validate artists
        for artist in self.artists.values():
            violations = artist.validate_cardinality()
            self.cardinality_violations.extend(violations)
            total_violations += len(violations)

        # Validate albums
        for album in self.albums.values():
            violations = album.validate_cardinality()
            self.cardinality_violations.extend(violations)
            total_violations += len(violations)

        self.stats['cardinality_violations'] = total_violations

        if total_violations > 0:
            logger.warning(
                f"Found {total_violations} cardinality constraint violations")
            for violation in self.cardinality_violations[:10]:  # Log first 10
                logger.warning(f"  {violation}")
            if len(self.cardinality_violations) > 10:
                logger.warning(
                    f"  ... and {len(self.cardinality_violations) - 10} more violations")
        else:
            logger.info("All cardinality constraints satisfied")

    def _generate_loading_diagnostics(self) -> None:
        """Generate comprehensive diagnostics about the loading process."""
        logger.info("Generating loading diagnostics...")

        # Count entities with relationships
        songs_with_artists = sum(
            1 for song in self.songs.values() if song.artist_ids)
        songs_with_genres = sum(
            1 for song in self.songs.values() if song.genre_ids)
        songs_with_albums = sum(
            1 for song in self.songs.values() if song.album_ids)
        songs_with_awards = sum(
            1 for song in self.songs.values() if song.award_ids)
        albums_with_artists = sum(
            1 for album in self.albums.values() if album.artist_ids)
        albums_with_genres = sum(
            1 for album in self.albums.values() if album.genre_ids)
        artists_with_labels = sum(
            1 for artist in self.artists.values() if artist.label_id)
        artists_with_songs = sum(
            1 for artist in self.artists.values() if artist.performed_song_ids)

        logger.info(f"Final relationship diagnostics:")
        logger.info(
            f"  Songs with artists: {songs_with_artists}/{len(self.songs)}")
        logger.info(
            f"  Songs with genres: {songs_with_genres}/{len(self.songs)}")
        logger.info(
            f"  Songs with albums: {songs_with_albums}/{len(self.songs)}")
        logger.info(
            f"  Songs with awards: {songs_with_awards}/{len(self.songs)}")
        logger.info(
            f"  Albums with artists (computed): {albums_with_artists}/{len(self.albums)}")
        logger.info(
            f"  Albums with genres: {albums_with_genres}/{len(self.albums)}")
        logger.info(
            f"  Artists with labels: {artists_with_labels}/{len(self.artists)}")
        logger.info(
            f"  Artists with songs: {artists_with_songs}/{len(self.artists)}")

        # Sample some entities for verification
        if self.songs:
            sample_song = next(iter(self.songs.values()))
            logger.info(
                f"Sample song {sample_song.id}: {len(sample_song.artist_ids)} artists, {len(sample_song.genre_ids)} genres, {len(sample_song.album_ids)} albums")
            if sample_song.artist_ids:
                logger.info(
                    f"  Artists: {list(sample_song.artist_ids)[:3]}...")
            if sample_song.genre_ids:
                logger.info(f"  Genres: {list(sample_song.genre_ids)[:3]}...")

        if self.artists:
            sample_artist = next(iter(self.artists.values()))
            logger.info(
                f"Sample artist {sample_artist.id}: {len(sample_artist.performed_song_ids)} songs, {len(sample_artist.released_album_ids)} albums")

        if self.albums:
            sample_album = next(iter(self.albums.values()))
            logger.info(
                f"Sample album {sample_album.id}: {len(sample_album.song_ids)} songs, {len(sample_album.artist_ids)} artists")

    def apply_reasoning_rules(self) -> None:
        """
        Apply all N3 reasoning rules in logical sequence with proper dependency management.
        """
        start_time = datetime.now()
        logger.info("Starting reasoning rule application...")

        try:
            # Pre-reasoning validation
            if not self._validate_minimum_data():
                logger.error(
                    "Insufficient data for reasoning. Aborting rule application.")
                return

            # Category 1: Basic classification and detection rules
            logger.info("Applying Category 1: Basic classification rules...")
            self._rule_01_collaboration_detection()
            self._rule_07_contribution_inference()

            # Category 2: Inheritance and propagation rules
            logger.info("Applying Category 2: Inheritance rules...")
            self._rule_02_genre_inheritance()

            # Category 3: Success and classification rules
            logger.info("Applying Category 3: Success classification rules...")
            self._rule_03_label_success_inference()
            self._rule_04_artist_establishment()

            # Category 4: Network and influence rules
            logger.info("Applying Category 4: Network analysis rules...")
            self._rule_06_genre_based_influence()
            self._rule_05_transitivity_influence()

            # Category 5: Quantitative analysis rules
            logger.info("Applying Category 5: Quantitative analysis rules...")
            self._rule_08_collaboration_strength()
            self._rule_09_popularity_score()
            self._rule_10_label_success_rating()

            # Category 6: String and temporal analysis
            logger.info("Applying Category 6: Analysis rules...")
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

    def _validate_minimum_data(self) -> bool:
        """Validate that we have minimum data required for reasoning."""
        if len(self.songs) == 0:
            logger.error("No songs loaded - cannot perform reasoning")
            return False

        if len(self.artists) == 0:
            logger.error("No artists loaded - cannot perform reasoning")
            return False

        # Check if songs have artists
        songs_with_artists = sum(
            1 for song in self.songs.values() if song.artist_ids)
        if songs_with_artists == 0:
            logger.error(
                "No songs have associated artists - check artistIDs column parsing")
            return False

        logger.info(
            f"Data validation passed: {len(self.songs)} songs, {len(self.artists)} artists, {songs_with_artists} songs with artists")
        return True

    # ===== N3 REASONING RULES =====

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

                    # Update genre's album list (inverse relationship)
                    if genre_id in self.genres:
                        self.genres[genre_id].album_ids.add(album.id)

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
            for artist_id in label.signed_artists:
                if artist_id in self.artists:
                    artist = self.artists[artist_id]
                    if len(artist.won_award_ids) > 0:
                        award_winning_artists.add(artist_id)

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
            album_count = len(artist.released_album_ids)
            artist.album_count = album_count

            # Count awards won by this artist
            award_count = len(artist.won_award_ids)
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
                    for song_id in artist1.performed_song_ids:
                        if song_id in self.songs:
                            artist1_genres.update(
                                self.songs[song_id].genre_ids)

                    for song_id in artist2.performed_song_ids:
                        if song_id in self.songs:
                            artist2_genres.update(
                                self.songs[song_id].genre_ids)

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
            # Artists are contributors (computed from songs)
            for artist_id in album.artist_ids:
                if artist_id in self.artists:
                    album.contributors.add(artist_id)
                    contributions_found += 1

            # Label is contributor (if album has derived label)
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
            'relationship_counts': {
                'song_artist_pairs': sum(len(song.artist_ids) for song in self.songs.values()),
                'song_genre_pairs': sum(len(song.genre_ids) for song in self.songs.values()),
                'song_album_pairs': sum(len(song.album_ids) for song in self.songs.values()),
                'song_award_pairs': sum(len(song.award_ids) for song in self.songs.values()),
                'album_genre_pairs': sum(len(album.genre_ids) for album in self.albums.values()),
                'artist_label_pairs': sum(1 for artist in self.artists.values() if artist.label_id),
                'total_relationships_parsed': self.stats['relationships_parsed'],
                'inverse_relationships_established': self.stats['inverse_relationships_established'],
                'derived_relationships_computed': self.stats['derived_relationships_computed']
            },
            'reasoning_results': {
                'collaborative_songs': len(self.collaborative_songs),
                'successful_labels': len(self.successful_labels),
                'established_artists': len(self.established_artists),
                'total_collaborations': sum(len(partners) for partners in self.collaboration_network.values()) // 2,
                'total_influences': sum(len(influences) for influences in self.influence_network.values()),
                'genre_similarities': sum(len(similar) for similar in self.genre_similarity_map.values())
            },
            'cardinality_validation': {
                'total_violations': self.stats['cardinality_violations'],
                # Show first 20
                'violations_list': self.cardinality_violations[:20]
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
        songs_with_albums = sum(
            1 for song in self.songs.values() if song.album_ids)
        songs_with_duration = sum(
            1 for song in self.songs.values() if song.duration > 0)

        metrics['song_completeness'] = {
            'with_artists': f"{songs_with_artists}/{len(self.songs)}",
            'with_genres': f"{songs_with_genres}/{len(self.songs)}",
            'with_albums': f"{songs_with_albums}/{len(self.songs)}",
            'with_duration': f"{songs_with_duration}/{len(self.songs)}"
        }

        # Artist quality metrics
        artists_with_labels = sum(
            1 for artist in self.artists.values() if artist.label_id)
        artists_with_birth_dates = sum(
            1 for artist in self.artists.values() if artist.birth_date)
        artists_with_songs = sum(
            1 for artist in self.artists.values() if artist.performed_song_ids)
        artists_with_albums = sum(
            1 for artist in self.artists.values() if artist.released_album_ids)

        metrics['artist_completeness'] = {
            'with_labels': f"{artists_with_labels}/{len(self.artists)}",
            'with_birth_dates': f"{artists_with_birth_dates}/{len(self.artists)}",
            'with_songs': f"{artists_with_songs}/{len(self.artists)}",
            'with_albums': f"{artists_with_albums}/{len(self.artists)}"
        }

        # Album quality metrics
        albums_with_artists = sum(
            1 for album in self.albums.values() if album.artist_ids)
        albums_with_songs = sum(
            1 for album in self.albums.values() if album.song_ids)
        albums_with_genres = sum(
            1 for album in self.albums.values() if album.genre_ids)
        albums_with_labels = sum(
            1 for album in self.albums.values() if album.label_id)

        metrics['album_completeness'] = {
            'with_artists': f"{albums_with_artists}/{len(self.albums)}",
            'with_songs': f"{albums_with_songs}/{len(self.albums)}",
            'with_genres': f"{albums_with_genres}/{len(self.albums)}",
            'with_labels': f"{albums_with_labels}/{len(self.albums)}"
        }

        # Relationship density
        total_possible_collaborations = len(
            self.artists) * (len(self.artists) - 1) // 2
        actual_collaborations = sum(
            len(partners) for partners in self.collaboration_network.values()) // 2

        if total_possible_collaborations > 0:
            collaboration_density = actual_collaborations / total_possible_collaborations
            metrics['collaboration_density'] = f"{collaboration_density:.4f}"
        else:
            metrics['collaboration_density'] = "0.0000"

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
