import 'dart:convert';
import 'package:flutter/services.dart';
import '../models/ranking.dart';
import '../models/fighter.dart';
import '../models/fight.dart';
import 'dart:math' as math;

class UFCDataService {
  static final UFCDataService _instance = UFCDataService._internal();
  factory UFCDataService() => _instance;
  UFCDataService._internal();

  List<Ranking> _rankings = [];
  List<Fighter> _fighters = [];
  Map<String, List<Ranking>> _rankingsByDivision = {};
  Map<String, Fighter> _fightersById = {};
  bool _isLoaded = false;
  List<Fight> _upcomingFights = [];
  List<Fight> get upcomingFights => List.unmodifiable(_upcomingFights);

  bool get isLoaded => _isLoaded;

  Future<void> loadData() async {
    if (_isLoaded) return;

    try {
      final String jsonString = await rootBundle.loadString('assets/data/ufc_data.json');
      final Map<String, dynamic> jsonData = json.decode(jsonString);
      
      _rankings = [];
      _fighters = [];
      _rankingsByDivision = {};
      _fightersById = {};

      // Load rankings with better error handling
      if (jsonData['rankings'] != null) {
        for (var rankingJson in jsonData['rankings']) {
          try {
            final ranking = Ranking.fromJson(rankingJson);
            _rankings.add(ranking);
            
            // Group by division
            if (!_rankingsByDivision.containsKey(ranking.division)) {
              _rankingsByDivision[ranking.division] = [];
            }
            _rankingsByDivision[ranking.division]!.add(ranking);
          } catch (e) {
            print('❌ Error parsing ranking: $e');
            print('   JSON: $rankingJson');
          }
        }

        // Sort each division by rank (champions first, then by rank)
        _rankingsByDivision.forEach((division, rankings) {
          rankings.sort((a, b) {
            if (a.isChampion && !b.isChampion) return -1;
            if (!a.isChampion && b.isChampion) return 1;
            return a.rank.compareTo(b.rank);
          });
        });
      }

      // Load fighters from rankings (they have embedded fighter profiles)
      for (var rankingJson in jsonData['rankings']) {
        try {
          // Check if ranking has a fighter profile
          if (rankingJson['has_detailed_profile'] == true && rankingJson['fighter_profile'] != null) {
            final fighterProfile = rankingJson['fighter_profile'];
            // Create fighter from the embedded profile
            final fighter = Fighter.fromJson(fighterProfile);
            _fighters.add(fighter);
            _fightersById[fighter.id] = fighter;
            
            // Also store by fighter URL for easier lookup
            if (fighterProfile['fighter_url'] != null) {
              _fightersById[fighterProfile['fighter_url']] = fighter;
            }
            
            // Update the ranking record with the fighter profile record if available
            if (fighterProfile['record'] != null) {
              bool foundMatch = false;
              
              // Try to match by fighterUrl first, then by normalized name
              for (var ranking in _rankings) {
                bool match = false;
                
                // Match by fighterUrl if available (most reliable)
                if (ranking.fighterUrl != null && fighterProfile['fighter_url'] != null) {
                  match = ranking.fighterUrl == fighterProfile['fighter_url'];
                }
                
                // Fallback: match by normalized name (case-insensitive, accent-insensitive)
                if (!match) {
                  String normalize(String s) => s.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]'), '');
                  match = normalize(ranking.fighterName) == normalize(fighter.name);
                }
                
                // Additional fallback: try partial name matching for edge cases
                if (!match) {
                  String normalizePartial(String s) => s.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]'), '');
                  String rankingNormalized = normalizePartial(ranking.fighterName);
                  String fighterNormalized = normalizePartial(fighter.name);
                  
                  // Check if one name contains the other (for cases like "Merab Dvalishvili" vs "Merab Dvalishvelli")
                  match = rankingNormalized.contains(fighterNormalized) || 
                         fighterNormalized.contains(rankingNormalized) ||
                         // Check for common variations
                         rankingNormalized.replaceAll('velli', 'vili') == fighterNormalized.replaceAll('velli', 'vili') ||
                         rankingNormalized.replaceAll('vili', 'velli') == fighterNormalized.replaceAll('vili', 'velli');
                }
                
                if (match) {
                  foundMatch = true;
                  // Create a new ranking with the updated record
                  final updatedRanking = Ranking(
                    id: ranking.id,
                    fighterName: ranking.fighterName,
                    division: ranking.division,
                    rank: ranking.rank,
                    record: fighter.record, // Use fighter's real record
                    rankChange: ranking.rankChange,
                    fighterUrl: ranking.fighterUrl,
                    isChampion: ranking.isChampion,
                    fighterId: ranking.fighterId,
                  );
                  
                  // Replace the ranking in the list
                  final index = _rankings.indexOf(ranking);
                  if (index != -1) {
                    _rankings[index] = updatedRanking;
                  }
                  
                  // Update in division groups
                  if (_rankingsByDivision.containsKey(ranking.division)) {
                    final divIndex = _rankingsByDivision[ranking.division]!.indexOf(ranking);
                    if (divIndex != -1) {
                      _rankingsByDivision[ranking.division]![divIndex] = updatedRanking;
                    }
                  }
                  
                  // Debug log for successful matches
                  print('✅ Updated record for ${ranking.fighterName}: ${fighter.record.displayString}');
                  break;
                }
              }
              
              // Log unmatched fighters for debugging
              if (!foundMatch) {
                print('⚠️ No match found for fighter: ${fighter.name} (${fighter.record.displayString})');
                print('   Looking for ranking with name similar to: ${fighter.name}');
                // Show potential matches for debugging
                for (var ranking in _rankings) {
                  if (ranking.fighterName.toLowerCase().contains(fighter.name.toLowerCase().split(' ').first) ||
                      fighter.name.toLowerCase().contains(ranking.fighterName.toLowerCase().split(' ').first)) {
                    print('   Potential match: ${ranking.fighterName} (URL: ${ranking.fighterUrl})');
                  }
                }
              }
            }
          }
        } catch (e) {
          print('❌ Error parsing fighter from ranking: $e');
          print('   JSON: $rankingJson');
        }
      }

      _isLoaded = true;
      print('✅ Loaded ${_rankings.length} rankings and ${_fighters.length} fighters');
      
      // Final pass: handle any remaining unmatched fighters
      _handleUnmatchedFighters();
      
      // Print some sample data for verification
      if (_rankings.isNotEmpty) {
        final sampleRanking = _rankings.first;
        print('📊 Sample ranking: ${sampleRanking.fighterName} - ${sampleRanking.record.wins}W-${sampleRanking.record.losses}L-${sampleRanking.record.draws}D');
      }
      
    } catch (e) {
      print('❌ Error loading UFC data: $e');
      _isLoaded = false;
    }
  }

  List<Ranking> getAllRankings() => List.from(_rankings);

  List<Fighter> getAllFighters() => List.from(_fighters);

  List<String> getDivisions() => _rankingsByDivision.keys.toList()..sort();

  List<Ranking> getRankingsForDivision(String division) {
    return _rankingsByDivision[division] ?? [];
  }

  Ranking? getChampionForDivision(String division) {
    final rankings = getRankingsForDivision(division);
    return rankings.firstWhere(
      (r) => r.isChampion,
      orElse: () => Ranking(
        id: '',
        fighterName: 'No Champion',
        division: division,
        rank: 0,
        record: Record(wins: 0, losses: 0, draws: 0),
      ),
    );
  }

  List<Ranking> getRankedFightersForDivision(String division) {
    return getRankingsForDivision(division).where((r) => r.isRanked).toList();
  }

  Fighter? getFighterById(String id) => _fightersById[id];

  Fighter? getFighterByName(String name) {
    try {
      return _fighters.firstWhere(
        (fighter) => fighter.name.toLowerCase() == name.toLowerCase(),
      );
    } catch (e) {
      return null;
    }
  }

  Fighter? getFighterByRanking(Ranking ranking) {
    // Try to get fighter by URL first, then by ID, then by name
    if (ranking.fighterUrl != null) {
      final fighter = _fightersById[ranking.fighterUrl];
      if (fighter != null) return fighter;
    }
    
    if (ranking.fighterId != null) {
      final fighter = getFighterById(ranking.fighterId!);
      if (fighter != null) return fighter;
    }
    
    return getFighterByName(ranking.fighterName);
  }

  List<Fighter> getFightersByDivision(String division) {
    return _fighters.where((fighter) => fighter.division == division).toList();
  }

  List<Fighter> searchFighters(String query) {
    if (query.isEmpty) return [];
    
    return _fighters.where((fighter) =>
        fighter.name.toLowerCase().contains(query.toLowerCase()) ||
        fighter.division.toLowerCase().contains(query.toLowerCase()) ||
        (fighter.fightingStyle?.toLowerCase().contains(query.toLowerCase()) ?? false)
    ).toList();
  }

  Map<String, dynamic> getDivisionStats(String division) {
    final rankings = getRankingsForDivision(division);
    final champion = getChampionForDivision(division);
    final rankedFighters = getRankedFightersForDivision(division);
    
    return {
      'division': division,
      'champion': champion,
      'ranked_fighters': rankedFighters,
      'total_fighters': rankings.length,
      'has_champion': champion != null && champion.fighterName != 'No Champion',
    };
  }

  List<Map<String, dynamic>> getTopFighters({int limit = 10}) {
    final topRankings = _rankings
        .where((r) => r.rank <= limit && r.rank > 0)
        .take(limit)
        .toList()
      ..sort((a, b) => a.rank.compareTo(b.rank));

    return topRankings.map((ranking) {
      final fighter = getFighterByRanking(ranking);
      return {
        'ranking': ranking,
        'fighter': fighter,
        'has_profile': fighter != null,
      };
    }).toList();
  }

  void clearData() {
    _rankings.clear();
    _fighters.clear();
    _rankingsByDivision.clear();
    _fightersById.clear();
    _isLoaded = false;
  }

  Future<void> loadUpcomingFights() async {
    // TODO: Implement real scraping and loading of upcoming fights
    _upcomingFights = [];
  }

  void _handleUnmatchedFighters() {
    // Find rankings that still have 0-0-0 records but should have fighter profiles
    final unmatchedRankings = _rankings.where((ranking) => 
      ranking.record.wins == 0 && ranking.record.losses == 0 && ranking.record.draws == 0
    ).toList();
    
    if (unmatchedRankings.isEmpty) {
      print('🎉 All fighter records updated successfully!');
      return;
    }
    
    print('🔍 Found ${unmatchedRankings.length} rankings with 0-0-0 records, attempting final matching...');
    
    // Try to match remaining fighters using more flexible criteria
    for (var ranking in unmatchedRankings) {
      Fighter? bestMatch;
      double bestScore = 0.0;
      
      for (var fighter in _fighters) {
        double score = _calculateNameSimilarity(ranking.fighterName, fighter.name);
        if (score > bestScore && score > 0.7) { // 70% similarity threshold
          bestScore = score;
          bestMatch = fighter;
        }
      }
      
      if (bestMatch != null) {
        // Update the ranking with the matched fighter's record
        final updatedRanking = Ranking(
          id: ranking.id,
          fighterName: ranking.fighterName,
          division: ranking.division,
          rank: ranking.rank,
          record: bestMatch.record,
          rankChange: ranking.rankChange,
          fighterUrl: ranking.fighterUrl,
          isChampion: ranking.isChampion,
          fighterId: ranking.fighterId,
        );
        
        // Replace in lists
        final index = _rankings.indexOf(ranking);
        if (index != -1) _rankings[index] = updatedRanking;
        
        if (_rankingsByDivision.containsKey(ranking.division)) {
          final divIndex = _rankingsByDivision[ranking.division]!.indexOf(ranking);
          if (divIndex != -1) _rankingsByDivision[ranking.division]![divIndex] = updatedRanking;
        }
        
        print('🔧 Final match: ${ranking.fighterName} -> ${bestMatch.name} (${bestMatch.record.displayString}) [Score: ${(bestScore * 100).toStringAsFixed(1)}%]');
      } else {
        print('❌ No match found for: ${ranking.fighterName}');
      }
    }
  }
  
  double _calculateNameSimilarity(String name1, String name2) {
    // Simple similarity calculation based on common substrings
    String normalize(String s) => s.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]'), '');
    String n1 = normalize(name1);
    String n2 = normalize(name2);
    
    if (n1 == n2) return 1.0;
    
    // Check for common words
    List<String> words1 = n1.split(' ');
    List<String> words2 = n2.split(' ');
    
    int commonWords = 0;
    for (String word1 in words1) {
      for (String word2 in words2) {
        if (word1 == word2 && word1.length > 2) {
          commonWords++;
        }
      }
    }
    
    if (commonWords > 0) {
      return commonWords / math.max(words1.length, words2.length);
    }
    
    // Check for substring matches
    if (n1.contains(n2) || n2.contains(n1)) {
      return 0.8;
    }
    
    return 0.0;
  }
} 