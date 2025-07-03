# MovieLens N3 Ontology Reasoning Report
*Generated: 2025-07-03 18:52:50*

## Executive Summary

This report presents the results of applying 24 N3 reasoning rules to the MovieLens dataset, containing 9,742 movies, 610 users, and 100,836 ratings.

---

## Reasoning Statistics

### Movie Quality Distribution

| Quality Tier | Count | Percentage |
|--------------|-------|------------|
| Good | 809 | 8.3% |
| Unclassified | 5,072 | 52.1% |
| Poor | 249 | 2.6% |
| Excellent | 148 | 1.5% |
| Insufficient Data | 3,464 | 35.6% |

### Movie Era Distribution

| Era | Count |
|-----|-------|
| Classic | 1,479 |
| Unclassified | 8,263 |

### User Behavior Analysis

| Behavior Type | Count |
|---------------|-------|
| Unclassified | 443 |
| Generous | 138 |
| Critical | 29 |

### Recommendation Engine Performance

- **Total Recommendations Generated**: 556
- **Users with Recommendations**: 104
- **Average Recommendations per User**: 5.3

---

## Genre Analysis

### Top Genres by Total Ratings

| Rank | Genre | Movies | Total Ratings | Avg Rating | Popularity Level |
|------|-------|--------|---------------|------------|------------------|
| 1 | Drama | 4349 | 41,928 | 3.66 | HIGH |
| 2 | Comedy | 3753 | 39,053 | 3.38 | HIGH |
| 3 | Action | 1828 | 30,635 | 3.45 | HIGH |
| 4 | Thriller | 1889 | 26,452 | 3.49 | HIGH |
| 5 | Adventure | 1262 | 24,161 | 3.51 | HIGH |
| 6 | Romance | 1591 | 18,124 | 3.51 | MEDIUM |
| 7 | Sci-Fi | 980 | 17,243 | 3.46 | MEDIUM |
| 8 | Crime | 1196 | 16,681 | 3.66 | MEDIUM |
| 9 | Fantasy | 778 | 11,834 | 3.49 | MEDIUM |
| 10 | Children | 664 | 9,208 | 3.41 | MEDIUM |

### Mainstream Genres

| Genre | Total Ratings | Movies | Market Appeal |
|-------|---------------|--------|---------------|
| Drama | 41,928 | 4349 | Mainstream |
| Comedy | 39,053 | 3753 | Mainstream |
| Action | 30,635 | 1828 | Mainstream |
| Thriller | 26,452 | 1889 | Mainstream |
| Adventure | 24,161 | 1262 | Mainstream |

### Niche Genres

| Genre | Avg Rating | Movies | Market Appeal |
|-------|------------|--------|---------------|
| Documentary | 3.80 | 438 | Cult Following |
| Film-Noir | 3.92 | 85 | Cult Following |

---

## Hidden Gems Discovery

High-quality movies with limited exposure that deserve more attention:

| Rank | Movie Title | Rating | Vote Count |
|------|-------------|--------|------------|
| 1 | Secrets & Lies (1996) | 4.59 | 11 |
| 2 | Guess Who's Coming to Dinner (1967) | 4.55 | 11 |
| 3 | Paths of Glory (1957) | 4.54 | 12 |
| 4 | Streetcar Named Desire, A (1951) | 4.47 | 20 |
| 5 | Celebration, The (Festen) (1998) | 4.46 | 12 |
| 6 | Ran (1985) | 4.43 | 15 |
| 7 | His Girl Friday (1940) | 4.39 | 14 |
| 8 | All Quiet on the Western Front (1930) | 4.35 | 10 |
| 9 | Sunset Blvd. (a.k.a. Sunset Boulevard) (1950) | 4.33 | 27 |
| 10 | Hustler, The (1961) | 4.33 | 18 |
| 11 | Double Indemnity (1944) | 4.32 | 17 |
| 12 | It Happened One Night (1934) | 4.32 | 14 |
| 13 | Philadelphia Story, The (1940) | 4.31 | 29 |
| 14 | Living in Oblivion (1995) | 4.31 | 13 |
| 15 | Fog of War: Eleven Lessons from the Life of Robert S. McNamara, The (2003) | 4.31 | 13 |

---

## User Segmentation Analysis

### Unclassified
**Users**: 340

**Top Preferred Genres**:
- Drama: 166 users
- Thriller: 153 users
- Adventure: 141 users
- Action: 137 users
- Comedy: 133 users

**Rating Behaviors**:
- Standard: 253 users
- Critical: 18 users
- Generous: 69 users

### Action Fans
**Users**: 97

**Top Preferred Genres**:
- Action: 97 users
- Adventure: 69 users
- Drama: 68 users
- Thriller: 61 users
- Comedy: 53 users

**Rating Behaviors**:
- Standard: 64 users
- Generous: 28 users
- Critical: 5 users

### Drama Enthusiasts
**Users**: 113

**Top Preferred Genres**:
- Drama: 113 users
- Romance: 44 users
- Comedy: 42 users
- Thriller: 34 users
- Adventure: 28 users

**Rating Behaviors**:
- Standard: 86 users
- Generous: 22 users
- Critical: 5 users

### Comedy Lovers
**Users**: 60

**Top Preferred Genres**:
- Comedy: 60 users
- Drama: 46 users
- Romance: 33 users
- Thriller: 28 users
- Action: 26 users

**Rating Behaviors**:
- Standard: 40 users
- Generous: 19 users
- Critical: 1 users

---

## Sample Personalized Recommendations

### User 77

| Movie | Reason | Details |
|-------|--------|---------|
| Braveheart (1995) | Genre bridge | Rating: 4.03 |
| Léon: The Professional (a.k.a. The Professional) (Léon) (1994) | Genre bridge | Rating: 4.02 |
| Blade Runner (1982) | Genre bridge | Rating: 4.10 |
| North by Northwest (1959) | Genre bridge | Rating: 4.18 |
| Princess Bride, The (1987) | Genre bridge | Rating: 4.23 |

### User 161

| Movie | Reason | Details |
|-------|--------|---------|
| Toy Story (1995) | Genre preference match | Rating: 3.92 |
| American President, The (1995) | Genre preference match | Rating: 3.67 |
| Four Rooms (1995) | Genre preference match | Rating: 3.70 |
| City of Lost Children, The (Cité des enfants perdus, La) (1995) | Genre preference match | Rating: 4.01 |
| Babe (1995) | Genre preference match | Rating: 3.65 |

---

## Business Insights

### Key Findings

- **Quality Distribution**: 1.5% of movies achieve 'Excellent' status
- **Genre Diversity**: 19 distinct genres identified in the dataset
- **Hidden Opportunities**: 410 underrated movies identified for promotion
- **User Engagement**: 104 users eligible for personalized recommendations

### Strategic Recommendations

- **Mainstream Focus**: Leverage 5 high-volume genres for broad market appeal
- **Niche Cultivation**: Develop 2 specialized genres for targeted audiences
- **Quality Enhancement**: Focus on elevating movies currently in 'Good' tier to 'Excellent'
- **Discovery Features**: Implement hidden gems recommendations to improve catalog utilization

---

## Technical Details

### Reasoning Rules Applied

This analysis applied 24 N3 reasoning rules across the following categories:

- **Movie Quality Classification** (Rules 1-4): Excellent, Good, Poor, Controversial
- **Genre Analysis** (Rules 5-6): Popular and Niche genre identification
- **Temporal Analysis** (Rules 7-8): Classic movies and Contemporary hits
- **User Preferences** (Rules 12-14): Genre preferences and reviewer behavior
- **Content Similarity** (Rules 15-16): Genre and quality-based similarity
- **Advanced Recommendations** (Rules 17-19): Cross-genre and hidden gems
- **Contextual Analysis** (Rules 20-21): Seasonal and viewing context
- **Business Intelligence** (Rules 22-24): Data quality and audience segmentation

### Data Processing Statistics

- **Movies Processed**: 9,742
- **Ratings Analyzed**: 100,836
- **Users Profiled**: 610
- **Genres Identified**: 20
- **Reasoning Outputs**: 9,742 classifications

---

*Report generated by MovieLens N3 Ontology Reasoner*